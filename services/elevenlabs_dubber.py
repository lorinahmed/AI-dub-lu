import os
import asyncio
import requests
from typing import Dict, Optional

class ElevenLabsDubber:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        
    async def dub_video(self, audio_path: str, target_language: str, job_id: str) -> str:
        """Use ElevenLabs Dubbing API for professional dubbing"""
        try:
            if not self.api_key:
                raise Exception("ElevenLabs API key not configured")
            
            # Step 1: Upload audio file
            upload_url = f"{self.base_url}/dubbing/upload"
            
            with open(audio_path, 'rb') as audio_file:
                files = {'audio': audio_file}
                headers = {'xi-api-key': self.api_key}
                
                response = requests.post(upload_url, files=files, headers=headers)
                response.raise_for_status()
                
                upload_data = response.json()
                dubbing_id = upload_data['dubbing_id']
            
            print(f"DEBUG: Uploaded audio, dubbing_id: {dubbing_id}")
            
            # Step 2: Start dubbing process
            dubbing_url = f"{self.base_url}/dubbing/{dubbing_id}"
            
            dubbing_config = {
                "target_language": target_language,
                "mode": "automatic",  # Automatic speaker detection and voice matching
                "voice_settings": {
                    "similarity_boost": 0.75,
                    "stability": 0.5,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            headers = {
                'xi-api-key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(dubbing_url, json=dubbing_config, headers=headers)
            response.raise_for_status()
            
            print(f"DEBUG: Started dubbing process")
            
            # Step 3: Monitor dubbing progress
            dubbed_audio_path = await self._monitor_dubbing_progress(dubbing_id, job_id)
            
            return dubbed_audio_path
            
        except Exception as e:
            raise Exception(f"ElevenLabs dubbing failed: {str(e)}")
    
    async def _monitor_dubbing_progress(self, dubbing_id: str, job_id: str) -> str:
        """Monitor the dubbing progress and download when complete"""
        try:
            status_url = f"{self.base_url}/dubbing/{dubbing_id}"
            headers = {'xi-api-key': self.api_key}
            
            max_attempts = 60  # 5 minutes with 5-second intervals
            attempts = 0
            
            while attempts < max_attempts:
                response = requests.get(status_url, headers=headers)
                response.raise_for_status()
                
                status_data = response.json()
                status = status_data.get('status', 'unknown')
                
                print(f"DEBUG: Dubbing status: {status}")
                
                if status == 'completed':
                    # Download the dubbed audio
                    return await self._download_dubbed_audio(dubbing_id, job_id)
                elif status == 'failed':
                    raise Exception(f"Dubbing failed: {status_data.get('error', 'Unknown error')}")
                
                # Wait 5 seconds before checking again
                await asyncio.sleep(5)
                attempts += 1
            
            raise Exception("Dubbing timed out")
            
        except Exception as e:
            raise Exception(f"Progress monitoring failed: {str(e)}")
    
    async def _download_dubbed_audio(self, dubbing_id: str, job_id: str) -> str:
        """Download the completed dubbed audio"""
        try:
            download_url = f"{self.base_url}/dubbing/{dubbing_id}/audio"
            headers = {'xi-api-key': self.api_key}
            
            response = requests.get(download_url, headers=headers)
            response.raise_for_status()
            
            # Save the dubbed audio
            output_dir = os.path.join(os.getenv("OUTPUT_DIR", "./outputs"), job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, "dubbed_audio_elevenlabs.mp3")
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"DEBUG: Downloaded dubbed audio to {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Audio download failed: {str(e)}")
    
    async def get_dubbing_languages(self) -> list:
        """Get list of supported dubbing languages"""
        try:
            url = f"{self.base_url}/dubbing/languages"
            headers = {'xi-api-key': self.api_key}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Failed to get dubbing languages: {e}")
            return []
    
    async def get_dubbing_status(self, dubbing_id: str) -> Dict:
        """Get detailed status of a dubbing job"""
        try:
            url = f"{self.base_url}/dubbing/{dubbing_id}"
            headers = {'xi-api-key': self.api_key}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            raise Exception(f"Failed to get dubbing status: {str(e)}") 