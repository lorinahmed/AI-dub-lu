#!/usr/bin/env python3
"""
YouTube Video Dubber - Setup Test Script
This script tests all components to ensure they're working correctly.
"""

import os
import sys
import asyncio
import tempfile
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    packages = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('yt_dlp', 'yt_dlp'),
        ('whisper', 'whisper'),
        ('googletrans', 'googletrans'),
        ('elevenlabs', 'elevenlabs'),
        ('ffmpeg', 'ffmpeg'),
        ('dotenv', 'dotenv'),
    ]
    
    failed_imports = []
    
    for package, module in packages:
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package}: {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

def test_ffmpeg():
    """Test if FFmpeg is available"""
    print("\nTesting FFmpeg...")
    
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ FFmpeg is available")
            return True
        else:
            print("✗ FFmpeg returned error")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
        print(f"✗ FFmpeg not found: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\nTesting environment...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['ELEVENLABS_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"✗ Missing: {var}")
        else:
            print(f"✓ Found: {var}")
    
    return len(missing_vars) == 0

async def test_services():
    """Test service components"""
    print("\nTesting services...")
    
    try:
        # Test YouTube downloader
        from services.youtube_downloader import YouTubeDownloader
        downloader = YouTubeDownloader()
        print("✓ YouTube downloader initialized")
        
        # Test transcriber
        from services.transcriber import Transcriber
        transcriber = Transcriber()
        print("✓ Transcriber initialized")
        
        # Test translator
        from services.translator import Translator
        translator = Translator()
        print("✓ Translator initialized")
        
        # Test TTS service
        from services.tts_service import TTSService
        tts = TTSService()
        print("✓ TTS service initialized")
        
        # Test video processor
        from services.video_processor import VideoProcessor
        processor = VideoProcessor()
        print("✓ Video processor initialized")
        
        # Test job manager
        from utils.job_manager import JobManager
        job_manager = JobManager()
        print("✓ Job manager initialized")
        
        return True
        
    except Exception as e:
        print(f"✗ Service test failed: {e}")
        return False

def test_directories():
    """Test directory creation"""
    print("\nTesting directories...")
    
    directories = ['uploads', 'outputs', 'temp']
    created_dirs = []
    
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            created_dirs.append(directory)
            print(f"✓ Created: {directory}")
        except Exception as e:
            print(f"✗ Failed to create {directory}: {e}")
    
    return len(created_dirs) == len(directories)

async def test_translation():
    """Test translation service"""
    print("\nTesting translation...")
    
    try:
        from services.translator import Translator
        translator = Translator()
        
        # Test translation
        result = await translator.translate("Hello world", "es")
        if result and len(result) > 0:
            print(f"✓ Translation test passed: 'Hello world' -> '{result}'")
            return True
        else:
            print("✗ Translation returned empty result")
            return False
            
    except Exception as e:
        print(f"✗ Translation test failed: {e}")
        return False

def test_whisper_model():
    """Test Whisper model loading"""
    print("\nTesting Whisper model...")
    
    try:
        import whisper
        model = whisper.load_model("tiny")  # Use tiny model for quick test
        print("✓ Whisper model loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Whisper model test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("YouTube Video Dubber - Setup Test")
    print("=" * 40)
    
    tests = [
        ("Package Imports", test_imports),
        ("FFmpeg", test_ffmpeg),
        ("Environment", test_environment),
        ("Directories", test_directories),
        ("Whisper Model", test_whisper_model),
        ("Services", test_services),
        ("Translation", test_translation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        return True
    else:
        print("⚠ Some tests failed. Please check the setup guide.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 