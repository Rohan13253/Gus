"""
WebSocket Router for real-time audio streaming.
Handles "/ws/audio" connection from ESP32 or browser; text commands and binary audio.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import os
import re  # Added for regex

# 1. Import the Brain, Hardware Bridge, and Transcriber
from server.services.ai_engine import get_ai_engine
from server.services.hardware_bridge import execute_frontend_command, get_hardware_bridge
from server.services.transcriber import Transcriber

router = APIRouter()

# Store active WebSocket connections
active_connections: List[WebSocket] = []

# 2. Shared brain and transcriber
brain = get_ai_engine()
transcriber = Transcriber()
bridge = get_hardware_bridge()

# Global state to track if we are waiting for the user's age
waiting_for_age = False

@router.websocket("/audio")
async def websocket_audio_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for ESP32 audio stream.
    Receives raw PCM audio bytes OR text commands.
    """
    global waiting_for_age
    await websocket.accept()
    active_connections.append(websocket)
    print(f"✅ Client Connected: {websocket.client}")

    try:
        while True:
            # Receive data
            data = await websocket.receive()

            # CASE A: Binary Audio – Voice Commands
            if "bytes" in data:
                audio_bytes = data["bytes"]

                # 1. Transcribe
                text = transcriber.transcribe_audio(audio_bytes)

                if text:
                    print(f"🎤 Voice Heard: {text}")
                    lower_text = text.lower()

                    # === 1. CHECK IF WAITING FOR AGE ===
                    if waiting_for_age:
                        # Extract number from response (e.g., "I am 8", "Eight", "8")
                        age_match = re.search(r"\d+", lower_text)

                        # Handle text numbers (simple case for "eight", "ten" - optional, sticking to digits for robustness)
                        # You can expand this if needed, but regex \d+ catches "8", "10" etc.

                        if age_match:
                            age = int(age_match.group(0))
                            brain.set_age(age)
                            brain.set_mode("child")
                            waiting_for_age = False  # Reset state

                            response_text = f"Got it! You are {age} years old. I am now Gus Junior! 🎈 Ready to play?"

                            # Playful hardware feedback
                            await bridge.send_command("LED", "GREEN_BLINK")
                            await websocket.send_json({"type": "ai_response", "text": response_text})
                            await bridge.send_command("SAY", response_text)
                            continue  # Skip the rest of the loop
                        else:
                            # User didn't say a number
                            response_text = "I didn't catch that number. How old are you?"
                            await websocket.send_json({"type": "ai_response", "text": response_text})
                            await bridge.send_command("SAY", response_text)
                            continue

                    # === 2. STANDARD COMMANDS ===

                    # Command: Switch to Child Mode
                    if "child mode" in lower_text or "kids mode" in lower_text or "junior" in lower_text:
                        print("🤖 Intent Detected: CHILD MODE")
                        if brain.user_age:
                            # We already know the age
                            brain.set_mode("child")
                            response_text = f"Switching to Child Mode for age {brain.user_age}! 🌟"
                            await bridge.send_command("LED", "GREEN_BLINK")
                            await websocket.send_json({"type": "ai_response", "text": response_text})
                            await bridge.send_command("SAY", response_text)
                        else:
                            # We need to ask for age
                            waiting_for_age = True
                            response_text = "Sure thing! But first, how old are you?"
                            await websocket.send_json({"type": "ai_response", "text": response_text})
                            await bridge.send_command("SAY", response_text)

                    # Command: Study Mode
                    elif "study" in lower_text or "focus" in lower_text:
                        print("🤖 Intent Detected: STUDY")
                        waiting_for_age = False # Cancel age wait if they switch mode
                        brain.set_mode("study")
                        await bridge.send_command("LED", "BLUE")
                        response_text = "Study Mode Activated. Blue LED is on. I am now your strict tutor."
                        await websocket.send_json({"type": "ai_response", "text": response_text})
                        await bridge.send_command("SAY", response_text)

                    # Command: Alarm / Emergency
                    elif "alarm" in lower_text or "emergency" in lower_text or "security" in lower_text:
                        print("🤖 Intent Detected: ALARM")
                        waiting_for_age = False
                        brain.set_mode("alarm")
                        await bridge.send_command("BUZZER", "ON")
                        await bridge.send_command("LED", "RED_BLINK")
                        await websocket.send_json({"type": "alert", "message": "SECURITY BREACH DETECTED"})
                        response_text = "ALARM TRIGGERED. Security protocols active."
                        await websocket.send_json({"type": "ai_response", "text": response_text})
                        await bridge.send_command("SAY", response_text)

                    # Command: Normal Mode
                    elif "normal" in lower_text or "relax" in lower_text:
                        print("🤖 Intent Detected: NORMAL")
                        waiting_for_age = False
                        brain.set_mode("normal")
                        await bridge.send_command("LED", "GREEN")
                        response_text = "Returning to Normal Mode. Systems green."
                        await websocket.send_json({"type": "ai_response", "text": response_text})
                        await bridge.send_command("SAY", response_text)

                    # No Command? Just Chat.
                    else:
                        ai_response = brain.process_user_input(text)
                        print(f"💡 AI Says: {ai_response}")
                        await websocket.send_json({"type": "ai_response", "text": ai_response})
                        await bridge.send_command("SAY", ai_response)

            # CASE B: Text / JSON (Frontend Buttons)
            elif "text" in data:
                raw_text = data["text"]
                print(f"📩 Received: {raw_text}")

                try:
                    # Attempt to parse as JSON
                    message = json.loads(raw_text)

                    if message.get("type") == "command":
                        cmd_type = message.get("command")
                        val = message.get("value")

                        if cmd_type:
                            # Hardware/Mode Actions from Buttons
                            if cmd_type == "study_mode":
                                waiting_for_age = False
                                await bridge.send_command("LED", "BLUE")
                                brain.set_mode("study")
                            elif cmd_type == "trigger_alarm":
                                waiting_for_age = False
                                await bridge.send_command("BUZZER", "ON")
                                await bridge.send_command("LED", "RED_BLINK")
                                brain.set_mode("alarm")
                                await websocket.send_json({"type": "alert", "message": "MANUAL ALARM TRIGGERED"})
                            elif cmd_type == "normal_mode":
                                waiting_for_age = False
                                await bridge.send_command("LED", "GREEN")
                                brain.set_mode("normal")
                            elif cmd_type == "privacy_mode":
                                waiting_for_age = False
                                await bridge.send_command("LED", "OFF")
                                brain.set_mode("privacy")

                            # Note: If you add a "Child Mode" button later, handle it here too

                        await websocket.send_json({"status": "ack", "msg": "Command Executed"})

                except json.JSONDecodeError:
                    # Plain text chat fallback
                    ai_response = brain.process_user_input(raw_text)
                    await websocket.send_json({"type": "ai_response", "text": ai_response})

    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
        print(f"❌ Client Disconnected")
    except Exception as e:
        print(f"⚠️ WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)