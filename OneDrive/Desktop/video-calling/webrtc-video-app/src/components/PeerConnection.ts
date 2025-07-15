// src/utils/PeerConnection.ts
import { v4 as uuidv4 } from 'uuid';
import { webrtcConfig } from '../utils/webrtcConfig';

export class PeerConnection {
  private peerConnection: RTCPeerConnection;
  private localStream: MediaStream | null = null;
  private remoteStreams: Map<string, MediaStream> = new Map();
  private onRemoteStreamUpdate: (streams: Map<string, MediaStream>) => void;
  private onError: (error: Error) => void;
  private ws: WebSocket | null = null;
  private peerId: string;
  private roomId: string;
  private targetPeerId: string | null = null; // Store targetPeerId for the session
  private isClosed: boolean = false;
  private isInitializing: boolean = false;

  constructor(
    roomId: string,
    onRemoteStreamUpdate: (streams: Map<string, MediaStream>) => void,
    onError: (error: Error) => void
  ) {
    this.peerId = Date.now().toString() + Math.random().toString(36).slice(2);
    this.roomId = roomId;
    this.peerConnection = new RTCPeerConnection(webrtcConfig);
    this.onRemoteStreamUpdate = onRemoteStreamUpdate;
    this.onError = onError;

    // Handle ICE candidates
    this.peerConnection.onicecandidate = (event) => {
      if (event.candidate && this.ws && !this.isClosed && this.targetPeerId) {
        console.log('Sending ICE candidate:', event.candidate);
        this.ws.send(JSON.stringify({
          type: 'ice-candidate',
          candidate: event.candidate,
          roomId: this.roomId,
          peerId: this.peerId,
          targetPeerId: this.targetPeerId,
        }));
      } else {
        console.warn('Cannot send ICE candidate: Missing WebSocket or targetPeerId');
      }
    };

    // Handle remote stream
    this.peerConnection.ontrack = (event) => {
      console.log('Received remote stream:', event.streams);
      const stream = event.streams[0];
      this.remoteStreams.set(this.peerId, stream);
      this.onRemoteStreamUpdate(this.remoteStreams);
    };

    // Monitor signaling state changes
    this.peerConnection.onsignalingstatechange = () => {
      console.log(`PeerConnection signalingState changed to: ${this.peerConnection.signalingState}`);
      if (this.peerConnection.signalingState === 'closed') {
        this.isClosed = true;
        if (this.isInitializing) {
          this.onError(new Error('RTCPeerConnection closed during media stream initialization'));
        } else {
          this.onError(new Error('RTCPeerConnection is closed'));
        }
      }
    };

    // Monitor connection state changes
    this.peerConnection.onconnectionstatechange = () => {
      console.log(`PeerConnection connectionState changed to: ${this.peerConnection.connectionState}`);
      if (this.peerConnection.connectionState === 'failed') {
        this.onError(new Error('RTCPeerConnection connection failed'));
      } else if (this.peerConnection.connectionState === 'closed') {
        this.isClosed = true;
        if (this.isInitializing) {
          this.onError(new Error('RTCPeerConnection closed during media stream initialization'));
        } else {
          this.onError(new Error('RTCPeerConnection is closed'));
        }
      }
    };

    // Handle ICE connection state changes
    this.peerConnection.oniceconnectionstatechange = () => {
      console.log(`PeerConnection ICE connection state changed to: ${this.peerConnection.iceConnectionState}`);
      if (this.peerConnection.iceConnectionState === 'failed') {
        this.onError(new Error('ICE connection failed'));
      } else if (this.peerConnection.iceConnectionState === 'disconnected') {
        console.log('ICE connection disconnected, attempting to reconnect...');
        this.restartIce();
      }
    };

    // Handle ICE gathering state changes
    this.peerConnection.onicegatheringstatechange = () => {
      console.log(`PeerConnection ICE gathering state changed to: ${this.peerConnection.iceGatheringState}`);
    };
  }

