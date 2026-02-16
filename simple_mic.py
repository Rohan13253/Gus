import asyncio
import websockets
import json
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import io

# Settings
SAMPLE_RATE = 16000
DURATION = 5  # Record for 5 seconds
SERVER_URL = "ws://127.0.0.1:8000/ws/audio"

async def send_audio():
    print(f"🔌 Connecting to {SERVER_URL}...")
    async with websockets.connect(SERVER_URL) as websocket:
        print("✅ Connected! usage: Press Enter to record.")
        
        while True:
            input("\n🎤 Press Enter to start recording (5s)...")
            print("🔴 Recording...")
            
            # Record audio
            audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
            sd.wait()
            print("✅ Recording finished. Sending...")

            # Convert to WAV bytes
            bytes_io = io.BytesIO()
            wav.write(bytes_io, SAMPLE_RATE, audio_data)
            audio_bytes = bytes_io.getvalue()

            # Send to server
            await websocket.send(audio_bytes)
            print("📨 Sent to Brain. Waiting for response...")

            # Listen for reply
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(response)
                
                if data.get("type") == "ai_response":
                    print(f"🤖 Gus says: {data.get('text')}")
                else:
                    print(f"📩 Received: {data}")
            except asyncio.TimeoutError:
                print("⚠️ No response from server (Timeout)")

if __name__ == "__main__":
    try:
        asyncio.run(send_audio())
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
