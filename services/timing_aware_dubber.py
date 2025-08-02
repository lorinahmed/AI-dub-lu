import os
import asyncio
import json
import re
from typing import List, Dict, Optional, Tuple
import openai
from pydub import AudioSegment
import tempfile
import numpy as np

class TimingAwareDubber:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.words_per_minute = 150  # Average speaking rate
        self.max_speed_adjustment = 0.30  # Maximum 30% speed adjustment
        
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    async def dub_with_timing_awareness(
        self, 
        segments: List[Dict], 
        target_language: str, 
        job_id: str,
        source_language: Optional[str] = None
    ) -> str:
        """
        Dub audio with timing awareness to match original dialogue length
        """
        try:
            print(f"Starting timing-aware dubbing for {len(segments)} segments")
            
            # Create output directory
            output_dir = os.path.join(os.getenv("OUTPUT_DIR", "./outputs"), job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Step 1: Timing-aware translation
            translated_segments = await self._translate_with_timing_constraints(
                segments, target_language, source_language
            )
            
            # Step 2: Generate TTS with speed adjustment
            dubbed_audio_path = await self._generate_timed_speech(
                translated_segments, target_language, output_dir
            )
            
            return dubbed_audio_path
            
        except Exception as e:
            raise Exception(f"Timing-aware dubbing failed: {str(e)}")
    
    async def _translate_with_timing_constraints(
        self, 
        segments: List[Dict], 
        target_language: str,
        source_language: Optional[str] = None
    ) -> List[Dict]:
        """
        Translate segments with timing constraints using GPT
        """
        try:
            translated_segments = []
            
            for segment in segments:
                original_text = segment.get("text", "").strip()
                original_duration = segment.get("end", 0) - segment.get("start", 0)
                
                if not original_text:
                    continue
                
                # Calculate target word count based on duration
                target_word_count = self._calculate_target_word_count(original_duration)
                
                # Translate with timing constraint
                translated_text = await self._gpt_timing_aware_translation(
                    original_text, 
                    target_language, 
                    target_word_count,
                    source_language
                )
                
                # Create translated segment
                translated_segment = {
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "original_text": original_text,
                    "translated_text": translated_text,
                    "original_duration": original_duration,
                    "target_word_count": target_word_count,
                    "words": segment.get("words", [])
                }
                
                translated_segments.append(translated_segment)
            
            return translated_segments
            
        except Exception as e:
            raise Exception(f"Timing-aware translation failed: {str(e)}")
    
    def _calculate_target_word_count(self, duration: float) -> int:
        """
        Calculate target word count based on duration and speaking rate
        """
        # Convert duration to minutes and calculate words
        duration_minutes = duration / 60.0
        target_words = int(duration_minutes * self.words_per_minute)
        
        # Ensure minimum word count
        return max(target_words, 1)
    
    async def _gpt_timing_aware_translation(
        self, 
        text: str, 
        target_language: str, 
        target_word_count: int,
        source_language: Optional[str] = None
    ) -> str:
        """
        Use GPT for timing-aware translation
        """
        try:
            if not self.openai_api_key:
                # Fallback to simple translation without timing constraints
                return await self._fallback_translation(text, target_language, source_language)
            
            # Language name mapping
            language_names = {
                "es": "Spanish", "fr": "French", "de": "German", "it": "Italian",
                "pt": "Portuguese", "ru": "Russian", "ja": "Japanese", "ko": "Korean",
                "zh": "Chinese", "hi": "Hindi", "ar": "Arabic", "nl": "Dutch",
                "sv": "Swedish", "no": "Norwegian", "da": "Danish", "fi": "Finnish"
            }
            
            target_lang_name = language_names.get(target_language, target_language)
            
            prompt = f"""
            Translate the following text to {target_lang_name}, keeping it concise enough to be spoken in approximately {target_word_count} words (target: {target_word_count} words).

            IMPORTANT: 
            - Preserve the meaning and intent, not exact word-for-word translation
            - Keep the translation natural and conversational
            - Aim for exactly {target_word_count} words (±1 word)
            - If the original is too long, condense it while keeping key information
            - If the original is too short, expand slightly while maintaining natural flow

            Original text: "{text}"

            Translation ({target_lang_name}):
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional translator specializing in timing-aware translations for dubbing."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            # Clean up the response
            translated_text = re.sub(r'^["\']|["\']$', '', translated_text)
            
            return translated_text
            
        except Exception as e:
            print(f"GPT translation failed, using fallback: {str(e)}")
            return await self._fallback_translation(text, target_language, source_language)
    
    async def _fallback_translation(self, text: str, target_language: str, source_language: Optional[str] = None) -> str:
        """
        Fallback translation using Google Translate
        """
        try:
            from googletrans import Translator
            translator = Translator()
            
            result = await translator.translate(
                text, 
                dest=target_language, 
                src=source_language
            )
            
            return result.text
            
        except Exception as e:
            raise Exception(f"Fallback translation failed: {str(e)}")
    
    async def _generate_timed_speech(
        self, 
        segments: List[Dict], 
        target_language: str, 
        output_dir: str
    ) -> str:
        """
        Generate TTS with speed adjustment to match timing
        """
        try:
            from elevenlabs import ElevenLabs
            
            if not self.elevenlabs_api_key:
                raise Exception("ElevenLabs API key not configured")
            
            client = ElevenLabs(api_key=self.elevenlabs_api_key)
            
            # Get voice for language
            voice_id = self._get_voice_for_language(target_language)
            
            # Generate audio for each segment with speed adjustment
            audio_segments = []
            
            for segment in segments:
                translated_text = segment.get("translated_text", "")
                original_duration = segment.get("original_duration", 0)
                
                if not translated_text.strip():
                    continue
                
                # Generate audio for this segment
                audio = client.text_to_speech.convert(
                    text=translated_text,
                    voice_id=voice_id,
                    model_id="eleven_multilingual_v2"
                )
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                    if hasattr(audio, '__iter__') and not isinstance(audio, bytes):
                        audio_data = b''.join(audio)
                        temp_file.write(audio_data)
                    else:
                        temp_file.write(audio)
                    temp_file.flush()
                    
                    # Load audio and calculate speed adjustment
                    segment_audio = AudioSegment.from_mp3(temp_file.name)
                    adjusted_audio = self._adjust_audio_speed(segment_audio, original_duration)
                    
                    audio_segments.append({
                        "audio": adjusted_audio,
                        "start": segment.get("start", 0),
                        "end": segment.get("end", 0)
                    })
                    
                    # Clean up temp file
                    os.unlink(temp_file.name)
            
            # Combine all audio segments with proper timing
            combined_audio = self._combine_audio_segments(audio_segments)
            
            # Save final audio
            output_path = os.path.join(output_dir, "timing_aware_dubbed_audio.mp3")
            combined_audio.export(output_path, format="mp3")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Timed speech generation failed: {str(e)}")
    
    def _adjust_audio_speed(self, audio: AudioSegment, target_duration: float) -> AudioSegment:
        """
        Adjust audio speed to match target duration
        """
        try:
            current_duration = len(audio) / 1000.0  # Convert to seconds
            
            if current_duration <= 0 or target_duration <= 0:
                return audio
            
            # Calculate speed ratio
            speed_ratio = current_duration / target_duration
            
            # Limit speed adjustment to prevent unnatural speech
            if speed_ratio > (1 + self.max_speed_adjustment):
                speed_ratio = 1 + self.max_speed_adjustment
            elif speed_ratio < (1 - self.max_speed_adjustment):
                speed_ratio = 1 - self.max_speed_adjustment
            
            # Apply speed adjustment
            if speed_ratio != 1.0:
                # Use pydub's speedup/slowdown methods
                if speed_ratio > 1.0:
                    # Speed up
                    adjusted_audio = audio.speedup(playback_speed=speed_ratio)
                else:
                    # Slow down
                    adjusted_audio = audio.speedup(playback_speed=speed_ratio)
                
                return adjusted_audio
            
            return audio
            
        except Exception as e:
            print(f"Audio speed adjustment failed: {str(e)}")
            return audio
    
    def _combine_audio_segments(self, audio_segments: List[Dict]) -> AudioSegment:
        """
        Combine audio segments with proper timing
        """
        try:
            # Find total duration
            total_duration = max([seg["end"] for seg in audio_segments]) if audio_segments else 0
            
            # Create silent audio track
            combined_audio = AudioSegment.silent(duration=total_duration * 1000)  # Convert to milliseconds
            
            # Overlay each segment at its correct timestamp
            for segment in audio_segments:
                start_time = segment["start"] * 1000  # Convert to milliseconds
                audio = segment["audio"]
                
                # Overlay the audio segment
                combined_audio = combined_audio.overlay(audio, position=start_time)
            
            return combined_audio
            
        except Exception as e:
            raise Exception(f"Audio combination failed: {str(e)}")
    
    def _get_voice_for_language(self, language: str) -> str:
        """
        Get appropriate voice ID for the target language
        """
        # Default voice mapping for ElevenLabs
        voice_mapping = {
            "en": "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "es": "21m00Tcm4TlvDq8ikWAM",  # Rachel (multilingual)
            "fr": "21m00Tcm4TlvDq8ikWAM",  # Rachel (multilingual)
            "de": "21m00Tcm4TlvDq8ikWAM",  # Rachel (multilingual)
            "it": "21m00Tcm4TlvDq8ikWAM",  # Rachel (multilingual)
            "pt": "21m00Tcm4TlvDq8ikWAM",  # Rachel (multilingual)
            "ru": "21m00Tcm4TlvDq8ikWAM",  # Rachel (multilingual)
            "ja": "21m00Tcm4TlvDq8ikWAM",  # Rachel (multilingual)
            "ko": "21m00Tcm4TlvDq8ikWAM",  # Rachel (multilingual)
            "zh": "21m00Tcm4TlvDq8ikWAM",  # Rachel (multilingual)
            "hi": "21m00Tcm4TlvDq8ikWAM",  # Rachel (multilingual)
            "ar": "21m00Tcm4TlvDq8ikWAM",  # Rachel (multilingual)
        }
        
        return voice_mapping.get(language, "21m00Tcm4TlvDq8ikWAM")  # Default to Rachel 