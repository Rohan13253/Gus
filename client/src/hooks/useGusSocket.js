/**
 * useGusSocket Hook
 * Custom React hook to manage WebSocket connection to the backend.
 * Handles connection, reconnection, and message handling.
 */

import { useState, useEffect, useRef, useCallback } from 'react'

const useGusSocket = (onMessage) => {
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const reconnectAttemptsRef = useRef(0)
  const onMessageRef = useRef(onMessage)
  const isConnectingRef = useRef(false)

  // Keep onMessage callback ref updated
  useEffect(() => {
    onMessageRef.current = onMessage
  }, [onMessage])

  const connect = useCallback(() => {
    // Prevent multiple connection attempts
    if (isConnectingRef.current || (wsRef.current && wsRef.current.readyState === WebSocket.OPEN)) {
      return
    }

    isConnectingRef.current = true

    try {
      // Close existing connection if any
      if (wsRef.current) {
        wsRef.current.close()
      }

      // WebSocket URL - adjust port if needed
      const wsUrl = 'ws://localhost:8000/ws/audio'
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('WebSocket connected to Gus backend')
        setIsConnected(true)
        reconnectAttemptsRef.current = 0
        isConnectingRef.current = false
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (onMessageRef.current) {
            onMessageRef.current(data)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        isConnectingRef.current = false
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        isConnectingRef.current = false
        
        // Only reconnect if not manually closed
        if (wsRef.current === ws) {
          // Attempt reconnection with exponential backoff
          const maxAttempts = 10
          if (reconnectAttemptsRef.current < maxAttempts) {
            const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectAttemptsRef.current += 1
              connect()
            }, delay)
          } else {
            console.error('Max reconnection attempts reached')
          }
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      isConnectingRef.current = false
    }
  }, [])

  useEffect(() => {
    connect()

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
      isConnectingRef.current = false
    }
  }, [connect])

  const sendMessage = (message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      if (message instanceof Blob) {
        wsRef.current.send(message)
      } else if (typeof message === 'string') {
        wsRef.current.send(message)
      } else {
        wsRef.current.send(JSON.stringify(message))
      }
      return true
    }
    console.warn('WebSocket is not connected')
    return false
  }

  return {
    isConnected,
    sendMessage
  }
}

export default useGusSocket
