// src/app/room/[id]/page.tsx
'use client'

import { useEffect, useState, useRef } from 'react';
import { useRouter, useParams } from 'next/navigation';
import VideoPlayer from '../../../components/VideoPlayer';
import CallControls from '../../../components/CallControls';
import { PeerConnection } from '../../../components/PeerConnection';
import { connectToSignalingServer } from '../../../utils/signaling';

export default function Room() {
  const router = useRouter();
  const params = useParams();
  const roomId = params?.id;
  const [peerConnection, setPeerConnection] = useState<PeerConnection | null>(null);
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [remoteStreams, setRemoteStreams] = useState<Map<string, MediaStream>>(new Map());
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const isMounted = useRef(true);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    isMounted.current = true;

    if (!roomId || typeof roomId !== 'string') {
      console.error('Invalid room ID:', roomId);
      setError('Invalid room ID');
      setIsLoading(false);
      return;
    }

    console.log('Setting up WebRTC for room:', roomId);

    const pc = new PeerConnection(
      roomId,
      (streams: Map<string, MediaStream>) => {
        if (isMounted.current) {
          console.log('Remote streams updated:', streams);
          setRemoteStreams(new Map(streams));
        }
      },
      (err: Error) => {
        if (isMounted.current) {
          console.error('PeerConnection error:', err);
          setError(err.message);
          setIsLoading(false);
        }
      }
    );
    setPeerConnection(pc);

    const setup = async () => {
      try {
        console.log('Initializing local stream...');
        const stream = await pc.initialize();
        if (!isMounted.current) return;
        setLocalStream(stream);
        console.log('Local stream initialized:', stream);

        console.log('Connecting to signaling server...');
        const ws = await connectToSignalingServer(roomId);
        if (!isMounted.current) return;
        wsRef.current = ws;
        pc.setWebSocket(ws);
        console.log('WebSocket connection established');

        ws.onmessage = (event) => {
          if (!isMounted.current) return;
          console.log('Received WebSocket message:', event.data);
          try {
            const data = JSON.parse(event.data);
            switch (data.type) {
              case 'peerId':
                if (data.peerId !== pc.getPeerId()) {
                  console.log('Creating offer for peer:', data.peerId);
                  pc.createOffer(data.peerId);
                } else {
                  console.log('Ignoring own peerId:', data.peerId);
                }
                break;
              case 'offer':
                if (data.targetPeerId === pc.getPeerId()) {
                  console.log('Handling offer from:', data.peerId);
                  pc.handleOffer(data.offer, data.peerId);
                }
                break;
              case 'answer':
                if (data.targetPeerId === pc.getPeerId()) {
                  console.log('Handling answer from:', data.peerId);
                  pc.handleAnswer(data.answer);
                }
                break;
              case 'ice-candidate':
                if (data.targetPeerId === pc.getPeerId()) {
                  console.log('Handling ICE candidate from:', data.peerId);
                  pc.handleIceCandidate(data.candidate);
                }
                break;
              case 'error':
                setError(data.message);
                break;
              default:
                console.log('Unknown message type:', data.type);
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
            setError('Failed to parse signaling message');
          }
        };

        ws.onerror = (error) => {
          if (!isMounted.current) return;
          console.error('WebSocket error:', error);
          setError('Signaling server connection failed');
          setIsLoading(false);
        };

        ws.onclose = (event) => {
          if (!isMounted.current) return;
          console.log(`WebSocket closed: code=${event.code}, reason=${event.reason}`);
          setError('Signaling server disconnected');
          setIsLoading(false);
        };

        console.log('Sending join message for peer:', pc.getPeerId());
        ws.send(JSON.stringify({ 
          type: 'join', 
          roomId, 
          peerId: pc.getPeerId() 
        }));

        setIsLoading(false);
      } catch (err) {
        if (!isMounted.current) return;
        console.error('Setup error:', err);
        setError(err instanceof Error ? err.message : 'Failed to setup video call');
        setIsLoading(false);
      }
    };

    setup();

    return () => {
      isMounted.current = false;
      console.log('Cleaning up WebRTC connection');
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      pc?.disconnect();
    };
  }, [roomId]);

  const handleEndCall = () => {
    console.log('Ending call');
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    peerConnection?.disconnect();
    router.push('/');
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-800 via-gray-900 to-black text-white p-6">
      {error && (
        <div className="mb-6 p-4 bg-red-600 bg-opacity-30 backdrop-blur-md rounded-lg shadow-lg flex items-center justify-between w-full max-w-2xl border border-red-500">
          <span>Error: {error}</span>
          <button
            onClick={() => router.push('/')}
            className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            Return Home
          </button>
        </div>
      )}
      <div className="w-full max-w-5xl">
        {isLoading ? (
          <div className="text-center">
            <svg className="animate-spin h-8 w-8 text-blue-400 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-gray-300 mt-2 text-lg">Joining your video call...</p>
          </div>
        ) : (
          <>
            <h1 className="text-3xl font-bold mb-6 text-center text-gray-100">
              Video Call - Room: {roomId}
            </h1>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 justify-items-center">
              {localStream ? (
                <div className="relative w-full max-w-md bg-gray-800 rounded-lg overflow-hidden shadow-xl">
                  <VideoPlayer stream={localStream} muted />
                  <div className="absolute bottom-3 left-3 bg-gray-900 bg-opacity-70 text-gray-200 px-4 py-1 rounded-full text-sm shadow-lg">
                    You
                  </div>
                </div>
              ) : (
                <div className="text-gray-300 text-center">Failed to load local stream</div>
              )}
              {Array.from(remoteStreams.entries()).map(([peerId, stream]) => (
                <div key={peerId} className="relative w-full max-w-md bg-gray-800 rounded-lg overflow-hidden shadow-xl transform transition-all duration-500 ease-in-out animate-join">
                  <VideoPlayer stream={stream} userId={peerId.slice(0, 8)} />
                  <div className="absolute bottom-3 left-3 bg-gray-900 bg-opacity-70 text-gray-200 px-4 py-1 rounded-full text-sm shadow-lg">
                    {peerId.slice(0, 8)}
                  </div>
                </div>
              ))}
            </div>
            {peerConnection && (
              <div className="mt-8 flex justify-center gap-4">
                <button
                  onClick={() => setIsMuted(peerConnection.toggleAudio())}
                  className={`px-6 py-3 rounded-full text-gray-200 font-semibold shadow-lg bg-opacity-70 backdrop-blur-md transition-colors ${
                    isMuted ? 'bg-gray-600' : 'bg-blue-600 hover:bg-blue-500'
                  }`}
                >
                  {isMuted ? 'Unmute' : 'Mute'}
                </button>
                <button
                  onClick={() => setIsVideoOff(peerConnection.toggleVideo())}
                  className={`px-6 py-3 rounded-full text-gray-200 font-semibold shadow-lg bg-opacity-70 backdrop-blur-md transition-colors ${
                    isVideoOff ? 'bg-gray-600' : 'bg-blue-600 hover:bg-blue-500'
                  }`}
                >
                  {isVideoOff ? 'Video On' : 'Video Off'}
                </button>
                <button
                  onClick={handleEndCall}
                  className="px-6 py-3 rounded-full bg-red-600 text-gray-200 font-semibold hover:bg-red-500 shadow-lg bg-opacity-70 backdrop-blur-md transition-colors"
                >
                  End Call
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}