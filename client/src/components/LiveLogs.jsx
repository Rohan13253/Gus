/**
 * LiveLogs Component
 * Matrix-style scrolling terminal window for voice interaction logs.
 * Displays real-time logs with a retro terminal aesthetic.
 */

import React, { useEffect, useRef } from 'react'

const LiveLogs = ({ logs }) => {
  const logContainerRef = useRef(null)

  useEffect(() => {
    // Auto-scroll to bottom when new logs arrive
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs])

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title">📡 Live Voice Logs</h2>
        
        <div 
          ref={logContainerRef}
          className="bg-black text-green-400 font-mono text-sm p-4 rounded-lg h-96 overflow-y-auto"
          style={{
            fontFamily: 'monospace',
            background: 'linear-gradient(to bottom, #000000 0%, #001100 100%)',
            boxShadow: 'inset 0 0 20px rgba(0, 255, 0, 0.1)'
          }}
        >
          {logs.length === 0 ? (
            <div className="text-green-500 opacity-50">
              <div className="animate-pulse">Waiting for voice interactions...</div>
              <div className="mt-2 text-xs opacity-30">
                {`> Gus System Ready`}
              </div>
            </div>
          ) : (
            logs.map((log, index) => (
              <div 
                key={index} 
                className="mb-2 border-l-2 border-green-500 pl-2"
                style={{
                  animation: 'fadeIn 0.3s ease-in',
                  textShadow: '0 0 5px rgba(0, 255, 0, 0.5)'
                }}
              >
                <span className="text-green-300 text-xs">
                  {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : 'NOW'}
                </span>
                <div className="text-green-400 mt-1">
                  {log.user_text && (
                    <div className="mb-1">
                      <span className="text-yellow-400">USER:</span> {log.user_text}
                    </div>
                  )}
                  {log.robot_response && (
                    <div>
                      <span className="text-cyan-400">GUS:</span> {log.robot_response}
                    </div>
                  )}
                  {log.message && <div>{log.message}</div>}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  )
}

export default LiveLogs
