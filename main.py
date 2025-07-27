import os
import uuid
import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

from services.youtube_downloader import YouTubeDownloader
from services.transcriber import Transcriber
from services.translator import Translator
from services.tts_service import TTSService
from services.video_processor import VideoProcessor
from services.gender_detector import GenderDetector
from utils.job_manager import JobManager

# Load environment variables
load_dotenv()

app = FastAPI(title="YouTube Video Dubber", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
job_manager = JobManager()
youtube_downloader = YouTubeDownloader()
transcriber = Transcriber()
translator = Translator()
tts_service = TTSService()
video_processor = VideoProcessor()
gender_detector = GenderDetector()

class DubRequest(BaseModel):
    youtube_url: str
    target_language: str
    source_language: Optional[str] = None

class DubResponse(BaseModel):
    job_id: str
    status: str
    message: str

@app.post("/dub", response_model=DubResponse)
async def start_dubbing(request: DubRequest, background_tasks: BackgroundTasks):
    """Start the dubbing process for a YouTube video"""
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job
        job_manager.create_job(job_id, {
            "youtube_url": request.youtube_url,
            "target_language": request.target_language,
            "source_language": request.source_language,
            "status": "initialized"
        })
        
        # Start background processing
        background_tasks.add_task(
            process_dubbing_job,
            job_id,
            request.youtube_url,
            request.target_language,
            request.source_language
        )
        
        return DubResponse(
            job_id=job_id,
            status="started",
            message="Dubbing job started successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a dubbing job"""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job_id,
        "status": job.get("status", "unknown"),
        "progress": job.get("progress", 0),
        "message": job.get("message", ""),
        "error": job.get("error", None)
    }

@app.get("/download/{job_id}")
async def download_dubbed_video(job_id: str):
    """Download the completed dubbed video"""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    output_path = job.get("output_path")
    if not output_path or not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return {"download_url": f"/files/{job_id}/dubbed_video.mp4"}

@app.get("/jobs")
async def get_jobs():
    """Get all jobs with statistics"""
    stats = job_manager.get_job_stats()
    return stats

async def process_dubbing_job(job_id: str, youtube_url: str, target_language: str, source_language: Optional[str] = None):
    """Background task to process the dubbing job"""
    try:
        # Update job status
        job_manager.update_job(job_id, {"status": "downloading", "progress": 10})
        
        # Step 1: Download YouTube video
        video_path = await youtube_downloader.download_video(youtube_url, job_id)
        job_manager.update_job(job_id, {"status": "extracting_audio", "progress": 20})
        
        # Step 2: Extract audio
        audio_path = await video_processor.extract_audio(video_path, job_id)
        job_manager.update_job(job_id, {"status": "detecting_gender", "progress": 25})
        
        # Step 3: Detect speaker gender
        gender = await gender_detector.detect_gender_from_audio(audio_path)
        job_manager.update_job(job_id, {"status": "transcribing", "progress": 30})
        
        # Step 4: Transcribe audio
        transcription = await transcriber.transcribe(audio_path, source_language)
        job_manager.update_job(job_id, {"status": "translating", "progress": 50})
        
        # Step 5: Translate transcription
        translated_text = await translator.translate(transcription, target_language)
        job_manager.update_job(job_id, {"status": "generating_speech", "progress": 70})
        
        # Step 6: Generate speech with gender-matched voice
        dubbed_audio_path = await tts_service.generate_speech(translated_text, target_language, job_id, gender)
        job_manager.update_job(job_id, {"status": "synchronizing", "progress": 85})
        
        # Step 7: Synchronize audio with video
        output_path = await video_processor.sync_audio_with_video(
            video_path, dubbed_audio_path, job_id
        )
        
        # Update job as completed
        job_manager.update_job(job_id, {
            "status": "completed",
            "progress": 100,
            "output_path": output_path,
            "message": "Dubbing completed successfully"
        })
        
    except Exception as e:
        job_manager.update_job(job_id, {
            "status": "failed",
            "error": str(e),
            "message": f"Dubbing failed: {str(e)}"
        })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "YouTube Video Dubber"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    ) 