"""
Hardware Bridge Service.
Singleton that manages a single active WebSocket connection to the ESP32 robot.
Sends JSON commands (action, value) to the connected hardware.
"""

from typing import Optional
from fastapi import WebSocket


class HardwareBridge:
    """Singleton bridge to the ESP32 robot over WebSocket."""

    _instance: Optional["HardwareBridge"] = None

    def __new__(cls) -> "HardwareBridge":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.active_connection: Optional[WebSocket] = None
        self._initialized = True

    def connect(self, websocket: WebSocket) -> None:
        """Accept and store the single active robot connection."""
        self.active_connection = websocket

    def disconnect(self) -> None:
        """Clear the active connection (call when robot disconnects)."""
        self.active_connection = None

    async def send_command(self, action: str, value: str) -> bool:
        """
        Send a JSON payload to the connected robot.
        Payload format: {"action": action, "value": value}
        Returns True if sent, False if no connection.
        """
        if self.active_connection is None:
            print("[HardwareBridge] No robot connected, skipping command")
            return False
        payload = {"action": action, "value": value}
        try:
            await self.active_connection.send_json(payload)
            print(f"[HardwareBridge] Sent: {payload}")
            return True
        except Exception as e:
            print(f"[HardwareBridge] Send failed: {e}")
            self.disconnect()
            return False


async def execute_frontend_command(cmd_type: str, value: Optional[str] = None) -> None:
    """
    Map frontend command types to hardware actions.
    Called from API and WebSocket when user triggers a mode/action.
    """
    bridge = get_hardware_bridge()
    if cmd_type == "study_mode":
        await bridge.send_command("LED", "BLUE")
    elif cmd_type == "privacy_mode":
        await bridge.send_command("SERVO", "DOWN")
        await bridge.send_command("LED", "OFF")
    elif cmd_type == "trigger_alarm":
        await bridge.send_command("BUZZER", "ON")
        await bridge.send_command("LED", "RED_BLINK")
    elif cmd_type == "normal_mode":
        await bridge.send_command("LED", "GREEN")
    # set_volume can be sent to robot if needed later
    elif cmd_type == "set_volume" and value is not None:
        await bridge.send_command("VOLUME", str(value))


# Module-level singleton access
def get_hardware_bridge() -> HardwareBridge:
    return HardwareBridge()
