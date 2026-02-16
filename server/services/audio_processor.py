"""
Audio Processor Service for handling raw PCM audio streams.
Processes audio bytes from ESP32 and prepares for transcription.
"""

import numpy as np
from typing import Optional, Tuple
import struct


class AudioProcessor:
    """
    Handles raw PCM audio byte streams from ESP32.
    Converts bytes to audio samples and prepares for speech-to-text.
    """
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1, bit_depth: int = 16):
        """
        Initialize audio processor with ESP32 audio parameters.
        
        Args:
            sample_rate: Audio sample rate in Hz (default 16000)
            channels: Number of audio channels (default 1 = mono)
            bit_depth: Bit depth per sample (default 16)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.bit_depth = bit_depth
        self.bytes_per_sample = bit_depth // 8
    
    def bytes_to_audio_array(self, audio_bytes: bytes) -> np.ndarray:
        """
        Convert raw PCM bytes to numpy audio array.
        
        Args:
            audio_bytes: Raw PCM audio bytes from ESP32
        
        Returns:
            Numpy array of audio samples (normalized to [-1, 1])
        """
        # Unpack bytes as 16-bit signed integers
        samples = struct.unpack(f"<{len(audio_bytes) // self.bytes_per_sample}h", audio_bytes)
        
        # Convert to numpy array and normalize to [-1, 1]
        audio_array = np.array(samples, dtype=np.float32) / 32768.0
        
        return audio_array
    
    def detect_silence(self, audio_array: np.ndarray, threshold: float = 0.01) -> bool:
        """
        Detect if audio array contains mostly silence.
        
        Args:
            audio_array: Audio samples array
            threshold: RMS threshold for silence detection
        
        Returns:
            True if audio is mostly silence
        """
        rms = np.sqrt(np.mean(audio_array ** 2))
        return rms < threshold
    
    def process_audio_chunk(self, audio_bytes: bytes) -> Tuple[np.ndarray, dict]:
        """
        Process a chunk of audio bytes.
        
        Args:
            audio_bytes: Raw PCM audio bytes
        
        Returns:
            Tuple of (audio_array, metadata_dict)
        """
        audio_array = self.bytes_to_audio_array(audio_bytes)
        
        metadata = {
            "duration": len(audio_array) / self.sample_rate,
            "is_silence": self.detect_silence(audio_array),
            "rms_level": float(np.sqrt(np.mean(audio_array ** 2)))
        }
        
        return audio_array, metadata
    
    def prepare_for_transcription(self, audio_array: np.ndarray) -> bytes:
        """
        Prepare audio array for speech-to-text API (if needed).
        Converts back to PCM format expected by transcription service.
        
        Args:
            audio_array: Normalized audio array
        
        Returns:
            PCM bytes ready for transcription API
        """
        # Denormalize and convert back to 16-bit integers
        samples_int16 = (audio_array * 32768.0).astype(np.int16)
        
        # Pack back to bytes
        return struct.pack(f"<{len(samples_int16)}h", *samples_int16.tolist())
