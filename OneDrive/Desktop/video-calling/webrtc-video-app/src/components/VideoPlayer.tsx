'use client'

import { useEffect, useRef } from 'react'

interface VideoPlayerProps {
  stream: MediaStream | null
  muted?: boolean
  userId?: string
}

export default function VideoPlayer({ stream, muted = false, userId }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream
    }
  }, [stream])

  return (
    <div className="relative">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted={muted}
        className="w-[400px] h-[300px] bg-black rounded-lg shadow"
      />
      <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded">
        {userId || (muted ? 'You' : 'Remote')}
      </div>
    </div>
  )
}