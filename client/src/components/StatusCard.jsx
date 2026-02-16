/**
 * StatusCard Component
 * Displays system status: Temperature, Humidity, Online status, Battery, Mode
 */

import React from 'react'

const StatusCard = ({ status, isConnected }) => {
  if (!status) {
    return (
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title">System Status</h2>
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card bg-base-100 shadow-xl col-span-1 lg:col-span-3">
      <div className="card-body">
        <h2 className="card-title text-2xl">System Status</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-4">
          {/* Online Status */}
          <div className="stat">
            <div className="stat-title">Connection</div>
            <div className={`stat-value text-sm ${isConnected ? 'text-success' : 'text-error'}`}>
              {isConnected ? '🟢 Online' : '🔴 Offline'}
            </div>
          </div>

          {/* Mode */}
          <div className="stat">
            <div className="stat-title">Mode</div>
            <div className="stat-value text-sm capitalize">{status.mode || 'normal'}</div>
          </div>

          {/* Battery Level */}
          <div className="stat">
            <div className="stat-title">Battery</div>
            <div className="stat-value text-sm">{status.battery_level?.toFixed(0) || 100}%</div>
          </div>

          {/* Volume */}
          <div className="stat">
            <div className="stat-title">Volume</div>
            <div className="stat-value text-sm">{(status.volume * 100)?.toFixed(0) || 50}%</div>
          </div>

          {/* Recent Interactions */}
          <div className="stat">
            <div className="stat-title">Interactions</div>
            <div className="stat-value text-sm">{status.recent_interactions || 0}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatusCard
