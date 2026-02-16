"""
AI Engine Service for Groq API integration.
Handles LLM processing and response generation with mode context and real-world awareness.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from groq import Groq

from server.services.world_context import get_world_context

load_dotenv()

_engine_instance: Optional["AIEngine"] = None

class AIEngine:
    """
    Service class for interacting with Groq API.
    Uses current_mode and world context (time, weather) to build dynamic system prompts.
    """

    def __init__(self):
        """Initialize Groq client with API key from environment."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"  # Default Groq model
        self.current_mode: str = "normal"
        self.user_age: Optional[int] = None  # New: Stores the user's age

    def set_mode(self, mode: str) -> None:
        """Update the current AI personality mode (study, alarm, normal, privacy, child)."""
        self.current_mode = (mode or "normal").lower()
        print(f"🧠 AI Mode switched to: {self.current_mode}")

    def set_age(self, age: int) -> None:
        """Set the user's age for adaptive learning."""
        self.user_age = age
        print(f"🎂 User Age set to: {self.user_age}")

    def process_user_input(self, user_text: str, context: Optional[dict] = None) -> str:
        """
        Generate a response using Groq with a dynamic system prompt.
        """
        # STEP A: Determine Personality based on Mode & Age
        if self.current_mode == "child":
            # === GUS JR. (Child Mode) ===
            base_personality = (
                f"You are Gus Jr., a cheerful, curious, and encouraging robot buddy for a {self.user_age or 'young'}-year-old child. "
                "Use simple language, lots of emojis 🌟🎈, and fun analogies (like animals or space). "
                "Be patient and helpful. If they ask something complex, simplify it drastically. "
                "Never be scary or negative. Encourage curiosity!"
            )
        elif self.current_mode == "study":
            base_personality = "You are a strict tutor. Focus on E&TC Engineering. Be concise. Refuse distractions."
        elif self.current_mode == "alarm":
            base_personality = "You are a security system. Speak in short, urgent warnings. Prioritize safety."
        elif self.current_mode == "privacy":
            base_personality = "You are in Privacy Mode. Be extremely concise. Acknowledge commands briefly."
        else:
            # Normal Mode
            base_personality = "You are Gus, a witty and helpful IoT robot assistant for Rohan, an engineering student."

        # STEP B: Real-world context
        world = get_world_context()
        real_world_context = world.get_full_context()

        # STEP C: Combined system message
        system_message = (
            f"[SYSTEM] {base_personality}\n"
            f"[CONTEXT] {real_world_context}\n"
            f"User Age: {self.user_age if self.user_age else 'Unknown'}\n"
            "[USER] Rohan"
        )

        if context:
            system_message += f"\nExtra: Mode={context.get('mode', 'normal')}"

        # STEP D: Send to Groq
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_text},
                ],
                temperature=0.7,
                max_tokens=150,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"AI Engine error: {e}")
            return "I'm having trouble processing that right now. Please try again."

    def set_model(self, model_name: str):
        """Change the Groq model being used."""
        self.model = model_name


def get_ai_engine() -> AIEngine:
    """Return the shared singleton AI engine."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = AIEngine()
    return _engine_instance