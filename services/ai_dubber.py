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
from pyannote.audio import Pipeline

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
    matched_voice_id: str = None
    matched_voice_name: str = None

class AIDubber:
    def __init__(self):
        self.transcriber = Transcriber()
        self.translator = Translator()
        self.tts_service = TTSService()
        self.whisper_model = whisper.load_model("base")
        print("DEBUG: AI Dubber initialized with PyAnnote speaker diarization and voice matching")
        
    async def dub_with_ai_analysis(self, audio_path: str, target_language: str, job_id: str, timing_aware: bool = True, use_simple_fallback: bool = False) -> str:
        """AI-powered dubbing with speaker diarization and intelligent voice matching"""
        try:
            print(f"DEBUG: Starting AI-powered dubbing for job {job_id} (timing_aware: {timing_aware}, fallback: {use_simple_fallback})")
            
            if use_simple_fallback:
                print("DEBUG: Using simple fallback mode - skipping complex AI analysis")
                return await self._simple_dubbing_fallback(audio_path, target_language, job_id, timing_aware)
            
            # Step 1: Get PyAnnote speaker diarization
            print("DEBUG: Step 1 - Starting PyAnnote speaker diarization...")
            huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
            if not huggingface_token:
                raise Exception("HUGGINGFACE_TOKEN environment variable not set. Please add it to your .env file.")
            
            print("DEBUG: Loading PyAnnote pipeline...")
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=huggingface_token
            )
            print("DEBUG: Running PyAnnote diarization...")
            diarization = pipeline(audio_path)
            print("DEBUG: PyAnnote diarization completed")
            print("DEBUG: PyAnnote diarization result:")
            print(diarization)
            
            # Step 2: AI-powered transcription with PyAnnote speaker diarization
            print("DEBUG: Step 2 - Starting AI transcription with PyAnnote...")
            segments = await self._ai_transcribe_with_pyannote(audio_path, diarization)
            print(f"DEBUG: AI transcription completed, {len(segments)} segments created")
            
            # Step 3: AI analysis of each speaker segment
            print("DEBUG: Step 3 - Starting AI analysis of speakers...")
            segments = await self._analyze_speakers_ai(segments, audio_path)
            print(f"DEBUG: AI analysis completed, {len(segments)} segments analyzed")
            
            # Step 4: Intelligent voice matching per speaker
            print("DEBUG: Step 4 - Starting intelligent voice matching...")
            segments = await self._match_voices_intelligently(segments, target_language)
            print(f"DEBUG: Voice matching completed, {len(segments)} segments matched")
            
            # Step 5: Translate with context preservation (and timing awareness if enabled)
            print(f"DEBUG: Step 5 - Starting translation step...")
            segments = await self._translate_with_context(segments, target_language, timing_aware)
            print(f"DEBUG: Translation completed, {len(segments)} segments processed")
            
            # Step 6: Generate AI-enhanced speech (with timing adjustment if enabled)
            print(f"DEBUG: Step 6 - Starting speech generation step...")
            dubbed_audio_path = await self._generate_ai_speech(segments, target_language, job_id, timing_aware)
            print(f"DEBUG: Speech generation completed")
            
            return dubbed_audio_path
            
        except Exception as e:
            print(f"DEBUG: AI dubbing failed with error: {str(e)}")
            print("DEBUG: Attempting simple fallback mode...")
            try:
                return await self._simple_dubbing_fallback(audio_path, target_language, job_id, timing_aware)
            except Exception as fallback_error:
                print(f"DEBUG: Simple fallback also failed: {str(fallback_error)}")
                raise Exception(f"AI dubbing failed: {str(e)}")
    
    async def _simple_dubbing_fallback(self, audio_path: str, target_language: str, job_id: str, timing_aware: bool = True) -> str:
        """Simple fallback dubbing without complex AI analysis"""
        try:
            print("DEBUG: Starting simple fallback dubbing...")
            
            # Step 1: Simple transcription with Whisper
            print("DEBUG: Step 1 - Simple Whisper transcription...")
            result = self.whisper_model.transcribe(
                audio_path,
                verbose=True,
                word_timestamps=True,
                language="en"
            )
            print("DEBUG: Simple transcription completed")
            
            # Step 2: Create simple segments
            print("DEBUG: Step 2 - Creating simple segments...")
            segments = []
            for i, seg in enumerate(result.get('segments', [])):
                segment = SpeakerSegment(
                    start_time=seg.get('start', 0),
                    end_time=seg.get('end', 0),
                    text=seg.get('text', '').strip(),
                    speaker_id=f"SPEAKER_{i:02d}",
                    gender="unknown",
                    confidence=1.0
                )
                segments.append(segment)
            print(f"DEBUG: Created {len(segments)} simple segments")
            
            # Step 3: Simple translation
            print("DEBUG: Step 3 - Simple translation...")
            segments = await self._translate_with_context(segments, target_language, timing_aware)
            print(f"DEBUG: Simple translation completed, {len(segments)} segments processed")
            
            # Step 4: Simple speech generation
            print("DEBUG: Step 4 - Simple speech generation...")
            dubbed_audio_path = await self._generate_ai_speech(segments, target_language, job_id, timing_aware)
            print("DEBUG: Simple speech generation completed")
            
            return dubbed_audio_path
            
        except Exception as e:
            print(f"DEBUG: Simple fallback failed: {str(e)}")
            raise Exception(f"Simple fallback dubbing failed: {str(e)}")
    
    async def _ai_transcribe_with_pyannote(self, audio_path: str, diarization) -> List[SpeakerSegment]:
        """AI-powered transcription with PyAnnote speaker diarization"""
        try:
            print(f"DEBUG: Starting AI transcription with PyAnnote speaker detection")
            
            # Step 1: Use Whisper for transcription
            print("DEBUG: Running Whisper transcription...")
            result = self.whisper_model.transcribe(
                audio_path,
                verbose=True,
                word_timestamps=True,
                language="en"
            )
            print("DEBUG: Whisper transcription completed")
            print("-----------------Whisper result----------------- ")
            print(result)
            
            # Step 2: Align Whisper segments with PyAnnote diarization
            print("DEBUG: Aligning Whisper segments with PyAnnote diarization...")
            segments = self._align_whisper_with_pyannote(result['segments'], diarization)
            print(f"DEBUG: Alignment completed, created {len(segments)} segments with PyAnnote speaker detection")
            
            return segments
            
        except Exception as e:
            print(f"DEBUG: AI transcription failed with error: {str(e)}")
            raise Exception(f"AI transcription failed: {str(e)}")
    
    async def _ai_transcribe_with_speakers(self, audio_path: str) -> List[SpeakerSegment]:
        """AI-powered transcription with fallback speaker detection (legacy method)"""
        try:
            print(f"DEBUG: Starting AI transcription with fallback speaker detection")
            
            # Step 1: Use Whisper for transcription
            result = self.whisper_model.transcribe(
                audio_path,
                verbose=True,
                word_timestamps=True,
                language="en"
            )
            
            
            # Step 2: Create simple speaker segments (fallback approach)
            segments = self._create_fallback_speaker_segments(result['segments'])
            
            print(f"DEBUG: Created {len(segments)} segments with fallback speaker detection")
            return segments
            
        except Exception as e:
            raise Exception(f"AI transcription failed: {str(e)}")
    
    def _align_whisper_with_pyannote(self, whisper_segments: List[Dict], diarization) -> List[SpeakerSegment]:
        """Align Whisper transcription segments with PyAnnote speaker diarization"""
        try:
            segments = []
            
            # Extract speaker timeline from PyAnnote diarization
            speaker_timeline = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speaker_timeline.append({
                    'start': turn.start,
                    'end': turn.end,
                    'speaker': speaker
                })
                print(f"DEBUG: PyAnnote - Speaker {speaker} speaks from {turn.start:.1f}s to {turn.end:.1f}s")
            
            # Sort by start time
            speaker_timeline.sort(key=lambda x: x['start'])
            
            print(f"DEBUG: PyAnnote found {len(set(s['speaker'] for s in speaker_timeline))} unique speakers")
            
            # Align each Whisper segment with PyAnnote speaker
            for i, segment in enumerate(whisper_segments):
                segment_start = segment['start']
                segment_end = segment['end']
                segment_mid = (segment_start + segment_end) / 2
                
                # Find which speaker is talking at the midpoint of this segment
                assigned_speaker = 'SPEAKER_00'  # Default fallback
                
                for speaker_turn in speaker_timeline:
                    if speaker_turn['start'] <= segment_mid <= speaker_turn['end']:
                        assigned_speaker = speaker_turn['speaker']
                        break
                
                # If no exact match, find the closest speaker turn
                if assigned_speaker == 'SPEAKER_00' and speaker_timeline:
                    closest_turn = min(speaker_timeline, 
                                     key=lambda x: min(abs(x['start'] - segment_mid), abs(x['end'] - segment_mid)))
                    assigned_speaker = closest_turn['speaker']
                
                # Create speaker segment
                speaker_segment = SpeakerSegment(
                    start_time=segment_start,
                    end_time=segment_end,
                    text=segment['text'].strip(),
                    speaker_id=assigned_speaker,
                    confidence=segment.get('confidence', 0.0),
                    voice_characteristics={}
                )
                
                segments.append(speaker_segment)
                print(f"DEBUG: Segment {i}: Speaker {assigned_speaker}, Text: {segment['text'][:50]}...")
            
            return segments
            
        except Exception as e:
            print(f"PyAnnote alignment error: {e}")
            # Fallback: assign all segments to single speaker
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
        """AI analysis of each speaker's voice characteristics for voice matching"""
        try:
            print(f"DEBUG: Starting voice characteristics analysis for voice matching")
            
            # Load audio for analysis
            y, sr = librosa.load(audio_path, sr=None)
            
            # Group segments by speaker for analysis
            speaker_groups = defaultdict(list)
            for segment in segments:
                speaker_groups[segment.speaker_id].append(segment)
            
            # Analyze each speaker's characteristics
            for speaker_id, speaker_segments in speaker_groups.items():
                print(f"DEBUG: Analyzing voice characteristics for speaker {speaker_id} with {len(speaker_segments)} segments")
                
                # Analyze first few segments of this speaker
                analysis_segments = speaker_segments[:3]  # Analyze first 3 segments
                
                all_characteristics = []
                
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
                        all_characteristics.append(characteristics)
                        
                        print(f"DEBUG: Speaker {speaker_id} - Pitch: {characteristics.get('pitch_mean', 0):.1f}Hz, "
                              f"Energy: {characteristics.get('energy_mean', 0):.3f}, "
                              f"Spectral Centroid: {characteristics.get('spectral_centroid_mean', 0):.1f}Hz")
                        
                    except Exception as e:
                        print(f"DEBUG: Error analyzing segment for speaker {speaker_id}: {e}")
                        continue
                
                # Calculate average characteristics for this speaker
                if all_characteristics:
                    avg_characteristics = {}
                    for key in all_characteristics[0].keys():
                        values = [char.get(key, 0) for char in all_characteristics if char.get(key, 0) > 0]
                        if values:
                            avg_characteristics[key] = sum(values) / len(values)
                        else:
                            avg_characteristics[key] = 0
                    
                    # Assign average characteristics to all segments of this speaker
                    for segment in speaker_segments:
                        segment.voice_characteristics = avg_characteristics
                        segment.gender = "unknown"  # We're not using gender detection
                        segment.emotion = "neutral"  # Keep default emotion
                
                print(f"DEBUG: Completed voice analysis for speaker {speaker_id}")
            
            return segments
            
        except Exception as e:
            raise Exception(f"Voice characteristics analysis failed: {str(e)}")
    
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
        """Intelligent voice matching based on AI analysis and available voices"""
        try:
            print(f"DEBUG: Starting intelligent voice matching")
            
            # Step 1: Download available voices from ElevenLabs
            available_voices = await self.tts_service.get_available_voices()
            print(f"DEBUG: Downloaded {len(available_voices)} available voices from ElevenLabs")
            
            # Step 2: Group by speaker and analyze patterns
            speaker_profiles = defaultdict(list)
            for segment in segments:
                speaker_profiles[segment.speaker_id].append(segment)
            
            # Step 3: Create voice profiles for each speaker
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
            
            # Step 4: Match speakers to available voices based on characteristics
            if not available_voices:
                raise Exception("Failed to download available voices from ElevenLabs - voice matching cannot proceed")
            
            speaker_voice_mapping = await self._match_speakers_to_voices(
                voice_profiles, available_voices, target_language
            )
            
            # Step 5: Assign matched voice IDs to segments
            for speaker_id, voice_info in speaker_voice_mapping.items():
                # Only print once per speaker, not per segment
                print(f"DEBUG: Speaker {speaker_id} matched to voice: {voice_info.get('name')} ({voice_info.get('voice_id')})")
                
                # Assign to all segments of this speaker
                for segment in segments:
                    if segment.speaker_id == speaker_id:
                        segment.matched_voice_id = voice_info.get('voice_id')
                        segment.matched_voice_name = voice_info.get('name')
            
            return segments
            
        except Exception as e:
            raise Exception(f"Voice matching failed: {str(e)}")
    
    async def _match_speakers_to_voices(self, voice_profiles: Dict, available_voices: List, target_language: str) -> Dict:
        """Match speaker profiles to available voices based on characteristics"""
        try:
            speaker_voice_mapping = {}
            
            # Filter voices by language support using language field
            language_voices = []
            print(f"DEBUG: Checking {len(available_voices)} voices for language support: {target_language}")
            
            for voice in available_voices:
                # Check verified_languages array (proper ElevenLabs API approach)
                if hasattr(voice, 'verified_languages') and voice.verified_languages:
                    print(f"DEBUG: Voice {voice.name} - Verified languages: {voice.verified_languages}")
                    
                    # Check if target language is in verified_languages
                    supports_language = False
                    for lang_info in voice.verified_languages:
                        # Each lang_info is a VerifiedVoiceLanguageResponseModel object
                        if hasattr(lang_info, 'language') and lang_info.language:
                            if lang_info.language.lower() == target_language.lower():
                                supports_language = True
                                print(f"DEBUG: Found language match: {lang_info.language}")
                                break
                    
                    if supports_language:
                        language_voices.append(voice)
                        print(f"DEBUG: ✓ Voice {voice.name} supports {target_language}")
                    else:
                        print(f"DEBUG: ✗ Voice {voice.name} does not support {target_language}")
                else:
                    print(f"DEBUG: Voice {voice.name} - No verified_languages available")
            
            if not language_voices:
                print(f"DEBUG: No voices found supporting language: {target_language}")
                print("DEBUG: Available voices and their verified_languages:")
                for voice in available_voices:
                    if hasattr(voice, 'verified_languages') and voice.verified_languages:
                        languages = [lang.language for lang in voice.verified_languages if hasattr(lang, 'language') and lang.language]
                        print(f"  - {voice.name}: {languages}")
                raise Exception(f"No voices found supporting language: {target_language}")
            
            print(f"DEBUG: Found {len(language_voices)} voices supporting language {target_language}")
            
            # Match each speaker to the best available voice
            used_voices = set()  # Track used voices to avoid duplicates
            
            for speaker_id, profile in voice_profiles.items():
                best_voice = None
                best_score = -1
                candidate_voices = []
                
                # Score all voices for this speaker
                for voice in language_voices:
                    score = self._calculate_voice_match_score(profile, voice)
                    candidate_voices.append((voice, score))
                
                # Sort by score (highest first)
                candidate_voices.sort(key=lambda x: x[1], reverse=True)
                
                # Find the best unused voice
                for voice, score in candidate_voices:
                    if voice.voice_id not in used_voices:
                        best_voice = voice
                        best_score = score
                        used_voices.add(voice.voice_id)
                        break
                
                # If all voices are used, use the best one anyway
                if not best_voice and candidate_voices:
                    best_voice, best_score = candidate_voices[0]
                
                if not best_voice:
                    raise Exception(f"No suitable voice found for speaker {speaker_id} with characteristics: {profile}")
                
                speaker_voice_mapping[speaker_id] = {
                    'voice_id': best_voice.voice_id,
                    'name': best_voice.name,
                    'match_score': best_score
                }
                print(f"DEBUG: Speaker {speaker_id} matched to {best_voice.name} with score {best_score:.2f}")
            
            return speaker_voice_mapping
            
        except Exception as e:
            print(f"Voice matching error: {e}")
            return {}
    
    def _calculate_voice_match_score(self, speaker_profile: Dict, voice) -> float:
        """Calculate how well a voice matches a speaker profile based on acoustic characteristics"""
        try:
            score = 0.0
            
            # Get speaker acoustic characteristics
            speaker_pitch = speaker_profile.get('pitch_mean', 0)
            speaker_energy = speaker_profile.get('energy_mean', 0)
            speaker_spectral_centroid = speaker_profile.get('spectral_centroid_mean', 0)
            speaker_mfcc_mean = speaker_profile.get('mfcc_mean', 0)
            speaker_speaking_rate = speaker_profile.get('speaking_rate', 0)
            
            # Voice characteristics from ElevenLabs (if available)
            if hasattr(voice, 'labels') and voice.labels:
                # Use acoustic characteristics for matching instead of gender labels
                voice_gender = voice.labels.get('gender', '').lower()
                
                # Pitch-based matching (primary factor)
                if speaker_pitch > 0:
                    if voice_gender in ['female', 'woman'] and 150 < speaker_pitch < 250:
                        score += 3.0  # High score for pitch match
                    elif voice_gender in ['male', 'man'] and 80 < speaker_pitch < 160:
                        score += 3.0  # High score for pitch match
                    elif voice_gender in ['female', 'woman'] and speaker_pitch < 150:
                        score += 1.0  # Lower score for mismatch
                    elif voice_gender in ['male', 'man'] and speaker_pitch > 160:
                        score += 1.0  # Lower score for mismatch
                
                # Age characteristics based on spectral centroid
                voice_age = voice.labels.get('age', '').lower()
                if voice_age and speaker_spectral_centroid > 0:
                    if 'young' in voice_age and speaker_spectral_centroid > 2000:
                        score += 2.0  # Young voice with high spectral centroid
                    elif 'mature' in voice_age and speaker_spectral_centroid < 1500:
                        score += 2.0  # Mature voice with low spectral centroid
                    elif 'young' in voice_age and speaker_spectral_centroid < 1500:
                        score += 0.5  # Lower score for age mismatch
                    elif 'mature' in voice_age and speaker_spectral_centroid > 2000:
                        score += 0.5  # Lower score for age mismatch
                
                # Energy level matching
                if speaker_energy > 0.1:  # High energy speaker
                    if 'energetic' in voice.labels.get('description', '').lower():
                        score += 1.5
                    elif 'calm' in voice.labels.get('description', '').lower():
                        score += 0.5
                
                # Accent/language preference (secondary factor)
                voice_accent = voice.labels.get('accent', '').lower()
                if voice_accent:
                    score += 0.5  # Small bonus for any accent information
            
            # Energy level scoring
            if speaker_energy > 0.15:  # High energy
                score += 1.0
            elif speaker_energy > 0.05:  # Medium energy
                score += 0.5
            
            # Speaking rate consideration
            if speaker_speaking_rate > 0.1:  # Fast speaker
                score += 0.5
            
            print(f"DEBUG: Voice match score for {voice.name}: {score:.2f} "
                  f"(Pitch: {speaker_pitch:.1f}Hz, Energy: {speaker_energy:.3f}, "
                  f"Spectral: {speaker_spectral_centroid:.1f}Hz)")
            
            return score
            
        except Exception as e:
            print(f"Voice match scoring error: {e}")
            return 0.0
    
    async def _translate_with_context(self, segments: List[SpeakerSegment], target_language: str, timing_aware: bool = True) -> List[SpeakerSegment]:
        """Translate with context preservation for better quality"""
        try:
            print(f"DEBUG: Starting context-aware translation (timing_aware: {timing_aware})")
            
            # Convert segments to format expected by translator
            segment_dicts = []
            for segment in segments:
                if segment.text.strip():
                    segment_dicts.append({
                        "start": segment.start_time,
                        "end": segment.end_time,
                        "text": segment.text.strip(),
                        "speaker_id": segment.speaker_id
                    })
            
            # Use timing-aware translation if enabled
            if timing_aware:
                translated_segments = await self.translator.translate_segments(
                    segment_dicts, target_language, timing_aware=True
                )
                
                # Create a mapping from segment dicts to original segments
                segment_mapping = {}
                for i, seg_dict in enumerate(segment_dicts):
                    for j, original_seg in enumerate(segments):
                        if (original_seg.start_time == seg_dict["start"] and 
                            original_seg.end_time == seg_dict["end"] and 
                            original_seg.text.strip() == seg_dict["text"]):
                            segment_mapping[i] = j
                            break
                
                # Update original segments with translated text
                for i, translated_seg in enumerate(translated_segments):
                    if i in segment_mapping:
                        original_idx = segment_mapping[i]
                        if original_idx < len(segments):
                            segments[original_idx].text = translated_seg.get("translated_text", segments[original_idx].text)
                            print(f"DEBUG: Timing-aware translated segment {original_idx} (Speaker {segments[original_idx].speaker_id}): {segments[original_idx].text[:50]}...")
            else:
                # Regular translation
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
    
    async def _generate_ai_speech(self, segments: List[SpeakerSegment], target_language: str, job_id: str, timing_aware: bool = True) -> str:
        """Generate AI-enhanced speech with speaker-specific voices and timing"""
        try:
            print(f"DEBUG: Starting AI speech generation with per-speaker voices (timing_aware: {timing_aware})")
            
            # Create output directory
            output_dir = os.path.join(os.getenv("OUTPUT_DIR", "./outputs"), job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            if timing_aware:
                # Use timing-aware speech generation with speed adjustment
                return await self._generate_timing_aware_speech(segments, target_language, job_id, output_dir)
            else:
                # Use regular AI speech generation
                return await self._generate_regular_ai_speech(segments, target_language, job_id, output_dir)
            
        except Exception as e:
            raise Exception(f"AI speech generation failed: {str(e)}")
    
    async def _generate_regular_ai_speech(self, segments: List[SpeakerSegment], target_language: str, job_id: str, output_dir: str) -> str:
        """Generate regular AI-enhanced speech with speaker-specific voices"""
        try:
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
                
                # Get voice characteristics for this speaker
                avg_characteristics = {}
                if speaker_segments_list and speaker_segments_list[0].voice_characteristics:
                    avg_characteristics = speaker_segments_list[0].voice_characteristics
                    print(f"DEBUG: Speaker {speaker_id} - Pitch: {avg_characteristics.get('pitch_mean', 0):.1f}Hz, "
                          f"Energy: {avg_characteristics.get('energy_mean', 0):.3f}, "
                          f"Spectral: {avg_characteristics.get('spectral_centroid_mean', 0):.1f}Hz")
                
                # Get the matched voice ID for this speaker
                matched_voice_id = None
                if speaker_segments_list and speaker_segments_list[0].matched_voice_id:
                    matched_voice_id = speaker_segments_list[0].matched_voice_id
                    print(f"DEBUG: Using matched voice ID: {matched_voice_id} for speaker {speaker_id}")
                
                # Generate speech for this speaker using matched voice
                speaker_audio_path = await self.tts_service.generate_speech(
                    speaker_text, target_language, f"{job_id}_{speaker_id}", "unknown", matched_voice_id
                )
                
                speaker_audio_files[speaker_id] = {
                    'path': speaker_audio_path,
                    'segments': speaker_segments_list,
                    'voice_characteristics': avg_characteristics
                }
            
            # For now, let's use a simpler approach - just combine all audio without complex timestamp alignment
            # This will avoid the audio distortion issue
            final_audio_path = await self._combine_speaker_audio_simple(speaker_audio_files, output_dir)
            
            print(f"DEBUG: AI dubbing completed successfully")
            return final_audio_path
            
        except Exception as e:
            raise Exception(f"Regular AI speech generation failed: {str(e)}")
    
    async def _generate_timing_aware_speech(self, segments: List[SpeakerSegment], target_language: str, job_id: str, output_dir: str) -> str:
        """Generate timing-aware speech with speed adjustment"""
        try:
            print(f"DEBUG: Starting timing-aware speech generation")
            
            # Convert segments to format expected by TTS service
            segment_dicts = []
            for segment in segments:
                if segment.text.strip():
                    # Ensure valid timing
                    start_time = max(0, segment.start_time)
                    end_time = max(start_time + 0.1, segment.end_time)  # Minimum 0.1s duration
                    
                    segment_dicts.append({
                        "start": start_time,
                        "end": end_time,
                        "translated_text": segment.text.strip(),
                        "original_duration": end_time - start_time,
                        "speaker_id": segment.speaker_id
                    })
            
            # Check if we have any segments to process
            if not segment_dicts:
                print("DEBUG: No valid segments found for timing-aware speech generation")
                # Create a fallback audio file
                fallback_path = os.path.join(output_dir, "dubbed_audio.mp3")
                from pydub import AudioSegment
                silent_audio = AudioSegment.silent(duration=1000)  # 1 second of silence
                silent_audio.export(fallback_path, format="mp3")
                return fallback_path
            
            print(f"DEBUG: Processing {len(segment_dicts)} segments for timing-aware speech")
            
            # Use TTS service with timing and speed adjustment
            dubbed_audio_path = await self.tts_service.generate_speech_with_timing(
                segment_dicts, target_language, job_id, adjust_speed=True
            )
            
            print(f"DEBUG: Timing-aware AI dubbing completed successfully")
            return dubbed_audio_path
            
        except Exception as e:
            print(f"DEBUG: Timing-aware speech generation failed: {str(e)}")
            # Create a fallback audio file
            fallback_path = os.path.join(output_dir, "dubbed_audio.mp3")
            from pydub import AudioSegment
            silent_audio = AudioSegment.silent(duration=1000)  # 1 second of silence
            silent_audio.export(fallback_path, format="mp3")
            return fallback_path
    
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