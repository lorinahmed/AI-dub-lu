import os
import numpy as np
import librosa
from typing import Dict, List, Tuple
import asyncio

class GenderDetector:
    def __init__(self):
        # Typical pitch ranges (in Hz)
        self.male_pitch_range = (85, 180)    # Male voices typically 85-180 Hz
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
            
            # Determine gender based on pitch range
            if self.male_pitch_range[0] <= avg_pitch <= self.male_pitch_range[1]:
                return "male"
            elif self.female_pitch_range[0] <= avg_pitch <= self.female_pitch_range[1]:
                return "female"
            else:
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
            
            # Simple heuristic: female voices tend to have higher spectral centroid
            if avg_centroid > 2000:  # Threshold for female-like brightness
                return "female"
            else:
                return "male"
                
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