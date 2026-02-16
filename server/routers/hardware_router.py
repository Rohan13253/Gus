"""
Hardware Router - WebSocket endpoint for the ESP32 robot.
Single connection managed by HardwareBridge.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from server.services.hardware_bridge import get_hardware_bridge

router = APIRouter()
bridge = get_hardware_bridge()


@router.websocket("/ws/robot")
async def websocket_robot_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for the physical (or virtual) ESP32 robot.
    Only one active connection is held; new connection replaces the previous.
    """
    await websocket.accept()
    bridge.connect(websocket)
    print(f"🤖 Robot connected: {websocket.client}")

    try:
        while True:
            # Keep connection alive and detect disconnects
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        bridge.disconnect()
        print("🤖 Robot disconnected")
