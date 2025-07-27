import os
import asyncio
import yt_dlp
from typing import Optional

class YouTubeDownloader:
    def __init__(self):
        self.download_dir = os.getenv("UPLOAD_DIR", "./uploads")
        os.makedirs(self.download_dir, exist_ok=True)
    
    async def download_video(self, youtube_url: str, job_id: str) -> str:
        """Download a YouTube video and return the path to the downloaded file"""
        try:
            # Create job-specific directory
            job_dir = os.path.join(self.download_dir, job_id)
            os.makedirs(job_dir, exist_ok=True)
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best[height<=720]',  # Limit to 720p for faster processing
                'outtmpl': os.path.join(job_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            # Download the video
            loop = asyncio.get_event_loop()
            video_path = await loop.run_in_executor(
                None, self._download_with_ytdlp, youtube_url, ydl_opts, job_dir
            )
            
            return video_path
            
        except Exception as e:
            raise Exception(f"Failed to download YouTube video: {str(e)}")
    
    def _download_with_ytdlp(self, youtube_url: str, ydl_opts: dict, job_dir: str) -> str:
        """Download video using yt-dlp in a synchronous manner"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            info = ydl.extract_info(youtube_url, download=False)
            video_title = info.get('title', 'video')
            
            # Download the video
            ydl.download([youtube_url])
            
            # Find the downloaded file in the job directory
            print(f"Debug: job_dir = {job_dir}")
            for filename in os.listdir(job_dir):
                if filename.endswith(('.mp4', '.webm', '.mkv')):
                    return os.path.join(job_dir, filename)
            
            raise Exception("Downloaded video file not found")
    
    async def get_video_info(self, youtube_url: str) -> dict:
        """Get information about a YouTube video without downloading"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None, self._extract_info_with_ytdlp, youtube_url, ydl_opts
            )
            
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'thumbnail': info.get('thumbnail', ''),
            }
            
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")
    
    def _extract_info_with_ytdlp(self, youtube_url: str, ydl_opts: dict) -> dict:
        """Extract video info using yt-dlp in a synchronous manner"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(youtube_url, download=False) 