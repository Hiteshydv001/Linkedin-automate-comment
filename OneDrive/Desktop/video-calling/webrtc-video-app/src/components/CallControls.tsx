'use client'

interface CallControlsProps {
  stream: MediaStream | null
  isMuted: boolean
  isVideoOff: boolean
  onToggleMute: () => void
  onToggleVideo: () => void
  onEndCall: () => void
}

export default function CallControls({
  stream,
  isMuted,
  isVideoOff,
  onToggleMute,
  onToggleVideo,
  onEndCall
}: CallControlsProps) {
  return (
    <div className="flex justify-center gap-4 mt-6">
      <button
        onClick={onToggleMute}
        className={`px-4 py-2 rounded-full text-white ${isMuted ? 'bg-gray-500' : 'bg-blue-500'} hover:bg-opacity-80`}
        disabled={!stream}
      >
        {isMuted ? 'Unmute' : 'Mute'}
      </button>
      <button
        onClick={onToggleVideo}
        className={`px-4 py-2 rounded-full text-white ${isVideoOff ? 'bg-gray-500' : 'bg-blue-500'} hover:bg-opacity-80`}
        disabled={!stream}
      >
        {isVideoOff ? 'Video On' : 'Video Off'}
      </button>
      <button
        onClick={onEndCall}
        className="px-4 py-2 rounded-full bg-red-500 text-white hover:bg-red-600"
      >
        End Call
      </button>
    </div>
  )
}