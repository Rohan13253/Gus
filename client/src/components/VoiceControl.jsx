/**
 * VoiceControl – Browser mic for talking to Gus.
 * Hold the button to record (MediaRecorder); release to send audio blob to parent.
 */

import React, { useState, useRef } from 'react'

const VoiceControl = ({ onVoiceRecorded, disabled = false }) => {
  const [listening, setListening] = useState(false)
  const [error, setError] = useState(null)
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])

  const startRecording = async () => {
    if (disabled) return
    setError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      chunksRef.current = []
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }
      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop())
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        if (blob.size > 0 && onVoiceRecorded) onVoiceRecorded(blob)
      }
      recorder.start(100)
      mediaRecorderRef.current = recorder
      setListening(true)
    } catch (err) {
      setError(err.message || 'Microphone access failed')
      setListening(false)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current = null
    }
    setListening(false)
  }

  return (
    <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-10 flex flex-col items-center gap-2">
      {error && (
        <div className="text-error text-sm bg-base-100 px-3 py-1 rounded-full shadow-lg">
          {error}
        </div>
      )}
      <button
        type="button"
        className={`btn btn-circle w-20 h-20 shadow-2xl border-4 ${
          listening ? 'btn-error animate-pulse' : 'btn-primary'
        }`}
        onMouseDown={startRecording}
        onMouseUp={stopRecording}
        onMouseLeave={stopRecording}
        onTouchStart={(e) => { e.preventDefault(); startRecording(); }}
        onTouchEnd={(e) => { e.preventDefault(); stopRecording(); }}
        disabled={disabled}
        aria-label={listening ? 'Release to send' : 'Hold to talk'}
        title={listening ? 'Release to send' : 'Hold to talk'}
      >
        <span className="text-3xl">{listening ? '🔴' : '🎤'}</span>
      </button>
      <span className="text-sm font-medium text-base-content bg-base-100 px-3 py-1 rounded-full shadow-lg">
        {listening ? '🔴 Listening...' : 'Hold to talk'}
      </span>
    </div>
  )
}

export default VoiceControl
