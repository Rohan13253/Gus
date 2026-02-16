import { useState, useEffect, useCallback } from 'react'
import StatusCard from './components/StatusCard'
import LiveLogs from './components/LiveLogs'
import ControlPanel from './components/ControlPanel'
import VoiceControl from './components/VoiceControl'
import { getStatus } from './api/endpoints'
import useGusSocket from './hooks/useGusSocket'

function App() {
  const [systemStatus, setSystemStatus] = useState(null)
  const [logs, setLogs] = useState([])
  const [alertActive, setAlertActive] = useState(false)

  // 1. WebSocket Message Handler
  const handleWebSocketMessage = useCallback((message) => {
    if (message.type === 'ai_response') {
      setLogs(prev => [...prev, { robot_response: message.text, timestamp: new Date().toISOString() }]);
    }
    else if (message.type === 'log') {
      setLogs(prev => [...prev, { message: message.data, timestamp: new Date().toISOString() }]);
    }
    else if (message.type === 'alert') {
      setAlertActive(true);
      setTimeout(() => setAlertActive(false), 5000); // Hide after 5s
      setLogs(prev => [...prev, { message: `🚨 ALERT: ${message.message}`, timestamp: new Date().toISOString() }]);
    }
  }, []);

  const { isConnected, sendMessage } = useGusSocket(handleWebSocketMessage);

  const handleManualChat = useCallback((text) => {
    setLogs(prev => [...prev, { user_text: text, timestamp: new Date().toISOString() }]);
    sendMessage(text);
  }, [sendMessage]);

  const handleVoiceInput = useCallback((audioBlob) => {
    setLogs(prev => [...prev, { user_text: '(voice message)', timestamp: new Date().toISOString() }]);
    sendMessage(audioBlob);
  }, [sendMessage]);

  // --- NEW: Handle Buttons via WebSocket ---
  const handleSystemCommand = useCallback((command, value = null) => {
    // This sends the command via WebSocket, triggering the EXACT same logic as Voice
    const payload = JSON.stringify({
      type: "command",
      command: command,
      value: value
    });
    sendMessage(payload);

    // Log it locally so you see it immediately
    setLogs(prev => [...prev, { user_text: `[COMMAND] ${command}`, timestamp: new Date().toISOString() }]);
  }, [sendMessage]);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await getStatus()
        setSystemStatus(status)
      } catch (error) { console.error('Failed to fetch status:', error) }
    }
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-base-200 p-8 relative">
      {/* RED ALERT OVERLAY */}
      {alertActive && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-red-600/90 animate-pulse pointer-events-none">
          <div className="text-white text-center">
            <h1 className="text-8xl font-black mb-4">⚠️ ALERT ⚠️</h1>
            <p className="text-4xl font-bold tracking-widest">SECURITY BREACH DETECTED</p>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8 text-primary">
          🤖 Gus - IoT Robot Assistant
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <StatusCard status={systemStatus} isConnected={isConnected} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <LiveLogs logs={logs} />

          {/* PASS THE NEW WEBSOCKET HANDLER HERE */}
          <ControlPanel
            onCommandSent={handleSystemCommand}
            onSendMessage={handleManualChat}
          />
        </div>

        <VoiceControl
          onVoiceRecorded={handleVoiceInput}
          disabled={!isConnected}
        />
      </div>
    </div>
  )
}

export default App