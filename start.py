#!/usr/bin/env python3
"""
YouTube Video Dubber - Startup Script
This script sets up the environment and starts the application.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    # Check if FFmpeg is installed
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✓ FFmpeg is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ FFmpeg is not installed. Please install FFmpeg first:")
        print("  Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return False
    
    # Check if Python packages are installed
    required_packages = [
        'fastapi', 'uvicorn', 'yt-dlp', 'openai-whisper', 
        'googletrans', 'elevenlabs', 'pydub', 'ffmpeg-python'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} is not installed")
    
    if missing_packages:
        print(f"\nPlease install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def setup_directories():
    """Create necessary directories"""
    print("Setting up directories...")
    
    directories = ['uploads', 'outputs', 'temp']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_environment():
    """Check environment variables"""
    print("Checking environment...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            print("⚠ .env file not found. Please copy env.example to .env and configure your API keys.")
            print("  cp env.example .env")
            return False
        else:
            print("⚠ No environment configuration found.")
            return False
    
    # Check for required API keys
    required_keys = ['ELEVENLABS_API_KEY']
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print(f"⚠ Missing API keys: {', '.join(missing_keys)}")
        print("Please set these in your .env file")
        return False
    
    print("✓ Environment is configured")
    return True

def main():
    """Main startup function"""
    print("YouTube Video Dubber - Starting up...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing dependencies.")
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Check environment
    if not check_environment():
        print("\n⚠ Environment check failed. Some features may not work.")
        print("You can still start the application, but API features will be limited.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 All checks passed! Starting the application...")
    print("=" * 50)
    
    # Start the application
    try:
        from main import app
        import uvicorn
        
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8000))
        debug = os.getenv("DEBUG", "False").lower() == "true"
        
        print(f"Starting server on http://{host}:{port}")
        print("Press Ctrl+C to stop the server")
        
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 