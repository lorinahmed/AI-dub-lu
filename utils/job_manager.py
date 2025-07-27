import os
import json
import time
from typing import Dict, Optional
from datetime import datetime

class JobManager:
    def __init__(self):
        self.jobs = {}
        self.jobs_file = os.path.join(os.getenv("TEMP_DIR", "./temp"), "jobs.json")
        self._load_jobs()
    
    def _load_jobs(self):
        """Load jobs from persistent storage"""
        try:
            if os.path.exists(self.jobs_file):
                with open(self.jobs_file, 'r') as f:
                    self.jobs = json.load(f)
        except Exception as e:
            print(f"Error loading jobs: {e}")
            self.jobs = {}
    
    def _save_jobs(self):
        """Save jobs to persistent storage"""
        try:
            os.makedirs(os.path.dirname(self.jobs_file), exist_ok=True)
            with open(self.jobs_file, 'w') as f:
                json.dump(self.jobs, f, indent=2)
        except Exception as e:
            print(f"Error saving jobs: {e}")
    
    def create_job(self, job_id: str, job_data: Dict):
        """Create a new job"""
        job_data.update({
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "initialized",
            "progress": 0
        })
        
        self.jobs[job_id] = job_data
        self._save_jobs()
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def update_job(self, job_id: str, updates: Dict):
        """Update job with new data"""
        if job_id in self.jobs:
            self.jobs[job_id].update(updates)
            self.jobs[job_id]["updated_at"] = datetime.now().isoformat()
            self._save_jobs()
    
    def delete_job(self, job_id: str):
        """Delete a job"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            self._save_jobs()
    
    def get_all_jobs(self) -> Dict:
        """Get all jobs"""
        return self.jobs
    
    def get_jobs_by_status(self, status: str) -> Dict:
        """Get jobs filtered by status"""
        return {job_id: job for job_id, job in self.jobs.items() if job.get("status") == status}
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Clean up old completed or failed jobs"""
        current_time = datetime.now()
        jobs_to_delete = []
        
        for job_id, job in self.jobs.items():
            if job.get("status") in ["completed", "failed"]:
                created_at = datetime.fromisoformat(job.get("created_at", "1970-01-01T00:00:00"))
                age_hours = (current_time - created_at).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    jobs_to_delete.append(job_id)
        
        for job_id in jobs_to_delete:
            self.delete_job(job_id)
        
        return len(jobs_to_delete)
    
    def get_job_stats(self) -> Dict:
        """Get statistics about jobs"""
        total_jobs = len(self.jobs)
        status_counts = {}
        
        for job in self.jobs.values():
            status = job.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_jobs": total_jobs,
            "status_counts": status_counts,
            "recent_jobs": self._get_recent_jobs(10)
        }
    
    def _get_recent_jobs(self, limit: int) -> list:
        """Get recent jobs sorted by creation time"""
        sorted_jobs = sorted(
            self.jobs.items(),
            key=lambda x: x[1].get("created_at", ""),
            reverse=True
        )
        
        return [
            {
                "job_id": job_id,
                "status": job.get("status"),
                "progress": job.get("progress", 0),
                "created_at": job.get("created_at"),
                "youtube_url": job.get("youtube_url", ""),
                "target_language": job.get("target_language", "")
            }
            for job_id, job in sorted_jobs[:limit]
        ] 