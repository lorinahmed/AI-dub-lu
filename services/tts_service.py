import os
import asyncio
import requests
from typing import Optional
from elevenlabs import ElevenLabs
from pydub import AudioSegment

class TTSService:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.service = os.getenv("TTS_SERVICE", "elevenlabs")
        self.default_voice_id = os.getenv("TTS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        
        if self.api_key:
            self.client = ElevenLabs(api_key=self.api_key)
        else:
            self.client = None
    
    async def generate_speech(self, text: str, target_language: str, job_id: str, gender: str = "unknown", voice_id: str = None) -> str:
        """Generate speech from text using ElevenLabs TTS with gender-based voice selection"""
        try:
            if not text or not text.strip():
                raise Exception("No text provided for speech generation")
            
            if not self.api_key:
                raise Exception("ElevenLabs API key not configured")
            
            # Create output directory
            output_dir = os.path.join(os.getenv("OUTPUT_DIR", "./outputs"), job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Run TTS generation in executor with timeout
            loop = asyncio.get_event_loop()
            try:
                audio_path = await asyncio.wait_for(
                    loop.run_in_executor(
                        None, self._generate_speech_sync, text, target_language, output_dir, gender, voice_id
                    ),
                    timeout=60.0  # 60 second timeout
                )
                return audio_path
            except asyncio.TimeoutError:
                raise Exception("TTS generation timed out after 60 seconds")
            
        except Exception as e:
            raise Exception(f"Speech generation failed: {str(e)}")
    
    def _generate_speech_sync(self, text: str, target_language: str, output_dir: str, gender: str = "unknown", voice_id: str = None) -> str:
        """Synchronous speech generation using ElevenLabs with gender-based voice selection"""
        try:
            # Use provided voice_id or select appropriate voice based on language and gender
            if not voice_id:
                voice_id = self._get_voice_for_language_and_gender(target_language, gender)
            print(f"DEBUG: Using voice_id: {voice_id} for language: {target_language}, gender: {gender}")
            
            # Choose appropriate model based on language
            # Use eleven_multilingual_v2 for most languages, but fallback to eleven_monolingual_v1 for problematic ones
            if target_language in ["hi", "ar", "zh", "ja", "ko"]:
                model_id = "eleven_monolingual_v1"  # More reliable for non-Latin scripts
            else:
                model_id = "eleven_multilingual_v2"  # Better for Latin script languages
            
            print(f"DEBUG: Using model: {model_id} for language: {target_language}")
            
            # Clean the text to remove any problematic characters
            cleaned_text = text.strip()
            if not cleaned_text:
                raise Exception("Empty text after cleaning")
            
            # Generate audio using the API
            audio = self.client.text_to_speech.convert(
                text=cleaned_text,
                voice_id=voice_id,
                model_id=model_id
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
            
            print(f"DEBUG: Audio generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"DEBUG: TTS generation error: {str(e)}")
            raise Exception(f"ElevenLabs TTS error: {str(e)}")
    
    def _get_voice_for_language_and_gender(self, language: str, gender: str = "unknown") -> str:
        """Get appropriate voice ID for the target language and gender"""
        # Language and gender to voice mapping for ElevenLabs
        voice_mapping = {
            "en": {
                "male": "ErXwobaYiN019PkySvjV",    # Antoni - English (Male)
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
                "male": "ErXwobaYiN019PkySvjV",    # Antoni - Italian (Male)
                "female": "EXAVITQu4vr4xnSDxMaL",  # Bella - Italian (Female)
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
        """Get list of available voices from ElevenLabs with timeout"""
        try:
            if not self.api_key:
                print("DEBUG: No API key available, skipping voice download")
                return []
            
            print("DEBUG: Starting to download available voices from ElevenLabs...")
            
            # Run API call in executor with timeout
            loop = asyncio.get_event_loop()
            try:
                voices = await asyncio.wait_for(
                    loop.run_in_executor(None, self._get_voices_sync),
                    timeout=30.0  # 30 second timeout
                )
                print(f"DEBUG: Successfully downloaded {len(voices)} voices from ElevenLabs")
                return voices
            except asyncio.TimeoutError:
                print("DEBUG: Timeout while downloading voices from ElevenLabs (30s)")
                return []
            
        except Exception as e:
            print(f"DEBUG: Failed to get voices: {e}")
            return []
    
    def _get_voices_sync(self) -> list:
        """Synchronous API call to get available voices"""
        try:
            if not self.client:
                print("DEBUG: No ElevenLabs client available")
                return []
            
            print("DEBUG: Making API call to ElevenLabs voices endpoint...")
            voices_response = self.client.voices.get_all()
            
            # Handle the GetVoicesResponse object properly
            if hasattr(voices_response, 'voices'):
                voices = voices_response.voices
            else:
                # If it's already a list
                voices = voices_response
            
            print(f"DEBUG: API call successful, received {len(voices)} voices")
            return voices
            
        except Exception as e:
            print(f"DEBUG: Error fetching voices from ElevenLabs API: {e}")
            return []
    
    async def generate_speech_with_timing(self, segments: list, target_language: str, job_id: str, adjust_speed: bool = False) -> str:
        """Generate speech for segments with timing information and optional speed adjustment"""
        try:
            if not segments:
                raise Exception("No segments provided for speech generation")
            
            # Create output directory
            output_dir = os.path.join(os.getenv("OUTPUT_DIR", "./outputs"), job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Run TTS generation in executor with timeout
            loop = asyncio.get_event_loop()
            try:
                audio_path = await asyncio.wait_for(
                    loop.run_in_executor(
                        None, self._generate_speech_with_timing_sync, segments, target_language, output_dir, adjust_speed
                    ),
                    timeout=120.0  # 120 second timeout for timing-aware generation
                )
                return audio_path
            except asyncio.TimeoutError:
                raise Exception("TTS generation timed out after 120 seconds")
            
        except Exception as e:
            raise Exception(f"Speech generation with timing failed: {str(e)}")
    
    def _generate_speech_with_timing_sync(self, segments: list, target_language: str, output_dir: str, adjust_speed: bool = False) -> str:
        """Synchronous speech generation for segments with timing and speed adjustment"""
        try:
            from pydub import AudioSegment
            import tempfile
            import hashlib
            import os
            
            # Create cache directory
            cache_dir = os.path.join(output_dir, "tts_cache")
            os.makedirs(cache_dir, exist_ok=True)
            
            # Generate audio for each segment
            audio_segments = []
            
            for i, segment in enumerate(segments):
                text = segment.get("translated_text", "")
                original_duration = segment.get("original_duration", 0)
                
                if not text.strip():
                    continue
                
                # Use the matched voice ID from intelligent voice matching, or fallback to generic selection
                voice_id = segment.get("matched_voice_id")
                if not voice_id:
                    voice_id = self._get_voice_for_language(target_language)
                    print(f"DEBUG: No matched voice ID for segment {i}, using fallback voice: {voice_id}")
                else:
                    print(f"DEBUG: Using matched voice ID for segment {i}: {voice_id}")
                
                # Create cache key based on text and voice
                cache_key = hashlib.md5(f"{text}_{voice_id}".encode()).hexdigest()
                cache_file = os.path.join(cache_dir, f"{cache_key}.mp3")
                
                # Check if cached audio exists
                if os.path.exists(cache_file):
                    print(f"DEBUG: Using cached TTS audio for segment {i}")
                    segment_audio = AudioSegment.from_mp3(cache_file)
                else:
                    print(f"DEBUG: Generating new TTS audio for segment {i}")
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
                        
                        # Load audio and save to cache
                        segment_audio = AudioSegment.from_mp3(temp_file.name)
                        
                        # Save to cache for future use
                        segment_audio.export(cache_file, format="mp3")
                        print(f"DEBUG: Saved TTS audio to cache: {cache_file}")
                        
                        # Clean up temporary file
                        os.unlink(temp_file.name)
                
                # Now adjust speed if needed (this doesn't affect the cached version)
                if adjust_speed and original_duration > 0:
                    print(f"DEBUG: Adjusting audio speed for segment:")
                    print(f"  Original duration: {original_duration:.1f}s")
                    print(f"  Generated duration: {len(segment_audio)/1000:.1f}s")
                    
                    segment_audio = self._adjust_audio_speed(segment_audio, original_duration)
                    print(f"  Adjusted duration: {len(segment_audio)/1000:.1f}s")
                
                audio_segments.append({
                    "audio": segment_audio,
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0)
                })
            
            # Combine audio segments with proper timing
            combined_audio = self._combine_audio_segments(audio_segments)
            
            # Save combined audio
            output_path = os.path.join(output_dir, "dubbed_audio.mp3")
            combined_audio.export(output_path, format="mp3")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Speech generation with timing error: {str(e)}")
    
    def _adjust_audio_speed(self, audio: AudioSegment, target_duration: float) -> AudioSegment:
        """Adjust audio speed to match target duration"""
        try:
            current_duration = len(audio) / 1000.0  # Convert to seconds
            
            if current_duration <= 0 or target_duration <= 0:
                return audio
            
            # Calculate speed ratio
            # If current_duration < target_duration, we need to slow down (speed_ratio < 1)
            # If current_duration > target_duration, we need to speed up (speed_ratio > 1)
            speed_ratio = current_duration / target_duration
            
            print(f"DEBUG: Speed adjustment calculation:")
            print(f"  Current duration: {current_duration:.1f}s")
            print(f"  Target duration: {target_duration:.1f}s")
            print(f"  Speed ratio: {speed_ratio:.3f}")
            
            # Limit speed adjustment to prevent unnatural speech (max ±30%)
            max_speed_adjustment = 0.30
            if speed_ratio > (1 + max_speed_adjustment):
                speed_ratio = 1 + max_speed_adjustment
                print(f"  Limited speed ratio to: {speed_ratio:.3f} (max speed up)")
            elif speed_ratio < (1 - max_speed_adjustment):
                speed_ratio = 1 - max_speed_adjustment
                print(f"  Limited speed ratio to: {speed_ratio:.3f} (max slow down)")
            
            # Apply speed adjustment - ONLY for speeding up (ratio > 1)
            if speed_ratio > 1.0:
                print(f"  Applying speed adjustment (speed up) with ratio: {speed_ratio:.3f}")
                
                # Only handle speed up (pydub works for this)
                print(f"  Input duration: {len(audio)/1000:.1f}s")
                print(f"  Target duration: {len(audio)/1000/speed_ratio:.1f}s")
                
                adjusted_audio = audio.speedup(playback_speed=speed_ratio)
                print(f"  Output duration: {len(adjusted_audio)/1000:.1f}s")
                
                return adjusted_audio
            elif speed_ratio < 1.0:
                print(f"  TTS audio is shorter than original - skipping speed adjustment")
                print(f"  Input duration: {len(audio)/1000:.1f}s")
                print(f"  Target duration: {target_duration:.1f}s")
                print(f"  Using original TTS duration (OpenAI should handle timing)")
                return audio
            else:
                print(f"  No speed adjustment needed")
            
            return audio
            
        except Exception as e:
            print(f"Audio speed adjustment failed: {str(e)}")
            return audio
            
    
    def _combine_audio_segments(self, audio_segments: list) -> AudioSegment:
        """Combine audio segments maintaining original timing by adding gaps when TTS is shorter"""
        try:
            if not audio_segments:
                # Return a short silent audio if no segments
                return AudioSegment.silent(duration=1000)  # 1 second of silence
            
            # Sort segments by start time to ensure proper order
            sorted_segments = sorted(audio_segments, key=lambda x: x.get("start", 0))
            
            # Use sequential combination with timing preservation
            combined_audio = AudioSegment.empty()
            current_position = 0
            
            for i, segment in enumerate(sorted_segments):
                if "audio" in segment:
                    audio = segment["audio"]
                    original_start = segment.get("start", 0)
                    original_end = segment.get("end", 0)
                    original_duration = original_end - original_start
                    tts_duration = len(audio) / 1000.0  # Convert to seconds
                    
                    print(f"DEBUG: Processing segment {i}:")
                    print(f"  Original timing: {original_start:.1f}s - {original_end:.1f}s (duration: {original_duration:.1f}s)")
                    print(f"  TTS duration: {tts_duration:.1f}s")
                    print(f"  Current position: {current_position:.1f}s")
                    
                    # Calculate how much gap we need to add to maintain original timing
                    if i == 0:
                        # First segment: add gap from start if needed
                        if original_start > 0:
                            gap_duration = original_start * 1000  # Convert to milliseconds
                            gap = AudioSegment.silent(duration=gap_duration)
                            combined_audio = combined_audio + gap
                            current_position = original_start
                            print(f"  Added initial gap: {original_start:.1f}s")
                    else:
                        # Subsequent segments: ensure they start at original timing
                        expected_start = original_start
                        if current_position < expected_start:
                            # Add gap to reach original start time
                            gap_duration = (expected_start - current_position) * 1000  # Convert to milliseconds
                            gap = AudioSegment.silent(duration=gap_duration)
                            combined_audio = combined_audio + gap
                            current_position = expected_start
                            print(f"  Added gap to maintain timing: {(expected_start - current_position + gap_duration/1000):.1f}s")
                        elif current_position > expected_start:
                            # TTS is longer than expected, just continue
                            print(f"  TTS longer than expected, continuing at current position")
                    
                    # Add the audio segment
                    combined_audio = combined_audio + audio
                    current_position += tts_duration
                    
                    print(f"  Final position: {current_position:.1f}s")
                    print(f"  ---")
            
            return combined_audio
            
        except Exception as e:
            print(f"Audio combination failed: {str(e)}")
            # Return a fallback silent audio
            return AudioSegment.silent(duration=1000)
    

    
    def get_supported_languages(self) -> list:
        """Get list of supported languages for TTS"""
        return [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "hi", "ar"
        ] 