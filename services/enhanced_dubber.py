import os
import asyncio
import numpy as np
import librosa
from typing import List, Dict, Tuple
from dataclasses import dataclass
from services.transcriber import Transcriber
from services.translator import Translator
from services.tts_service import TTSService
from services.gender_detector import GenderDetector

@dataclass
class AudioSegment:
    """Represents a segment of audio with speaker and timing information"""
    start_time: float
    end_time: float
    text: str
    speaker_id: str
    gender: str = "unknown"
    confidence: float = 0.0

class EnhancedDubber:
    def __init__(self):
        self.transcriber = Transcriber()
        self.translator = Translator()
        self.tts_service = TTSService()
        self.gender_detector = GenderDetector()
    
    async def dub_with_speaker_diarization(self, audio_path: str, target_language: str, job_id: str) -> str:
        """Enhanced dubbing with speaker diarization and per-segment gender detection"""
        try:
            # Step 1: Transcribe with timestamps and speaker diarization
            segments = await self._transcribe_with_diarization(audio_path)
            
            # Step 2: Detect gender for each segment
            segments = await self._detect_gender_per_segment(segments, audio_path)
            
            # Step 3: Translate each segment
            segments = await self._translate_segments(segments, target_language)
            
            # Step 4: Generate speech for each segment with appropriate voice
            dubbed_audio_path = await self._generate_segmented_speech(segments, target_language, job_id)
            
            return dubbed_audio_path
            
        except Exception as e:
            raise Exception(f"Enhanced dubbing failed: {str(e)}")
    
    async def _transcribe_with_diarization(self, audio_path: str) -> List[AudioSegment]:
        """Transcribe audio with speaker diarization using Whisper"""
        try:
            # Use Whisper's transcription with timestamps
            result = await self.transcriber.transcribe_with_timestamps(audio_path)
            
            segments = []
            for i, segment in enumerate(result['segments']):
                audio_segment = AudioSegment(
                    start_time=segment['start'],
                    end_time=segment['end'],
                    text=segment['text'].strip(),
                    speaker_id=f"speaker_{i}",  # Placeholder - would use actual diarization
                    confidence=segment.get('confidence', 0.0)
                )
                segments.append(audio_segment)
            
            print(f"DEBUG: Transcribed {len(segments)} segments")
            return segments
            
        except Exception as e:
            raise Exception(f"Transcription with diarization failed: {str(e)}")
    
    async def _detect_gender_per_segment(self, segments: List[AudioSegment], audio_path: str) -> List[AudioSegment]:
        """Detect gender for each audio segment"""
        try:
            # Load the full audio file
            y, sr = librosa.load(audio_path, sr=None)
            
            for segment in segments:
                # Extract the segment audio
                start_sample = int(segment.start_time * sr)
                end_sample = int(segment.end_time * sr)
                segment_audio = y[start_sample:end_sample]
                
                # Save segment to temporary file for gender detection
                temp_segment_path = f"/tmp/segment_{segment.speaker_id}_{segment.start_time}.wav"
                librosa.output.write_wav(temp_segment_path, segment_audio, sr)
                
                # Detect gender for this segment
                gender = await self.gender_detector.detect_gender_from_audio(temp_segment_path)
                segment.gender = gender
                
                print(f"DEBUG: Segment {segment.speaker_id} ({segment.start_time:.2f}s-{segment.end_time:.2f}s): {gender}")
                
                # Clean up temp file
                os.remove(temp_segment_path)
            
            return segments
            
        except Exception as e:
            raise Exception(f"Per-segment gender detection failed: {str(e)}")
    
    async def _translate_segments(self, segments: List[AudioSegment], target_language: str) -> List[AudioSegment]:
        """Translate each segment to target language"""
        try:
            for segment in segments:
                if segment.text.strip():
                    translated_text = await self.translator.translate(segment.text, target_language)
                    segment.text = translated_text
                    print(f"DEBUG: Translated segment {segment.speaker_id}: {segment.text[:50]}...")
            
            return segments
            
        except Exception as e:
            raise Exception(f"Segment translation failed: {str(e)}")
    
    async def _generate_segmented_speech(self, segments: List[AudioSegment], target_language: str, job_id: str) -> str:
        """Generate speech for each segment with appropriate voice"""
        try:
            # Create output directory
            output_dir = os.path.join(os.getenv("OUTPUT_DIR", "./outputs"), job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate speech for each segment
            audio_files = []
            for i, segment in enumerate(segments):
                if segment.text.strip():
                    # Generate speech with gender-matched voice
                    segment_audio_path = await self.tts_service.generate_speech(
                        segment.text, target_language, job_id, segment.gender
                    )
                    
                    # Add timing information
                    audio_files.append({
                        'path': segment_audio_path,
                        'start_time': segment.start_time,
                        'end_time': segment.end_time,
                        'duration': segment.end_time - segment.start_time
                    })
                    
                    print(f"DEBUG: Generated speech for segment {i} with {segment.gender} voice")
            
            # Combine all audio segments with proper timing
            final_audio_path = await self._combine_audio_segments(audio_files, output_dir)
            
            return final_audio_path
            
        except Exception as e:
            raise Exception(f"Segmented speech generation failed: {str(e)}")
    
    async def _combine_audio_segments(self, audio_files: List[Dict], output_dir: str) -> str:
        """Combine audio segments with proper timing"""
        try:
            # This is a simplified version - in production you'd use more sophisticated audio mixing
            import ffmpeg
            
            # For now, concatenate segments sequentially
            # In a full implementation, you'd maintain timing gaps and overlaps
            input_files = []
            for audio_file in audio_files:
                input_files.append(ffmpeg.input(audio_file['path']))
            
            # Concatenate all audio files
            output_path = os.path.join(output_dir, "dubbed_audio_segmented.mp3")
            
            # Use ffmpeg to concatenate
            stream = ffmpeg.concat(*input_files, v=0, a=1)
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, overwrite_output=True)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Audio segment combination failed: {str(e)}")

# Advanced speaker diarization using pyannote.audio (optional)
class SpeakerDiarizer:
    def __init__(self):
        # This would require pyannote.audio library
        # from pyannote.audio import Pipeline
        pass
    
    async def diarize_speakers(self, audio_path: str) -> List[Dict]:
        """Identify different speakers in the audio"""
        # This is a placeholder for advanced speaker diarization
        # Would use pyannote.audio or similar library
        pass 