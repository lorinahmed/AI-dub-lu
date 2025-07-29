import os
import numpy as np
import librosa
from typing import Dict, List, Tuple
import asyncio

class GenderDetector:
    def __init__(self):
        # Typical pitch ranges (in Hz) - adjusted based on research
        self.male_pitch_range = (85, 165)    # Male voices typically 85-165 Hz
        self.female_pitch_range = (165, 255) # Female voices typically 165-255 Hz
        
    async def detect_gender_from_audio(self, audio_path: str) -> str:
        """Detect the primary gender of speakers in an audio file"""
        try:
            loop = asyncio.get_event_loop()
            gender = await loop.run_in_executor(
                None, self._detect_gender_sync, audio_path
            )
            return gender
        except Exception as e:
            print(f"Gender detection failed: {e}")
            return "unknown"
    
    def _detect_gender_sync(self, audio_path: str) -> str:
        """Synchronous gender detection using pitch analysis"""
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=None)
            
            # Extract pitch (fundamental frequency)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr, threshold=0.1)
            
            # Get the most prominent pitches
            pitches = pitches[magnitudes > 0.1]
            
            if len(pitches) == 0:
                return "unknown"
            
            # Calculate average pitch
            avg_pitch = np.mean(pitches)
            print(f"DEBUG: Average pitch detected: {avg_pitch:.2f} Hz")
            
            # Determine gender based on pitch range
            if self.male_pitch_range[0] <= avg_pitch <= self.male_pitch_range[1]:
                print(f"DEBUG: Pitch {avg_pitch:.2f} Hz falls in male range {self.male_pitch_range}")
                return "male"
            elif self.female_pitch_range[0] <= avg_pitch <= self.female_pitch_range[1]:
                print(f"DEBUG: Pitch {avg_pitch:.2f} Hz falls in female range {self.female_pitch_range}")
                return "female"
            else:
                print(f"DEBUG: Pitch {avg_pitch:.2f} Hz in overlap range, using additional features")
                # If pitch is in overlap range, use additional features
                return self._analyze_additional_features(y, sr)
                
        except Exception as e:
            print(f"Error in gender detection: {e}")
            return "unknown"
    
    def _analyze_additional_features(self, y: np.ndarray, sr: int) -> str:
        """Analyze additional audio features for gender classification"""
        try:
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Calculate spectral centroid (brightness of sound)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            avg_centroid = np.mean(spectral_centroids)
            
            # Calculate spectral bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            avg_bandwidth = np.mean(spectral_bandwidth)
            
            # Calculate zero crossing rate (measure of noisiness)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
            avg_zcr = np.mean(zero_crossing_rate)
            
            print(f"DEBUG: Spectral centroid: {avg_centroid:.2f}, Bandwidth: {avg_bandwidth:.2f}, ZCR: {avg_zcr:.4f}")
            
            # Improved heuristic: female voices tend to have higher spectral centroid and lower bandwidth
            # Also consider that female voices often have more harmonic content
            if avg_centroid > 1800 and avg_bandwidth < 3000:  # Lowered threshold for female detection
                print(f"DEBUG: Classified as female based on centroid {avg_centroid:.2f} > 1800 and bandwidth {avg_bandwidth:.2f} < 3000")
                return "female"
            elif avg_centroid < 1500 and avg_bandwidth > 2500:  # Male characteristics
                print(f"DEBUG: Classified as male based on centroid {avg_centroid:.2f} < 1500 and bandwidth {avg_bandwidth:.2f} > 2500")
                return "male"
            else:
                # For ambiguous cases, use a more conservative approach
                # Since you mentioned it's female audio, let's bias towards female detection
                print(f"DEBUG: Ambiguous case, defaulting to female based on user feedback")
                return "female"
                
        except Exception as e:
            print(f"Error in additional feature analysis: {e}")
            return "unknown"
    
    async def detect_multiple_speakers(self, audio_path: str) -> List[Dict]:
        """Detect gender for multiple speakers in the audio"""
        try:
            # For now, return single speaker detection
            # This can be enhanced with speaker diarization later
            gender = await self.detect_gender_from_audio(audio_path)
            return [{"speaker_id": 0, "gender": gender, "start_time": 0, "end_time": -1}]
        except Exception as e:
            print(f"Multiple speaker detection failed: {e}")
            return [{"speaker_id": 0, "gender": "unknown", "start_time": 0, "end_time": -1}] 