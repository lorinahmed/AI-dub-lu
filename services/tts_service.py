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
    
    async def generate_speech(self, text: str, target_language: str, job_id: str, gender: str = "unknown") -> str:
        """Generate speech from text using ElevenLabs TTS with gender-based voice selection"""
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
                None, self._generate_speech_sync, text, target_language, output_dir, gender
            )
            
            return audio_path
            
        except Exception as e:
            raise Exception(f"Speech generation failed: {str(e)}")
    
    def _generate_speech_sync(self, text: str, target_language: str, output_dir: str, gender: str = "unknown") -> str:
        """Synchronous speech generation using ElevenLabs with gender-based voice selection"""
        try:
            # Select appropriate voice based on language and gender
            voice_id = self._get_voice_for_language_and_gender(target_language, gender)
            
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
    
    def _get_voice_for_language_and_gender(self, language: str, gender: str = "unknown") -> str:
        """Get appropriate voice ID for the target language and gender"""
        # Language and gender to voice mapping for ElevenLabs
        voice_mapping = {
            "en": {
                "male": "21m00Tcm4TlvDq8ikWAM",    # Rachel - English (Female)
                "female": "21m00Tcm4TlvDq8ikWAM",  # Rachel - English (Female)
                "unknown": "21m00Tcm4TlvDq8ikWAM"  # Default English voice
            },
            "es": {
                "male": "ErXwobaYiN019PkySvjV",    # Antoni - Spanish (Male)
                "female": "EXAVITQu4vr4xnSDxMaL",  # Bella - Spanish (Female)
                "unknown": "ErXwobaYiN019PkySvjV"  # Default Spanish voice
            },
            "fr": {
                "male": "yoZ06aMxZJJ28mfd3POQ",    # Josh - French (Male)
                "female": "AZnzlk1XvdvUeBnXmlld",  # Domi - French (Female)
                "unknown": "yoZ06aMxZJJ28mfd3POQ"  # Default French voice
            },
            "de": {
                "male": "AZnzlk1XvdvUeBnXmlld",    # Domi - German (Male)
                "female": "EXAVITQu4vr4xnSDxMaL",  # Bella - German (Female)
                "unknown": "AZnzlk1XvdvUeBnXmlld"  # Default German voice
            },
            "it": {
                "male": "EXAVITQu4vr4xnSDxMaL",    # Bella - Italian (Male)
                "female": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Italian (Female)
                "unknown": "EXAVITQu4vr4xnSDxMaL"  # Default Italian voice
            },
            "pt": {
                "male": "VR6AewLTigWG4xSOukaG",    # Arnold - Portuguese (Male)
                "female": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Portuguese (Female)
                "unknown": "VR6AewLTigWG4xSOukaG"  # Default Portuguese voice
            },
            "ru": {
                "male": "VR6AewLTigWG4xSOukaG",    # Arnold - Russian (Male)
                "female": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Russian (Female)
                "unknown": "VR6AewLTigWG4xSOukaG"  # Default Russian voice
            },
            "ja": {
                "male": "VR6AewLTigWG4xSOukaG",    # Arnold - Japanese (Male)
                "female": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Japanese (Female)
                "unknown": "VR6AewLTigWG4xSOukaG"  # Default Japanese voice
            },
            "ko": {
                "male": "VR6AewLTigWG4xSOukaG",    # Arnold - Korean (Male)
                "female": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Korean (Female)
                "unknown": "VR6AewLTigWG4xSOukaG"  # Default Korean voice
            },
            "zh": {
                "male": "VR6AewLTigWG4xSOukaG",    # Arnold - Chinese (Male)
                "female": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Chinese (Female)
                "unknown": "VR6AewLTigWG4xSOukaG"  # Default Chinese voice
            },
            "hi": {
                "male": "VR6AewLTigWG4xSOukaG",    # Arnold - Hindi (Male)
                "female": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Hindi (Female)
                "unknown": "VR6AewLTigWG4xSOukaG"  # Default Hindi voice
            },
            "ar": {
                "male": "VR6AewLTigWG4xSOukaG",    # Arnold - Arabic (Male)
                "female": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Arabic (Female)
                "unknown": "VR6AewLTigWG4xSOukaG"  # Default Arabic voice
            }
        }
        
        # Get the base language code (e.g., 'en' from 'en-US')
        base_language = language.split('-')[0].lower()
        
        # Get gender-specific voice mapping
        language_voices = voice_mapping.get(base_language, {})
        voice_id = language_voices.get(gender, language_voices.get("unknown", self.default_voice_id))
        
        return voice_id
    
    def _get_voice_for_language(self, language: str) -> str:
        """Get appropriate voice ID for the target language (backward compatibility)"""
        return self._get_voice_for_language_and_gender(language, "unknown")
    
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