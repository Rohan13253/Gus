import React, { useState } from 'react'

const ControlPanel = ({ onCommandSent, onSendMessage }) => {
  const [chatInput, setChatInput] = useState('')

  // This function passes the command UP to App.jsx -> WebSocket
  const handleCommand = (commandType, value = null) => {
    if (onCommandSent) {
      onCommandSent(commandType, value);
    }
  };

  const handleChatSubmit = (e) => {
    e.preventDefault()
    if (chatInput.trim() && onSendMessage) {
      onSendMessage(chatInput.trim())
      setChatInput('')
    }
  }

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title">🎮 Control Panel</h2>

        <div className="grid grid-cols-2 gap-4 mt-4">
          {/* Normal Mode */}
          <button
            className="btn btn-success btn-lg"
            onClick={() => handleCommand('normal_mode')}
          >
            ✅ Normal Mode
          </button>

          {/* Study Mode */}
          <button
            className="btn btn-primary btn-lg"
            onClick={() => handleCommand('study_mode')}
          >
            📚 Study Mode
          </button>

          {/* Privacy Mode */}
          <button
            className="btn btn-secondary btn-lg"
            onClick={() => handleCommand('privacy_mode')}
          >
            🔒 Privacy Mode
          </button>

          {/* Trigger Alarm */}
          <button
            className="btn btn-error btn-lg animate-pulse"
            onClick={() => handleCommand('trigger_alarm')}
          >
            🚨 Trigger Alarm
          </button>
        </div>

        {/* Chat with Gus */}
        <div className="mt-6">
          <h3 className="font-semibold mb-2">💬 Chat with Gus</h3>
          <form onSubmit={handleChatSubmit} className="flex gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Type your message..."
              className="input input-bordered flex-1"
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!chatInput.trim()}
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default ControlPanel