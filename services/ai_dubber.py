import os
import asyncio
import numpy as np
import librosa
import whisper
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import json
from services.transcriber import Transcriber
from services.translator import Translator
from services.tts_service import TTSService
from services.gender_detector import GenderDetector

@dataclass
class SpeakerSegment:
    """Represents a segment with speaker and AI analysis"""
    start_time: float
    end_time: float
    text: str
    speaker_id: str
    gender: str = "unknown"
    confidence: float = 0.0
    emotion: str = "neutral"
    voice_characteristics: Dict = None
    language: str = "en"

class AIDubber:
    def __init__(self):
        self.transcriber = Transcriber()
        self.translator = Translator()
        self.tts_service = TTSService()
        self.gender_detector = GenderDetector()
        self.whisper_model = whisper.load_model("base")
        print("DEBUG: Using fallback speaker detection (PyAnnote removed)")
        
    async def dub_with_ai_analysis(self, audio_path: str, target_language: str, job_id: str) -> str:
        """AI-powered dubbing with speaker diarization and intelligent voice matching"""
        try:
            print(f"DEBUG: Starting AI-powered dubbing for job {job_id}")
            
            # Step 1: AI-powered transcription with speaker diarization
            segments = await self._ai_transcribe_with_speakers(audio_path)
            
            # Step 2: AI analysis of each speaker segment
            segments = await self._analyze_speakers_ai(segments, audio_path)
            
            # Step 3: Intelligent voice matching per speaker
            segments = await self._match_voices_intelligently(segments, target_language)
            
            # Step 4: Translate with context preservation
            segments = await self._translate_with_context(segments, target_language)
            
            # Step 5: Generate AI-enhanced speech
            dubbed_audio_path = await self._generate_ai_speech(segments, target_language, job_id)
            
            return dubbed_audio_path
            
        except Exception as e:
            raise Exception(f"AI dubbing failed: {str(e)}")
    
    async def _ai_transcribe_with_speakers(self, audio_path: str) -> List[SpeakerSegment]:
        """AI-powered transcription with fallback speaker detection"""
        try:
            print(f"DEBUG: Starting AI transcription with fallback speaker detection")
            
            # Step 1: Use Whisper for transcription
            result = self.whisper_model.transcribe(
                audio_path,
                verbose=True,
                word_timestamps=True,
                language="en"
            )
            print("-----------------Whisper result----------------- ")
            print(result)
            
            # Step 2: Create simple speaker segments (fallback approach)
            segments = self._create_fallback_speaker_segments(result['segments'])
            
            print(f"DEBUG: Created {len(segments)} segments with fallback speaker detection")
            return segments
            
        except Exception as e:
            raise Exception(f"AI transcription failed: {str(e)}")
    
    def _create_fallback_speaker_segments(self, whisper_segments: List[Dict]) -> List[SpeakerSegment]:
        """Create speaker segments using a simple fallback approach"""
        try:
            segments = []
            
            # Simple approach: alternate between speakers based on segment duration
            # This is a basic fallback when PyAnnote is not available
            current_speaker = 0
            
            for i, segment in enumerate(whisper_segments):
                segment_start = segment['start']
                segment_end = segment['end']
                
                # Alternate speakers every few segments or based on duration
                if i > 0 and (segment_start - whisper_segments[i-1]['end']) > 2.0:  # Gap > 2 seconds
                    current_speaker = (current_speaker + 1) % 2  # Alternate between 2 speakers
                
                speaker_id = f"SPEAKER_{current_speaker:02d}"
                
                # Create speaker segment
                speaker_segment = SpeakerSegment(
                    start_time=segment_start,
                    end_time=segment_end,
                    text=segment['text'].strip(),
                    speaker_id=speaker_id,
                    confidence=segment.get('confidence', 0.0),
                    voice_characteristics={}
                )
                
                segments.append(speaker_segment)
                print(f"DEBUG: Segment {i}: Speaker {speaker_id}, Text: {segment['text'][:50]}...")
            
            return segments
            
        except Exception as e:
            print(f"Fallback speaker detection error: {e}")
            # Ultimate fallback: assign all segments to single speaker
            segments = []
            for i, segment in enumerate(whisper_segments):
                speaker_segment = SpeakerSegment(
                    start_time=segment['start'],
                    end_time=segment['end'],
                    text=segment['text'].strip(),
                    speaker_id='SPEAKER_00',
                    confidence=segment.get('confidence', 0.0),
                    voice_characteristics={}
                )
                segments.append(speaker_segment)
            return segments
    

    
    async def _analyze_speakers_ai(self, segments: List[SpeakerSegment], audio_path: str) -> List[SpeakerSegment]:
        """AI analysis of each speaker's characteristics"""
        try:
            print(f"DEBUG: Starting AI speaker analysis")
            
            # Load audio for analysis
            y, sr = librosa.load(audio_path, sr=None)
            
            # Group segments by speaker for analysis
            speaker_groups = defaultdict(list)
            for segment in segments:
                speaker_groups[segment.speaker_id].append(segment)
            
            # Analyze each speaker's characteristics
            for speaker_id, speaker_segments in speaker_groups.items():
                print(f"DEBUG: Analyzing speaker {speaker_id} with {len(speaker_segments)} segments")
                
                # Analyze first few segments of this speaker
                analysis_segments = speaker_segments[:3]  # Analyze first 3 segments
                
                detected_genders = []
                
                for segment in analysis_segments:
                    try:
                        # Extract segment audio
                        start_sample = int(segment.start_time * sr)
                        end_sample = int(segment.end_time * sr)
                        segment_audio = y[start_sample:end_sample]
                        
                        # Skip if segment is too short
                        if len(segment_audio) < sr * 0.5:  # Less than 0.5 seconds
                            continue
                        
                        # AI analysis of voice characteristics
                        characteristics = await self._analyze_voice_characteristics(segment_audio, sr)
                        segment.voice_characteristics = characteristics
                        
                        # Detect gender using the existing gender detector directly
                        temp_path = f"/tmp/segment_{speaker_id}_{segment.start_time}_{np.random.randint(1000, 9999)}.wav"
                        import soundfile as sf
                        
                        # Ensure audio is in the correct format
                        if segment_audio.dtype != np.float32:
                            segment_audio = segment_audio.astype(np.float32)
                        
                        # Normalize audio to prevent clipping
                        if np.max(np.abs(segment_audio)) > 1.0:
                            segment_audio = segment_audio / np.max(np.abs(segment_audio))
                        
                        sf.write(temp_path, segment_audio, sr)
                        
                        gender = await self.gender_detector.detect_gender_from_audio(temp_path)
                        segment.gender = gender
                        detected_genders.append(gender)
                        
                        # Clean up temp file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        
                        # Detect emotion
                        emotion = await self._detect_emotion_ai(segment_audio, sr, characteristics)
                        segment.emotion = emotion
                        
                        print(f"DEBUG: Speaker {speaker_id} - Gender: {gender}, Emotion: {emotion}")
                        
                    except Exception as e:
                        print(f"DEBUG: Error analyzing segment for speaker {speaker_id}: {e}")
                        # Clean up temp file if it exists
                        if 'temp_path' in locals() and os.path.exists(temp_path):
                            os.remove(temp_path)
                        continue
                
                # Assign the most common gender to all segments of this speaker
                if detected_genders:
                    dominant_gender = max(set(detected_genders), key=detected_genders.count)
                    for segment in speaker_segments:
                        segment.gender = dominant_gender
                    print(f"DEBUG: Speaker {speaker_id} dominant gender: {dominant_gender}")
            
            return segments
            
        except Exception as e:
            raise Exception(f"AI speaker analysis failed: {str(e)}")
    
    async def _analyze_voice_characteristics(self, audio: np.ndarray, sr: int) -> Dict:
        """Analyze voice characteristics using AI/ML features"""
        try:
            characteristics = {}
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            characteristics['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            characteristics['spectral_centroid_std'] = float(np.std(spectral_centroids))
            
            # Pitch features
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr, threshold=0.1)
            pitches = pitches[magnitudes > 0.1]
            if len(pitches) > 0:
                characteristics['pitch_mean'] = float(np.mean(pitches))
                characteristics['pitch_std'] = float(np.std(pitches))
                characteristics['pitch_range'] = float(np.max(pitches) - np.min(pitches))
            
            # MFCC features (voice timbre)
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            characteristics['mfcc_mean'] = float(np.mean(mfccs))
            characteristics['mfcc_std'] = float(np.std(mfccs))
            
            # Speaking rate (syllables per second approximation)
            zero_crossings = librosa.feature.zero_crossing_rate(audio)[0]
            characteristics['speaking_rate'] = float(np.mean(zero_crossings))
            
            # Energy features
            rms = librosa.feature.rms(y=audio)[0]
            characteristics['energy_mean'] = float(np.mean(rms))
            characteristics['energy_std'] = float(np.std(rms))
            
            return characteristics
            
        except Exception as e:
            print(f"Voice analysis error: {e}")
            return {}
    
    async def _detect_gender_ai(self, audio: np.ndarray, sr: int, characteristics: Dict) -> str:
        """AI-enhanced gender detection using multiple features"""
        try:
            # Use the existing gender detector as base
            temp_path = f"/tmp/temp_gender_analysis_{np.random.randint(1000, 9999)}.wav"
            import soundfile as sf
            
            # Ensure audio is in the correct format
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            # Normalize audio to prevent clipping
            if np.max(np.abs(audio)) > 1.0:
                audio = audio / np.max(np.abs(audio))
            
            sf.write(temp_path, audio, sr)
            
            gender = await self.gender_detector.detect_gender_from_audio(temp_path)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Enhance with additional AI features
            if characteristics:
                # Use spectral centroid and pitch for additional validation
                spectral_centroid = characteristics.get('spectral_centroid_mean', 0)
                pitch_mean = characteristics.get('pitch_mean', 0)
                
                # AI confidence scoring
                confidence_score = 0
                if spectral_centroid > 2000:
                    confidence_score += 1  # Likely female
                elif spectral_centroid < 1500:
                    confidence_score -= 1  # Likely male
                
                if pitch_mean > 200:
                    confidence_score += 1  # Likely female
                elif pitch_mean < 150:
                    confidence_score -= 1  # Likely male
                
                # Override if AI confidence is high
                if abs(confidence_score) >= 2:
                    gender = "female" if confidence_score > 0 else "male"
            
            return gender
            
        except Exception as e:
            print(f"AI gender detection error: {e}")
            # Clean up temp file if it exists
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            return "unknown"
    
    async def _detect_emotion_ai(self, audio: np.ndarray, sr: int, characteristics: Dict) -> str:
        """AI emotion detection based on voice characteristics"""
        try:
            # Simple emotion detection based on voice characteristics
            # In production, you'd use a trained emotion recognition model
            
            energy_mean = characteristics.get('energy_mean', 0)
            speaking_rate = characteristics.get('speaking_rate', 0)
            pitch_std = characteristics.get('pitch_std', 0)
            
            # Emotion classification based on features
            if energy_mean > 0.1 and speaking_rate > 0.05:
                return "excited"
            elif pitch_std > 50:
                return "emotional"
            elif energy_mean < 0.05:
                return "calm"
            else:
                return "neutral"
                
        except Exception as e:
            print(f"Emotion detection error: {e}")
            return "neutral"
    
    async def _match_voices_intelligently(self, segments: List[SpeakerSegment], target_language: str) -> List[SpeakerSegment]:
        """Intelligent voice matching based on AI analysis"""
        try:
            print(f"DEBUG: Starting intelligent voice matching")
            
            # Group by speaker and analyze patterns
            speaker_profiles = defaultdict(list)
            for segment in segments:
                speaker_profiles[segment.speaker_id].append(segment)
            
            # Create voice profiles for each speaker
            voice_profiles = {}
            for speaker_id, speaker_segments in speaker_profiles.items():
                # Analyze all segments for this speaker
                all_characteristics = [seg.voice_characteristics for seg in speaker_segments if seg.voice_characteristics]
                
                if all_characteristics:
                    # Create average profile
                    avg_profile = {}
                    for key in all_characteristics[0].keys():
                        values = [char[key] for char in all_characteristics if key in char]
                        if values:
                            avg_profile[key] = np.mean(values)
                    
                    voice_profiles[speaker_id] = avg_profile
                    
                    # Assign consistent voice based on profile
                    dominant_gender = max(set(seg.gender for seg in speaker_segments), 
                                        key=lambda x: sum(1 for seg in speaker_segments if seg.gender == x))
                    
                    for segment in speaker_segments:
                        segment.gender = dominant_gender
                    
                    print(f"DEBUG: Speaker {speaker_id} profile - Gender: {dominant_gender}, "
                          f"Pitch: {avg_profile.get('pitch_mean', 0):.1f}Hz, "
                          f"Energy: {avg_profile.get('energy_mean', 0):.3f}")
            
            return segments
            
        except Exception as e:
            raise Exception(f"Voice matching failed: {str(e)}")
    
    async def _translate_with_context(self, segments: List[SpeakerSegment], target_language: str) -> List[SpeakerSegment]:
        """Translate with context preservation for better quality"""
        try:
            print(f"DEBUG: Starting context-aware translation")
            
            # Translate each segment individually to avoid corruption
            for i, segment in enumerate(segments):
                if segment.text.strip():
                    try:
                        # Clean the text first
                        clean_text = segment.text.strip()
                        
                        # Skip if text is too short or contains corruption
                        if len(clean_text) < 2 or "Anterior:" in clean_text:
                            continue
                        
                        # Simple translation without context
                        translated_text = await self.translator.translate(clean_text, target_language)
                        
                        # Clean the translated text
                        if translated_text and not translated_text.startswith("Anterior:"):
                            segment.text = translated_text.strip()
                            print(f"DEBUG: Translated segment {i} (Speaker {segment.speaker_id}): {translated_text[:50]}...")
                        else:
                            print(f"DEBUG: Skipping corrupted translation for segment {i}")
                            
                    except Exception as e:
                        print(f"DEBUG: Translation error for segment {i}: {e}")
                        continue
            
            return segments
            
        except Exception as e:
            raise Exception(f"Context translation failed: {str(e)}")
    
    async def _generate_ai_speech(self, segments: List[SpeakerSegment], target_language: str, job_id: str) -> str:
        """Generate AI-enhanced speech with speaker-specific voices and timing"""
        try:
            print(f"DEBUG: Starting AI speech generation with per-speaker voices")
            
            # Create output directory
            output_dir = os.path.join(os.getenv("OUTPUT_DIR", "./outputs"), job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Group segments by speaker for voice consistency
            speaker_segments = defaultdict(list)
            for segment in segments:
                if segment.text.strip():
                    speaker_segments[segment.speaker_id].append(segment)
            
            # Generate separate audio for each speaker with their detected gender
            speaker_audio_files = {}
            
            for speaker_id, speaker_segments_list in speaker_segments.items():
                print(f"DEBUG: Generating audio for speaker {speaker_id}")
                
                # Combine all text for this speaker
                speaker_text = " ".join([seg.text for seg in speaker_segments_list if seg.text.strip()])
                
                # Determine gender for this speaker based on analysis
                # Use the most common gender detected for this speaker
                genders = [seg.gender for seg in speaker_segments_list if seg.gender != "unknown"]
                if genders:
                    speaker_gender = max(set(genders), key=genders.count)
                else:
                    # Fallback: use pitch analysis to determine gender
                    avg_pitch = np.mean([seg.voice_characteristics.get('pitch_mean', 0) for seg in speaker_segments_list if seg.voice_characteristics])
                    speaker_gender = "female" if avg_pitch > 150 else "male"
                
                print(f"DEBUG: Speaker {speaker_id} - Gender: {speaker_gender}, Text length: {len(speaker_text)}")
                
                # Generate speech for this speaker
                speaker_audio_path = await self.tts_service.generate_speech(
                    speaker_text, target_language, f"{job_id}_{speaker_id}", speaker_gender
                )
                
                speaker_audio_files[speaker_id] = {
                    'path': speaker_audio_path,
                    'segments': speaker_segments_list,
                    'gender': speaker_gender
                }
            
            # For now, let's use a simpler approach - just combine all audio without complex timestamp alignment
            # This will avoid the audio distortion issue
            final_audio_path = await self._combine_speaker_audio_simple(speaker_audio_files, output_dir)
            
            print(f"DEBUG: AI dubbing completed successfully")
            return final_audio_path
            
        except Exception as e:
            raise Exception(f"AI speech generation failed: {str(e)}")
    
    async def _combine_speaker_audio_simple(self, speaker_audio_files: Dict, output_dir: str) -> str:
        """Simple audio combination without complex timestamp alignment"""
        try:
            import ffmpeg
            
            print(f"DEBUG: Combining speaker audio files")
            
            # Create a simple concatenation of all speaker audio files
            output_path = os.path.join(output_dir, "dubbed_audio_combined.wav")
            
            # Get all audio file paths
            audio_paths = [data['path'] for data in speaker_audio_files.values()]
            
            if len(audio_paths) == 1:
                # If only one speaker, just copy the file
                import shutil
                shutil.copy2(audio_paths[0], output_path)
            else:
                # Combine multiple audio files with ffmpeg
                input_files = []
                for audio_path in audio_paths:
                    input_files.append(ffmpeg.input(audio_path))
                
                # Concatenate with a small gap between speakers
                stream = ffmpeg.concat(*input_files, v=0, a=1)
                stream = ffmpeg.output(stream, output_path)
                ffmpeg.run(stream, overwrite_output=True)
            
            print(f"DEBUG: Combined audio created: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Audio combination failed: {str(e)}")

    async def _create_timestamp_aligned_audio(self, segments: List[SpeakerSegment], speaker_audio_files: Dict, output_dir: str, job_id: str) -> str:
        """Create timestamp-aligned audio that matches original dialogue timing"""
        try:
            import ffmpeg
            import soundfile as sf
            import numpy as np
            
            print(f"DEBUG: Creating timestamp-aligned audio")
            
            # Get the total duration from the last segment
            total_duration = max([seg.end_time for seg in segments]) if segments else 10.0
            
            # Create a silent audio track of the total duration
            sample_rate = 22050  # Standard sample rate
            silent_audio = np.zeros(int(total_duration * sample_rate))
            
            # For each segment, insert the corresponding speaker audio at the right timestamp
            for segment in segments:
                if segment.text.strip() and segment.speaker_id in speaker_audio_files:
                    speaker_data = speaker_audio_files[segment.speaker_id]
                    
                    # Load the speaker's audio
                    speaker_audio, sr = sf.read(speaker_data['path'])
                    
                    # Resample if needed
                    if sr != sample_rate:
                        # Simple resampling (in production, use proper resampling)
                        ratio = sample_rate / sr
                        speaker_audio = np.interp(
                            np.arange(0, len(speaker_data['segments']) * len(speaker_audio) / len(speaker_data['segments']), ratio),
                            np.arange(len(speaker_audio)),
                            speaker_audio
                        )
                    
                    # Calculate start and end positions in the silent audio
                    start_sample = int(segment.start_time * sample_rate)
                    end_sample = int(segment.end_time * sample_rate)
                    segment_duration_samples = end_sample - start_sample
                    
                    # Extract the corresponding portion from speaker audio
                    # This is a simplified approach - in production, you'd use proper audio segmentation
                    if len(speaker_audio) > 0:
                        # Calculate which part of the speaker's audio corresponds to this segment
                        speaker_segments = speaker_data['segments']
                        segment_index = next((i for i, seg in enumerate(speaker_segments) if seg.start_time == segment.start_time), 0)
                        
                        # Extract portion of speaker audio for this segment
                        audio_per_segment = len(speaker_audio) // len(speaker_segments)
                        start_audio = segment_index * audio_per_segment
                        end_audio = min(start_audio + audio_per_segment, len(speaker_audio))
                        
                        segment_audio = speaker_audio[start_audio:end_audio]
                        
                        # Resize to fit the segment duration
                        if len(segment_audio) > segment_duration_samples:
                            segment_audio = segment_audio[:segment_duration_samples]
                        elif len(segment_audio) < segment_duration_samples:
                            # Pad with silence
                            padding = np.zeros(segment_duration_samples - len(segment_audio))
                            segment_audio = np.concatenate([segment_audio, padding])
                        
                        # Insert into the main audio track
                        if start_sample + len(segment_audio) <= len(silent_audio):
                            silent_audio[start_sample:start_sample + len(segment_audio)] = segment_audio
            
            # Save the timestamp-aligned audio
            output_path = os.path.join(output_dir, "dubbed_audio_timestamped.wav")
            sf.write(output_path, silent_audio, sample_rate)
            
            print(f"DEBUG: Timestamp-aligned audio created: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Timestamp alignment failed: {str(e)}")

    async def _combine_ai_audio_segments(self, audio_files: List[Dict], output_dir: str) -> str:
        """Combine AI-generated audio segments with timing preservation"""
        try:
            import ffmpeg
            
            # Create a more sophisticated audio combination
            output_path = os.path.join(output_dir, "dubbed_audio_ai.mp3")
            
            # For now, use simple concatenation
            # In production, you'd implement proper timing gaps and overlaps
            input_files = []
            for audio_file in audio_files:
                input_files.append(ffmpeg.input(audio_file['path']))
            
            # Concatenate with proper timing
            stream = ffmpeg.concat(*input_files, v=0, a=1)
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, overwrite_output=True)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"AI audio combination failed: {str(e)}")
    
    async def get_ai_analysis_summary(self, segments: List[SpeakerSegment]) -> Dict:
        """Get summary of AI analysis results"""
        try:
            summary = {
                'total_segments': len(segments),
                'unique_speakers': len(set(seg.total_speakers for seg in segments)),
                'speaker_analysis': {},
                'gender_distribution': defaultdict(int),
                'emotion_distribution': defaultdict(int)
            }
            
            # Analyze each speaker
            speaker_groups = defaultdict(list)
            for segment in segments:
                speaker_groups[segment.speaker_id].append(segment)
                summary['gender_distribution'][segment.gender] += 1
                summary['emotion_distribution'][segment.emotion] += 1
            
            for speaker_id, speaker_segments in speaker_groups.items():
                summary['speaker_analysis'][speaker_id] = {
                    'segment_count': len(speaker_segments),
                    'dominant_gender': max(set(seg.gender for seg in speaker_segments), 
                                         key=lambda x: sum(1 for seg in speaker_segments if seg.gender == x)),
                    'dominant_emotion': max(set(seg.emotion for seg in speaker_segments), 
                                          key=lambda x: sum(1 for seg in speaker_segments if seg.emotion == x)),
                    'total_duration': sum(seg.end_time - seg.start_time for seg in speaker_segments)
                }
            
            return summary
            
        except Exception as e:
            print(f"Analysis summary error: {e}")
            return {} 