import os
import asyncio
import whisper
from typing import Optional, List, Dict

class Transcriber:
    def __init__(self):
        self.model_name = os.getenv("WHISPER_MODEL", "base")
        self.device = os.getenv("WHISPER_DEVICE", "cpu")
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model"""
        try:
            print(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name, device=self.device)
            print("Whisper model loaded successfully")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            # Fallback to base model
            self.model = whisper.load_model("base", device=self.device)
    
    async def transcribe(self, audio_path: str, source_language: Optional[str] = None) -> str:
        """Transcribe audio file to text"""
        try:
            if not os.path.exists(audio_path):
                raise Exception(f"Audio file not found: {audio_path}")
            
            # Run transcription in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._transcribe_sync, audio_path, source_language
            )
            
            return result
            
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def _transcribe_sync(self, audio_path: str, source_language: Optional[str] = None) -> str:
        """Synchronous transcription using Whisper"""
        try:
            # Configure transcription options
            options = {
                "language": source_language if source_language else None,
                "task": "transcribe",
                "verbose": False,
            }
            
            # Transcribe the audio
            result = self.model.transcribe(audio_path, **options)
            
            # Extract the transcribed text
            transcribed_text = result.get("text", "").strip()
            
            if not transcribed_text:
                raise Exception("No text was transcribed from the audio")
            
            return transcribed_text
            
        except Exception as e:
            raise Exception(f"Whisper transcription error: {str(e)}")
    
    async def transcribe_with_timestamps(self, audio_path: str, source_language: Optional[str] = None) -> List[Dict]:
        """Transcribe audio with word-level timestamps"""
        try:
            if not os.path.exists(audio_path):
                raise Exception(f"Audio file not found: {audio_path}")
            
            # Run transcription in executor
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._transcribe_with_timestamps_sync, audio_path, source_language
            )
            
            return result
            
        except Exception as e:
            raise Exception(f"Transcription with timestamps failed: {str(e)}")
    
    def _transcribe_with_timestamps_sync(self, audio_path: str, source_language: Optional[str] = None) -> List[Dict]:
        """Synchronous transcription with timestamps"""
        try:
            # Configure transcription options
            options = {
                "language": source_language if source_language else None,
                "task": "transcribe",
                "verbose": False,
                "word_timestamps": True,
            }
            
            # Transcribe the audio
            result = self.model.transcribe(audio_path, **options)
            
            # Extract segments with timestamps
            segments = result.get("segments", [])
            
            # Format segments for easier processing
            formatted_segments = []
            for segment in segments:
                formatted_segments.append({
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "text": segment.get("text", "").strip(),
                    "words": segment.get("words", [])
                })
            
            return formatted_segments
            
        except Exception as e:
            raise Exception(f"Whisper transcription with timestamps error: {str(e)}")
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages for Whisper"""
        return [
            "af", "am", "ar", "as", "az", "ba", "be", "bg", "bn", "bo", "br", "bs", "ca", "cs", "cy", "da", "de", "el", "en", "es", "et", "eu", "fa", "fi", "fo", "fr", "gl", "gu", "ha", "he", "hi", "hr", "ht", "hu", "hy", "id", "is", "it", "ja", "jw", "ka", "kk", "km", "kn", "ko", "la", "lb", "ln", "lo", "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "ne", "nl", "nn", "no", "oc", "pa", "pl", "ps", "pt", "ro", "ru", "sa", "sd", "si", "sk", "sl", "sn", "so", "sq", "sr", "su", "sv", "sw", "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "uk", "ur", "uz", "vi", "yi", "yo", "zh"
        ] 