# 🎙️ Tale Transskription Service

A FastAPI-based speech transcription service using the `syvai/hviske-v3-conversation` model with GPU support. This service provides a beautiful web interface for uploading audio files and getting transcriptions (Danish interface).

## Features

- **GPU-accelerated transcription** using NVIDIA CUDA
- **Multiple audio format support**: WAV, MP3, MP4, M4A, FLAC, OGG, WEBM
- **Automatic 16kHz conversion** for optimal transcription quality
- **Modern web interface** with drag-and-drop file upload and microphone recording (Danish language)
- **Direct microphone recording** with real-time audio level monitoring
- **Real-time progress tracking** and error handling
- **RESTful API** for programmatic access
- **Docker support** with GPU acceleration
- **Health check endpoints** for monitoring

## Requirements

### System Requirements
- NVIDIA GPU with CUDA support (recommended)
- Docker with NVIDIA Container Toolkit (for Docker deployment)
- Python 3.8+ (for local development)
- Modern web browser with microphone access (for recording feature)

### GPU Support
This service is optimized for GPU acceleration. While it will run on CPU, GPU usage significantly improves transcription speed.

## Quick Start with Docker

### 1. Prerequisites
Make sure you have Docker and NVIDIA Container Toolkit installed:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### 2. Build and Run

```bash
# Clone the repository
git clone <your-repo-url>
cd hviske-demo

# Build and start the service
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

The service will be available at `http://localhost:8000`

### 3. Check Service Health

```bash
curl http://localhost:8000/health
```

## Local Development

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Service

```bash
# Start the FastAPI server
python app/main.py

# Or use uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Usage

### Web Interface
Visit `http://localhost:8000` to access the web interface (Danish language).

**Features:**
- **File Upload**: Drag and drop audio files or click to browse
- **Microphone Recording**: Record directly from your microphone with real-time audio level monitoring
- **Progress Tracking**: See upload and processing progress
- **Results Display**: View transcription results with copy functionality
- **Danish Interface**: All text and instructions are in Danish

### REST API

#### Upload and Transcribe Audio File

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_audio_file.wav"
```

**Response:**
```json
{
  "filename": "your_audio_file.wav",
  "transcription": "This is the transcribed text from your audio file.",
  "status": "success"
}
```

#### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda:0",
  "cuda_available": true
}
```

## Project Structure

```
hviske-demo/
├── app/
│   └── main.py              # FastAPI application
├── templates/
│   └── index.html           # Web interface
├── static/                  # Static assets
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # This file
```

## Configuration

### Environment Variables

- `CUDA_VISIBLE_DEVICES`: GPU device ID (default: 0)
- `PYTHONPATH`: Python path (default: /app)

### Model Configuration

The service uses the `syvai/hviske-v3-conversation` model. You can modify the model ID in `app/main.py`:

```python
MODEL_ID = "syvai/hviske-v3-conversation"
```

## Supported Audio Formats

- **WAV** - Waveform Audio File Format
- **MP3** - MPEG Audio Layer III
- **MP4** - MPEG-4 Part 14
- **M4A** - MPEG-4 Audio
- **FLAC** - Free Lossless Audio Codec
- **OGG** - Ogg Vorbis
- **WEBM** - WebM audio

All uploaded files are automatically converted to 16kHz for optimal transcription quality.

## Performance Considerations

- **GPU Memory**: The model requires significant GPU memory. Adjust `batch_size` in `app/main.py` based on your GPU capacity.
- **Audio Length**: Longer audio files take more time to process. The service processes audio in 30-second chunks.
- **File Size**: Large audio files may take longer to upload and process.

## Troubleshooting

### Common Issues

1. **Model Loading Failed**
   - Ensure you have sufficient GPU memory
   - Check internet connection for model download
   - Verify CUDA installation

2. **CUDA Out of Memory**
   - Reduce `batch_size` in `app/main.py`
   - Use smaller audio files
   - Restart the service

3. **Service Not Starting**
   - Check Docker logs: `docker-compose logs`
   - Verify port 8000 is available
   - Ensure NVIDIA Container Toolkit is installed

### Logs

```bash
# View Docker logs
docker-compose logs -f

# View health status
curl http://localhost:8000/health
```

## Development

### Adding New Features

1. **New Audio Formats**: Add format to `SUPPORTED_FORMATS` in `app/main.py`
2. **Custom Models**: Modify `MODEL_ID` and adjust pipeline configuration
3. **Additional Endpoints**: Add new FastAPI routes in `app/main.py`

### Testing

```bash
# Test with sample audio file
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@test_audio.wav"
```

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please open an issue in the repository. 