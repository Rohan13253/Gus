#!/usr/bin/env python3
"""
Virtual ESP32 - Simulator for the Gus robot hardware.
Connects to the server at ws://127.0.0.1:8000/ws/robot and prints
incoming commands as graphical logs. Run the server first, then this script.
"""

import asyncio
import json
import sys

try:
    import websockets
except ImportError:
    print("Install websockets: pip install websockets")
    sys.exit(1)

WS_URL = "ws://127.0.0.1:8000/ws/robot"
RECONNECT_DELAY = 3
MAX_RECONNECT_DELAY = 30


def format_command(action: str, value: str) -> str:
    """Turn action/value into a human-readable graphical log line."""
    action_upper = action.upper()
    value_upper = value.upper() if isinstance(value, str) else str(value)
    if action_upper == "LED":
        return f"Turning LED {value_upper}"
    if action_upper == "SERVO":
        return f"Moving SERVO {value_upper}"
    if action_upper == "BUZZER":
        return f"BUZZER {value_upper}"
    if action_upper == "VOLUME":
        return f"Setting VOLUME to {value_upper}"
    return f"{action_upper} {value_upper}"


async def run_robot() -> None:
    delay = RECONNECT_DELAY
    while True:
        try:
            async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=10) as ws:
                delay = RECONNECT_DELAY
                print("🤖 VIRTUAL ROBOT: Connected to server. Waiting for commands...\n")
                while True:
                    raw = await ws.recv()
                    try:
                        data = json.loads(raw)
                        action = data.get("action", "?")
                        value = data.get("value", "?")
                        line = format_command(action, value)
                        print(f"🤖 VIRTUAL ROBOT: {line}")
                    except json.JSONDecodeError:
                        print(f"🤖 VIRTUAL ROBOT: (raw) {raw}")
        except (websockets.exceptions.ConnectionClosed, OSError, ConnectionRefusedError) as e:
            print(f"⚠️  Connection lost: {e}. Reconnecting in {delay}s...")
            await asyncio.sleep(delay)
            delay = min(delay * 2, MAX_RECONNECT_DELAY)
        except KeyboardInterrupt:
            print("\n🤖 VIRTUAL ROBOT: Shutting down.")
            break


if __name__ == "__main__":
    asyncio.run(run_robot())