  async initialize() {
    try {
      if (this.isClosed) {
        throw new Error('Cannot initialize: RTCPeerConnection is already closed');
      }

      this.isInitializing = true;
      console.log('Starting media stream initialization...');

      const maxRetries = 3;
      let retryCount = 0;
      let stream: MediaStream | null = null;

      while (retryCount < maxRetries && !stream) {
        try {
          stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true,
          });
        } catch (err) {
          retryCount++;
          if (retryCount === maxRetries) {
            throw new Error('Failed to get media stream after multiple attempts');
          }
          console.log(`Retrying getUserMedia (${retryCount}/${maxRetries})...`);
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }

      if (!stream) {
        throw new Error('Failed to obtain media stream');
      }

      this.localStream = stream;

      if (this.isClosed) {
        this.localStream.getTracks().forEach(track => track.stop());
        throw new Error('RTCPeerConnection closed during media stream initialization');
      }

      console.log('PeerConnection signalingState before addTrack:', this.peerConnection.signalingState);
      if (this.peerConnection.signalingState === 'closed') {
        this.localStream.getTracks().forEach(track => track.stop());
        throw new Error('Cannot add track: RTCPeerConnection is closed before addTrack');
      }

      this.localStream.getTracks().forEach(track => {
        if (!this.isClosed) {
          console.log('Adding track to RTCPeerConnection:', track);
          this.peerConnection.addTrack(track, this.localStream!);
        } else {
          throw new Error('Cannot add track: RTCPeerConnection is closed');
        }
      });

      this.isInitializing = false;
      return this.localStream;
    } catch (error) {
      this.isInitializing = false;
      this.onError(error instanceof Error ? error : new Error('Failed to initialize media'));
      throw error;
    }
  }

  getPeerId(): string {
    return this.peerId;
  }

  setWebSocket(ws: WebSocket) {
    this.ws = ws;
  }

  setTargetPeerId(targetPeerId: string) {
    this.targetPeerId = targetPeerId;
    console.log(`Set targetPeerId to: ${targetPeerId}`);
  }

  async createOffer(targetPeerId: string) {
    try {
      if (this.isClosed) {
        throw new Error('Cannot create offer: RTCPeerConnection is closed');
      }

      this.setTargetPeerId(targetPeerId); // Store targetPeerId for the session

      console.log('Creating offer for peer:', targetPeerId);
      const offer = await this.peerConnection.createOffer();
      if (this.isClosed) {
        throw new Error('RTCPeerConnection closed after creating offer');
      }

      console.log('Setting local description with offer...');
      await this.peerConnection.setLocalDescription(offer);
      if (this.isClosed) {
        throw new Error('RTCPeerConnection closed after setting local description');
      }

      if (this.ws && !this.isClosed) {
        this.ws.send(JSON.stringify({
          type: 'offer',
          offer,
          roomId: this.roomId,
          peerId: this.peerId,
          targetPeerId,
        }));
      } else {
        throw new Error('Cannot send offer: WebSocket is not available');
      }
    } catch (error) {
      this.onError(error instanceof Error ? error : new Error('Failed to create offer'));
    }
  }

  async handleOffer(offer: RTCSessionDescriptionInit, peerId: string) {
    try {
      if (this.isClosed) {
        throw new Error('Cannot handle offer: RTCPeerConnection is closed');
      }

      this.setTargetPeerId(peerId); // Store targetPeerId for the session

      console.log('Setting remote description with offer from:', peerId);
      await this.peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
      if (this.isClosed) {
        throw new Error('RTCPeerConnection closed after setting remote description');
      }

      console.log('Creating answer...');
      const answer = await this.peerConnection.createAnswer();
      if (this.isClosed) {
        throw new Error('RTCPeerConnection closed after creating answer');
      }

      console.log('Setting local description with answer...');
      await this.peerConnection.setLocalDescription(answer);
      if (this.isClosed) {
        throw new Error('RTCPeerConnection closed after setting local description');
      }

      if (this.ws && !this.isClosed) {
        this.ws.send(JSON.stringify({
          type: 'answer',
          answer,
          roomId: this.roomId,
          peerId: this.peerId,
          targetPeerId: peerId,
        }));
      } else {
        throw new Error('Cannot send answer: WebSocket is not available');
      }
    } catch (error) {
      this.onError(error instanceof Error ? error : new Error('Failed to handle offer'));
    }
  }

  async handleAnswer(answer: RTCSessionDescriptionInit) {
    try {
      if (this.isClosed) {
        throw new Error('Cannot handle answer: RTCPeerConnection is closed');
      }

      console.log('Setting remote description with answer...');
      await this.peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
    } catch (error) {
      this.onError(error instanceof Error ? error : new Error('Failed to handle answer'));
    }
  }

  async handleIceCandidate(candidate: RTCIceCandidateInit) {
    try {
      if (this.isClosed) {
        throw new Error('Cannot handle ICE candidate: RTCPeerConnection is closed');
      }

      console.log('Adding ICE candidate...');
      await this.peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
    } catch (error) {
      this.onError(error instanceof Error ? error : new Error('Failed to handle ICE candidate'));
    }
  }

  private async restartIce() {
    try {
      if (this.isClosed) {
        throw new Error('Cannot restart ICE: RTCPeerConnection is closed');
      }

      console.log('Restarting ICE...');
      const offer = await this.peerConnection.createOffer({ iceRestart: true });
      if (this.isClosed) {
        throw new Error('RTCPeerConnection closed after creating ICE restart offer');
      }

      await this.peerConnection.setLocalDescription(offer);
      if (this.isClosed) {
        throw new Error('RTCPeerConnection closed after setting ICE restart offer');
      }

      if (this.ws && !this.isClosed && this.targetPeerId) {
        this.ws.send(JSON.stringify({
          type: 'offer',
          offer,
          roomId: this.roomId,
          peerId: this.peerId,
          targetPeerId: this.targetPeerId,
        }));
      } else {
        throw new Error('Cannot send ICE restart offer: Missing WebSocket or targetPeerId');
      }
    } catch (error) {
      this.onError(error instanceof Error ? error : new Error('Failed to restart ICE'));
    }
  }

  disconnect() {
    if (this.isClosed) return;
    this.isClosed = true;
    console.log('Disconnecting PeerConnection...');
    this.peerConnection.close();
    if (this.localStream) {
      this.localStream.getTracks().forEach(track => track.stop());
    }
    this.remoteStreams.clear();
    this.onRemoteStreamUpdate(this.remoteStreams);
    this.ws = null;
  }

  getLocalStream() {
    return this.localStream;
  }

  toggleAudio(): boolean {
    if (this.localStream && !this.isClosed) {
      const audioTrack = this.localStream.getAudioTracks()[0];
      audioTrack.enabled = !audioTrack.enabled;
      return !audioTrack.enabled;
    }
    return false;
  }

  toggleVideo(): boolean {
    if (this.localStream && !this.isClosed) {
      const videoTrack = this.localStream.getVideoTracks()[0];
      videoTrack.enabled = !videoTrack.enabled;
      return !videoTrack.enabled;
    }
    return false;
  }
}