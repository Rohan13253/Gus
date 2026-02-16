#!/usr/bin/env python3
"""
Virtual Microphone - Simulates ESP32 mic using the laptop's microphone.
Press and hold SPACEBAR to record; release to send audio to the server.
Prints the AI response to the console.

Dependencies: pip install sounddevice numpy scipy websockets
"""

import asyncio
import io
import json
import sys
import time

try:
    import numpy as np
    import sounddevice as sd
    from scipy.io import wavfile
except ImportError as e:
    print("Install dependencies: pip install sounddevice numpy scipy")
    sys.exit(1)

try:
    import websockets
except ImportError:
    print("Install websockets: pip install websockets")
    sys.exit(1)

WS_URL = "ws://127.0.0.1:8000/ws/audio"
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = np.int16


def record_until_release_sync() -> bytes:
    """Synchronous version: record for 3 seconds (no keyboard). Or use keyboard if available."""
    try:
        import keyboard
        print("Press and hold SPACEBAR to record, release to send...")
        keyboard.wait("space")
        frames = []
        stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE, blocksize=1024)
        stream.start()
        while keyboard.is_pressed("space"):
            chunk, _ = stream.read(1024)
            if chunk.size:
                frames.append(chunk)
            time.sleep(0.01)
        stream.stop()
        stream.close()
        if not frames:
            return b""
        audio = np.concatenate(frames, axis=0)
    except ImportError:
        print("(Install 'keyboard' for SPACEBAR: pip install keyboard)")
        print("Recording for 3 seconds...")
        rec = sd.rec(int(3 * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE)
        sd.wait()
        audio = rec
    buf = io.BytesIO()
    wavfile.write(buf, SAMPLE_RATE, audio)
    return buf.getvalue()


async def main() -> None:
    print("Virtual Mic – connect to", WS_URL)
    print("SPACEBAR: hold to record, release to send. (If 'keyboard' not installed, each run records 3s.)\n")
    while True:
        try:
            wav_bytes = record_until_release_sync()
            if len(wav_bytes) < 100:
                print("Too short, try again.")
                continue
            async with websockets.connect(WS_URL) as ws:
                await ws.send(wav_bytes)
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=15.0)
                    data = json.loads(msg)
                    if data.get("type") == "ai_response":
                        print("Gus:", data.get("text", ""))
                    else:
                        print("Server:", data)
                except asyncio.TimeoutError:
                    print("No response in time.")
        except (websockets.exceptions.ConnectionClosed, OSError, ConnectionRefusedError) as e:
            print("Connection error:", e)
            print("Retry in 3s...")
            await asyncio.sleep(3)
        except KeyboardInterrupt:
            print("\nBye.")
            break


if __name__ == "__main__":
    asyncio.run(main())
