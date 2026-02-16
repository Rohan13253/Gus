"""
World Context Service - Real-world awareness (time, weather) for the AI.
Singleton that provides location, time, and weather strings for system prompts.
"""

import os
from datetime import datetime
from typing import Optional

# DEBUG CHECK: See if requests is actually installed
try:
    import requests
    print("✅ Requests library loaded successfully.")
except ImportError:
    requests = None
    print("❌ ERROR: Requests library NOT found. Run 'pip install requests'.")

_instance: Optional["WorldContext"] = None

class WorldContext:
    """Singleton providing current time and weather for Pune, India."""

    def __new__(cls) -> "WorldContext":
        global _instance
        if _instance is None:
            _instance = super().__new__(cls)
        return _instance

    def get_time_string(self) -> str:
        """Return current time as e.g. 'Monday, 02:30 PM'."""
        now = datetime.now()
        return now.strftime("%A, %I:%M %p")

    def get_weather_string(self) -> str:
        """
        Return weather for Pune as e.g. '28°C, Clear Sky'.
        If OPENWEATHER_API_KEY is missing or request fails, return a safe message.
        """
        api_key = os.getenv("OPENWEATHER_API_KEY")

        # DEBUG PRINTS
        if not api_key:
            print("⚠️ DEBUG: API Key is MISSING in .env file.")
            return "Weather data unavailable (Missing Key)"

        if requests is None:
            print("⚠️ DEBUG: Requests library is missing.")
            return "Weather data unavailable (Missing Library)"

        try:
            print(f"🌍 DEBUG: Requesting weather for Pune with Key: {api_key[:5]}...") # Print first 5 chars only

            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {"q": "Pune", "appid": api_key, "units": "metric"}

            r = requests.get(url, params=params, timeout=5)

            if r.status_code != 200:
                print(f"❌ DEBUG: API Error {r.status_code}: {r.text}")
                return "Weather data unavailable (API Error)"

            data = r.json()
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"].title()

            result = f"{temp}°C, {desc}"
            print(f"✅ DEBUG: Weather Success! {result}")
            return result

        except Exception as e:
            print(f"❌ DEBUG: Crash inside get_weather_string: {e}")
            return "Weather data unavailable (Crash)"

    def get_full_context(self) -> str:
        """Combine location, time, and weather into one context string."""
        time_str = self.get_time_string()
        weather_str = self.get_weather_string()
        return f"Location: Pune, India. Time: {time_str}. Weather: {weather_str}."

def get_world_context() -> WorldContext:
    """Return the shared WorldContext singleton."""
    return WorldContext()