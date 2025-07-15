// src/app/page.tsx
'use client'

import { useState } from 'react';
import { useRouter } from 'next/navigation'; // Use next/navigation for App Router
import { v4 as uuidv4 } from 'uuid';

export default function Home() {
  const [roomCode, setRoomCode] = useState('');
  const router = useRouter();

  const startNewCall = () => {
    try {
      const newRoomId = uuidv4();
      console.log('Starting new call with room ID:', newRoomId);
      router.push(`/room/${newRoomId}`);
      console.log('Navigation attempted to:', `/room/${newRoomId}`);
    } catch (error) {
      console.error('Error starting new call:', error);
    }
  };

  const joinRoom = () => {
    if (roomCode.trim()) {
      console.log('Joining room with code:', roomCode);
      router.push(`/room/${roomCode.trim()}`);
      console.log('Navigation attempted to:', `/room/${roomCode.trim()}`);
    } else {
      console.log('No room code entered');
      alert('Please enter a room code');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      joinRoom();
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#1a2634]">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">WebRTC Video Call</h1>
        <p className="text-gray-400 mb-8">Start a secure, peer-to-peer video call</p>
        <div className="bg-[#2a3b4d] p-6 rounded-lg shadow-lg max-w-md w-full">
          <button
            onClick={startNewCall}
            className="w-full p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors mb-4"
          >
            Start New Call
          </button>
          <div className="flex items-center justify-center mb-4">
            <span className="text-gray-400">or</span>
          </div>
          <input
            type="text"
            value={roomCode}
            onChange={(e) => setRoomCode(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter room code"
            className="w-full p-3 bg-[#3b4a5b] text-white rounded-lg mb-4 focus:outline-none placeholder-gray-400"
          />
          <button
            onClick={joinRoom}
            className="w-full p-3 bg-[#3b4a5b] text-white rounded-lg hover:bg-[#4a5b6b] transition-colors"
          >
            Join Room
          </button>
        </div>
        <p className="text-gray-500 text-sm mt-8">
          Powered by WebRTC and Next.js
        </p>
      </div>
    </div>
  );
}