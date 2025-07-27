# YouTube Video Dubber - Setup Guide

This guide will help you set up and run the YouTube Video Dubber application on your system.

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **Memory**: At least 4GB RAM (8GB recommended for longer videos)
- **Storage**: At least 2GB free space for processing videos
- **Internet**: Stable connection for downloading videos and API calls

### Required Software

#### 1. Python 3.8+
```bash
# Check if Python is installed
python3 --version

# If not installed:
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip

# macOS
brew install python3

# Windows
# Download from https://python.org
```

#### 2. FFmpeg
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

#### 3. Node.js (for frontend)
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node

# Windows
# Download from https://nodejs.org
```

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd dubber
```

### 2. Install Python Dependencies
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 4. Configure Environment Variables
```bash
# Copy example environment file
cp env.example .env

# Edit the .env file with your API keys
nano .env  # or use your preferred editor
```

#### Required API Keys

**ElevenLabs API Key** (Required for TTS):
1. Go to [ElevenLabs](https://elevenlabs.io/)
2. Sign up for a free account
3. Go to your profile settings
4. Copy your API key
5. Add it to `.env`: `ELEVENLABS_API_KEY=your_key_here`

**Google Translate API Key** (Optional):
- The app uses the free `googletrans` library by default
- For production use, consider getting a Google Cloud API key

### 5. Environment Configuration

Edit your `.env` file with the following settings:

```env
# API Keys
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
GOOGLE_TRANSLATE_API_KEY=your_google_translate_api_key_here

# App Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# File Storage
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
TEMP_DIR=./temp

# Whisper Configuration
WHISPER_MODEL=base
WHISPER_DEVICE=cpu

# Translation Configuration
TRANSLATION_SERVICE=google

# TTS Configuration
TTS_SERVICE=elevenlabs
TTS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

## Running the Application

### Option 1: Using the Startup Script (Recommended)
```bash
# Make the script executable
chmod +x start.py

# Run the startup script
python3 start.py
```

The startup script will:
- Check all dependencies
- Create necessary directories
- Validate environment configuration
- Start the backend server

### Option 2: Manual Startup

#### Start the Backend
```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Start the FastAPI server
python3 main.py
```

#### Start the Frontend (in a new terminal)
```bash
cd frontend
npm start
```

### 3. Access the Application

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

## Usage

### 1. Basic Usage
1. Open http://localhost:3000 in your browser
2. Enter a YouTube video URL
3. Select your target language
4. Click "Start Dubbing"
5. Monitor the progress
6. Download the completed video

### 2. API Usage
```bash
# Start a dubbing job
curl -X POST "http://localhost:8000/dub" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=example",
    "target_language": "es",
    "source_language": "en"
  }'

# Check job status
curl "http://localhost:8000/status/{job_id}"

# Download completed video
curl "http://localhost:8000/download/{job_id}"
```

## Troubleshooting

### Common Issues

#### 1. FFmpeg Not Found
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Verify installation
ffmpeg -version
```

#### 2. Python Package Installation Errors
```bash
# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# If specific packages fail, install individually
pip install fastapi uvicorn yt-dlp
```

#### 3. Whisper Model Download Issues
```bash
# The first run will download the Whisper model
# This may take several minutes depending on your internet connection
# If it fails, try:
pip install --upgrade openai-whisper
```

#### 4. ElevenLabs API Errors
- Verify your API key is correct
- Check your ElevenLabs account has sufficient credits
- Ensure the API key is properly set in the `.env` file

#### 5. YouTube Download Issues
```bash
# Update yt-dlp
pip install --upgrade yt-dlp

# Some videos may be restricted or unavailable
# Try with a different YouTube video
```

#### 6. Memory Issues
- For longer videos, increase available RAM
- Use a smaller Whisper model: set `WHISPER_MODEL=tiny` in `.env`
- Process shorter video segments

### Performance Optimization

#### 1. GPU Acceleration (Optional)
If you have a CUDA-capable GPU:
```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Set device to GPU in .env
WHISPER_DEVICE=cuda
```

#### 2. Model Selection
- `tiny`: Fastest, least accurate
- `base`: Good balance (default)
- `small`: More accurate, slower
- `medium`: High accuracy, slower
- `large`: Best accuracy, slowest

## Production Deployment

### 1. Environment Variables
```env
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

### 2. Process Management
Use a process manager like `systemd` or `supervisor`:

```ini
# /etc/systemd/system/youtube-dubber.service
[Unit]
Description=YouTube Video Dubber
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/dubber
Environment=PATH=/path/to/dubber/venv/bin
ExecStart=/path/to/dubber/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. Reverse Proxy
Use Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the application logs
3. Ensure all dependencies are properly installed
4. Verify your API keys are correct
5. Try with a simple, short YouTube video first

## License

This project is licensed under the MIT License. 