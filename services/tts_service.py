import os
import asyncio
import requests
from typing import Optional
from elevenlabs import ElevenLabs

class TTSService:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.service = os.getenv("TTS_SERVICE", "elevenlabs")
        self.default_voice_id = os.getenv("TTS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        
        if self.api_key:
            self.client = ElevenLabs(api_key=self.api_key)
        else:
            self.client = None
    
    async def generate_speech(self, text: str, target_language: str, job_id: str) -> str:
        """Generate speech from text using ElevenLabs TTS"""
        try:
            if not text or not text.strip():
                raise Exception("No text provided for speech generation")
            
            if not self.api_key:
                raise Exception("ElevenLabs API key not configured")
            
            # Create output directory
            output_dir = os.path.join(os.getenv("OUTPUT_DIR", "./outputs"), job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Run TTS generation in executor
            loop = asyncio.get_event_loop()
            audio_path = await loop.run_in_executor(
                None, self._generate_speech_sync, text, target_language, output_dir
            )
            
            return audio_path
            
        except Exception as e:
            raise Exception(f"Speech generation failed: {str(e)}")
    
    def _generate_speech_sync(self, text: str, target_language: str, output_dir: str) -> str:
        """Synchronous speech generation using ElevenLabs"""
        try:
            # Select appropriate voice based on language
            voice_id = self._get_voice_for_language(target_language)
            
            # Generate audio using the new API
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2"
            )
            
            # Save audio file
            output_path = os.path.join(output_dir, "dubbed_audio.mp3")
            with open(output_path, "wb") as f:
                # Handle both bytes and generator responses
                if hasattr(audio, '__iter__') and not isinstance(audio, bytes):
                    # If it's a generator, read all chunks
                    audio_data = b''.join(audio)
                    f.write(audio_data)
                else:
                    # If it's already bytes
                    f.write(audio)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"ElevenLabs TTS error: {str(e)}")
    
    def _get_voice_for_language(self, language: str) -> str:
        """Get appropriate voice ID for the target language"""
        # Language to voice mapping for ElevenLabs
        voice_mapping = {
            "en": "21m00Tcm4TlvDq8ikWAM",  # Rachel - English
            "es": "ErXwobaYiN019PkySvjV",  # Antoni - Spanish
            "fr": "yoZ06aMxZJJ28mfd3POQ",  # Josh - French
            "de": "AZnzlk1XvdvUeBnXmlld",  # Domi - German
            "it": "EXAVITQu4vr4xnSDxMaL",  # Bella - Italian
            "pt": "VR6AewLTigWG4xSOukaG",  # Arnold - Portuguese
            "ru": "VR6AewLTigWG4xSOukaG",  # Arnold - Russian
            "ja": "VR6AewLTigWG4xSOukaG",  # Arnold - Japanese
            "ko": "VR6AewLTigWG4xSOukaG",  # Arnold - Korean
            "zh": "VR6AewLTigWG4xSOukaG",  # Arnold - Chinese
            "hi": "VR6AewLTigWG4xSOukaG",  # Arnold - Hindi
            "ar": "VR6AewLTigWG4xSOukaG",  # Arnold - Arabic
        }
        
        # Get the base language code (e.g., 'en' from 'en-US')
        base_language = language.split('-')[0].lower()
        
        return voice_mapping.get(base_language, self.default_voice_id)
    
    async def get_available_voices(self) -> list:
        """Get list of available voices from ElevenLabs"""
        try:
            if not self.api_key:
                return []
            
            # Run API call in executor
            loop = asyncio.get_event_loop()
            voices = await loop.run_in_executor(
                None, self._get_voices_sync
            )
            
            return voices
            
        except Exception as e:
            print(f"Failed to get voices: {e}")
            return []
    
    def _get_voices_sync(self) -> list:
        """Synchronous API call to get available voices"""
        try:
            if not self.client:
                return []
            
            voices = self.client.voices.get_all()
            return voices
            
        except Exception as e:
            print(f"Error fetching voices: {e}")
            return []
    
    async def generate_speech_with_timing(self, segments: list, target_language: str, job_id: str) -> str:
        """Generate speech for segments with timing information"""
        try:
            if not segments:
                raise Exception("No segments provided for speech generation")
            
            # Create output directory
            output_dir = os.path.join(os.getenv("OUTPUT_DIR", "./outputs"), job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Run TTS generation in executor
            loop = asyncio.get_event_loop()
            audio_path = await loop.run_in_executor(
                None, self._generate_speech_with_timing_sync, segments, target_language, output_dir
            )
            
            return audio_path
            
        except Exception as e:
            raise Exception(f"Speech generation with timing failed: {str(e)}")
    
    def _generate_speech_with_timing_sync(self, segments: list, target_language: str, output_dir: str) -> str:
        """Synchronous speech generation for segments with timing"""
        try:
            from pydub import AudioSegment
            import tempfile
            
            # Select voice
            voice_id = self._get_voice_for_language(target_language)
            
            # Generate audio for each segment
            audio_segments = []
            
            for segment in segments:
                text = segment.get("translated_text", "")
                if not text.strip():
                    continue
                
                # Generate audio for this segment
                audio = self.client.text_to_speech.convert(
                    text=text,
                    voice_id=voice_id,
                    model_id="eleven_multilingual_v2"
                )
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                    # Handle both bytes and generator responses
                    if hasattr(audio, '__iter__') and not isinstance(audio, bytes):
                        # If it's a generator, read all chunks
                        audio_data = b''.join(audio)
                        temp_file.write(audio_data)
                    else:
                        # If it's already bytes
                        temp_file.write(audio)
                    temp_file.flush()
                    audio_segments.append({
                        "file": temp_file.name,
                        "start": segment.get("start", 0),
                        "end": segment.get("end", 0)
                    })
            
            # Combine audio segments with proper timing
            combined_audio = AudioSegment.silent(duration=0)
            
            for segment in audio_segments:
                # Load audio segment
                segment_audio = AudioSegment.from_mp3(segment["file"])
                
                # Calculate silence duration before this segment
                silence_duration = segment["start"] * 1000  # Convert to milliseconds
                silence = AudioSegment.silent(duration=silence_duration)
                
                # Extend combined audio with silence and segment
                combined_audio = combined_audio + silence + segment_audio
                
                # Clean up temporary file
                os.unlink(segment["file"])
            
            # Save combined audio
            output_path = os.path.join(output_dir, "dubbed_audio.mp3")
            combined_audio.export(output_path, format="mp3")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Speech generation with timing error: {str(e)}")
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages for TTS"""
        return [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "hi", "ar"
        ] 