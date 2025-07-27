import os
import asyncio
import ffmpeg
from typing import Optional

class VideoProcessor:
    def __init__(self):
        self.temp_dir = os.getenv("TEMP_DIR", "./temp")
        self.output_dir = os.getenv("OUTPUT_DIR", "./outputs")
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def extract_audio(self, video_path: str, job_id: str) -> str:
        """Extract audio from video file"""
        try:
            if not os.path.exists(video_path):
                raise Exception(f"Video file not found: {video_path}")
            
            # Create job-specific directory
            job_dir = os.path.join(self.temp_dir, job_id)
            os.makedirs(job_dir, exist_ok=True)
            
            # Define output audio path
            audio_path = os.path.join(job_dir, "extracted_audio.wav")
            
            # Run audio extraction in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._extract_audio_sync, video_path, audio_path
            )
            
            return audio_path
            
        except Exception as e:
            raise Exception(f"Audio extraction failed: {str(e)}")
    
    def _extract_audio_sync(self, video_path: str, audio_path: str):
        """Synchronous audio extraction using FFmpeg"""
        try:
            # Extract audio using FFmpeg
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, audio_path, acodec='pcm_s16le', ac=1, ar='16000')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
        except Exception as e:
            raise Exception(f"FFmpeg audio extraction error: {str(e)}")
    
    async def sync_audio_with_video(self, video_path: str, audio_path: str, job_id: str) -> str:
        """Synchronize dubbed audio with original video"""
        try:
            if not os.path.exists(video_path):
                raise Exception(f"Video file not found: {video_path}")
            
            if not os.path.exists(audio_path):
                raise Exception(f"Audio file not found: {audio_path}")
            
            # Create output directory
            output_dir = os.path.join(self.output_dir, job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Define output video path
            output_path = os.path.join(output_dir, "dubbed_video.mp4")
            
            # Run video processing in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._sync_audio_with_video_sync, video_path, audio_path, output_path
            )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Video-audio synchronization failed: {str(e)}")
    
    def _sync_audio_with_video_sync(self, video_path: str, audio_path: str, output_path: str):
        """Synchronous video-audio synchronization using FFmpeg"""
        try:
            # Get video and audio streams
            video_stream = ffmpeg.input(video_path)
            audio_stream = ffmpeg.input(audio_path)
            
            # Combine video with new audio, removing original audio
            output_stream = ffmpeg.output(
                video_stream['v'],  # Video stream only
                audio_stream['a'],  # New audio stream
                output_path,
                vcodec='copy',      # Copy video codec (no re-encoding)
                acodec='aac',       # Use AAC for audio
                strict='experimental'
            )
            
            # Run FFmpeg command
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
        except Exception as e:
            raise Exception(f"FFmpeg video processing error: {str(e)}")
    
    async def get_video_info(self, video_path: str) -> dict:
        """Get information about a video file"""
        try:
            if not os.path.exists(video_path):
                raise Exception(f"Video file not found: {video_path}")
            
            # Run FFmpeg probe in executor
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None, self._get_video_info_sync, video_path
            )
            
            return info
            
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")
    
    def _get_video_info_sync(self, video_path: str) -> dict:
        """Synchronous video info extraction using FFmpeg"""
        try:
            # Use FFmpeg probe to get video information
            probe = ffmpeg.probe(video_path)
            
            # Extract relevant information
            format_info = probe.get('format', {})
            video_stream = None
            audio_stream = None
            
            for stream in probe.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                elif stream.get('codec_type') == 'audio':
                    audio_stream = stream
            
            return {
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'bit_rate': int(format_info.get('bit_rate', 0)),
                'video': {
                    'width': video_stream.get('width', 0) if video_stream else 0,
                    'height': video_stream.get('height', 0) if video_stream else 0,
                    'codec': video_stream.get('codec_name', 'unknown') if video_stream else 'unknown',
                    'fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else 0
                },
                'audio': {
                    'codec': audio_stream.get('codec_name', 'unknown') if audio_stream else 'unknown',
                    'sample_rate': int(audio_stream.get('sample_rate', 0)) if audio_stream else 0,
                    'channels': int(audio_stream.get('channels', 0)) if audio_stream else 0
                } if audio_stream else None
            }
            
        except Exception as e:
            raise Exception(f"FFmpeg probe error: {str(e)}")
    
    async def compress_video(self, input_path: str, output_path: str, quality: str = "medium") -> str:
        """Compress video to reduce file size"""
        try:
            if not os.path.exists(input_path):
                raise Exception(f"Input video file not found: {input_path}")
            
            # Run compression in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._compress_video_sync, input_path, output_path, quality
            )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Video compression failed: {str(e)}")
    
    def _compress_video_sync(self, input_path: str, output_path: str, quality: str):
        """Synchronous video compression using FFmpeg"""
        try:
            # Quality presets
            quality_presets = {
                "low": {"crf": 28, "preset": "fast"},
                "medium": {"crf": 23, "preset": "medium"},
                "high": {"crf": 18, "preset": "slow"}
            }
            
            preset = quality_presets.get(quality, quality_presets["medium"])
            
            # Compress video
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(
                stream,
                output_path,
                vcodec='libx264',
                acodec='aac',
                crf=preset["crf"],
                preset=preset["preset"],
                movflags='+faststart'
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
        except Exception as e:
            raise Exception(f"FFmpeg compression error: {str(e)}")
    
    async def create_preview(self, video_path: str, duration: int = 30, job_id: str = None) -> str:
        """Create a preview clip of the video"""
        try:
            if not os.path.exists(video_path):
                raise Exception(f"Video file not found: {video_path}")
            
            # Create output directory
            output_dir = os.path.join(self.output_dir, job_id) if job_id else self.output_dir
            os.makedirs(output_dir, exist_ok=True)
            
            # Define output path
            output_path = os.path.join(output_dir, "preview.mp4")
            
            # Run preview creation in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._create_preview_sync, video_path, output_path, duration
            )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Preview creation failed: {str(e)}")
    
    def _create_preview_sync(self, video_path: str, output_path: str, duration: int):
        """Synchronous preview creation using FFmpeg"""
        try:
            # Create preview by taking first N seconds
            stream = ffmpeg.input(video_path, t=duration)
            stream = ffmpeg.output(
                stream,
                output_path,
                vcodec='copy',
                acodec='copy'
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
        except Exception as e:
            raise Exception(f"FFmpeg preview creation error: {str(e)}") 