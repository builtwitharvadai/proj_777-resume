import { useState, useEffect, useRef, useCallback } from 'react'
import { authService } from '../services/auth'
import { WebSocketMessage } from '../types/qa'

export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error'

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void
  onConnectionChange?: (state: ConnectionState) => void
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export const useWebSocket = (url: string, options: UseWebSocketOptions = {}) => {
  const {
    onMessage,
    onConnectionChange,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
  } = options

  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected')
  const [lastError, setLastError] = useState<string | null>(null)

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef<number>(0)
  const shouldReconnectRef = useRef<boolean>(true)
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null)

  const updateConnectionState = useCallback(
    (state: ConnectionState) => {
      setConnectionState(state)
      onConnectionChange?.(state)

      console.warn('[WebSocket] Connection state changed', {
        state,
        timestamp: new Date().toISOString(),
      })
    },
    [onConnectionChange]
  )

  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
  }, [])

  const clearPingInterval = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current)
      pingIntervalRef.current = null
    }
  }, [])

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify(message))

        console.warn('[WebSocket] Message sent', {
          type: message.type,
          timestamp: new Date().toISOString(),
        })

        return true
      } catch (error) {
        console.error('[WebSocket] Failed to send message', {
          error,
          type: message.type,
          timestamp: new Date().toISOString(),
        })

        return false
      }
    } else {
      console.error('[WebSocket] Cannot send message - not connected', {
        readyState: wsRef.current?.readyState,
        timestamp: new Date().toISOString(),
      })

      return false
    }
  }, [])

  const startPingInterval = useCallback(() => {
    clearPingInterval()

    pingIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        sendMessage({
          type: 'ping',
          timestamp: new Date().toISOString(),
        })
      }
    }, 30000)
  }, [clearPingInterval, sendMessage])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
      console.warn('[WebSocket] Connection already exists', {
        readyState: wsRef.current.readyState,
        timestamp: new Date().toISOString(),
      })
      return
    }

    try {
      updateConnectionState('connecting')
      clearReconnectTimeout()

      const token = authService.getAccessToken()
      if (!token) {
        throw new Error('No authentication token available')
      }

      const wsUrl = `${url}?token=${encodeURIComponent(token)}`

      console.warn('[WebSocket] Initiating connection', {
        url,
        timestamp: new Date().toISOString(),
      })

      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.warn('[WebSocket] Connection established', {
          timestamp: new Date().toISOString(),
        })

        updateConnectionState('connected')
        reconnectAttemptsRef.current = 0
        setLastError(null)
        startPingInterval()
      }

      ws.onmessage = (event: MessageEvent) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)

          console.warn('[WebSocket] Message received', {
            type: message.type,
            timestamp: new Date().toISOString(),
          })

          if (message.type === 'pong') {
            return
          }

          onMessage?.(message)
        } catch (error) {
          console.error('[WebSocket] Failed to parse message', {
            error,
            data: event.data,
            timestamp: new Date().toISOString(),
          })
        }
      }

      ws.onerror = (error) => {
        console.error('[WebSocket] Connection error', {
          error,
          timestamp: new Date().toISOString(),
        })

        setLastError('WebSocket connection error')
        updateConnectionState('error')
      }

      ws.onclose = (event: CloseEvent) => {
        console.warn('[WebSocket] Connection closed', {
          code: event.code,
          reason: event.reason,
          wasClean: event.wasClean,
          timestamp: new Date().toISOString(),
        })

        clearPingInterval()
        updateConnectionState('disconnected')

        if (shouldReconnectRef.current && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1

          console.warn('[WebSocket] Scheduling reconnection attempt', {
            attempt: reconnectAttemptsRef.current,
            maxAttempts: maxReconnectAttempts,
            interval: reconnectInterval,
            timestamp: new Date().toISOString(),
          })

          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          console.error('[WebSocket] Max reconnection attempts reached', {
            attempts: reconnectAttemptsRef.current,
            timestamp: new Date().toISOString(),
          })

          setLastError('Failed to reconnect after maximum attempts')
          updateConnectionState('error')
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('[WebSocket] Failed to create connection', {
        error,
        timestamp: new Date().toISOString(),
      })

      setLastError(error instanceof Error ? error.message : 'Unknown error')
      updateConnectionState('error')
    }
  }, [url, updateConnectionState, clearReconnectTimeout, onMessage, maxReconnectAttempts, reconnectInterval, startPingInterval, clearPingInterval])

  const disconnect = useCallback(() => {
    console.warn('[WebSocket] Disconnecting', {
      timestamp: new Date().toISOString(),
    })

    shouldReconnectRef.current = false
    clearReconnectTimeout()
    clearPingInterval()

    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnect')
      wsRef.current = null
    }

    updateConnectionState('disconnected')
  }, [updateConnectionState, clearReconnectTimeout, clearPingInterval])

  useEffect(() => {
    shouldReconnectRef.current = true
    connect()

    return () => {
      shouldReconnectRef.current = false
      disconnect()
    }
  }, [url])

  return {
    connectionState,
    lastError,
    sendMessage,
    connect,
    disconnect,
  }
}
