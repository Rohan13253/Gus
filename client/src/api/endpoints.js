/**
 * API Endpoints
 * Central file for all HTTP fetch calls to the Python FastAPI server.
 */

const API_BASE_URL = 'http://localhost:8000/api'

/**
 * Fetch current system status
 * @returns {Promise<Object>} System status object
 */
export const getStatus = async () => {
  const response = await fetch(`${API_BASE_URL}/status`)
  if (!response.ok) {
    throw new Error(`Failed to fetch status: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Send a command to the robot
 * @param {Object} command - Command object with type and optional value
 * @param {string} command.type - Command type (study_mode, privacy_mode, trigger_alarm, set_volume, normal_mode)
 * @param {any} command.value - Optional value for commands like set_volume
 * @returns {Promise<Object>} Response object
 */
export const sendCommand = async (command) => {
  const response = await fetch(`${API_BASE_URL}/command`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(command),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || `Failed to send command: ${response.statusText}`)
  }

  return response.json()
}

/**
 * Get interaction logs (if endpoint exists)
 * @param {number} limit - Maximum number of logs to retrieve
 * @returns {Promise<Array>} Array of interaction logs
 */
export const getLogs = async (limit = 50) => {
  const response = await fetch(`${API_BASE_URL}/logs?limit=${limit}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch logs: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Get reminders (if endpoint exists)
 * @returns {Promise<Array>} Array of reminders
 */
export const getReminders = async () => {
  const response = await fetch(`${API_BASE_URL}/reminders`)
  if (!response.ok) {
    throw new Error(`Failed to fetch reminders: ${response.statusText}`)
  }
  return response.json()
}
