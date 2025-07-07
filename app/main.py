import os
import tempfile
import asyncio
from pathlib import Path
from typing import Optional
import logging

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import librosa
import soundfile as sf
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Audio Transcription API", version="1.0.0")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global variables for model and pipeline
model = None
processor = None
pipe = None

# Model configuration
MODEL_ID = "syvai/hviske-v3-conversation"
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
TORCH_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32

# Supported audio formats
SUPPORTED_FORMATS = {'.wav', '.mp3', '.mp4', '.m4a', '.flac', '.ogg', '.webm'}

@app.on_event("startup")
async def startup_event():
    """Initialize the model and pipeline on startup"""
    global model, processor, pipe
    
    logger.info(f"Loading model {MODEL_ID} on device {DEVICE}")
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    
    try:
        # Load model
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            MODEL_ID, 
            torch_dtype=TORCH_DTYPE, 
            low_cpu_mem_usage=True
        )
        model.to(DEVICE)
        
        # Load processor
        processor = AutoProcessor.from_pretrained(MODEL_ID)
        
        # Create pipeline
        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            chunk_length_s=30,
            batch_size=16,  # batch size for inference
            torch_dtype=TORCH_DTYPE,
            device=DEVICE,
        )
        
        logger.info("Model loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise

def convert_to_16khz(audio_path: str) -> str:
    """Convert audio file to 16kHz and return path to converted file"""
    try:
        # Load audio file
        audio, sample_rate = librosa.load(audio_path, sr=None)
        
        # Convert to 16kHz if needed
        if sample_rate != 16000:
            audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)
        
        # Create temporary file for converted audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_path = temp_file.name
        temp_file.close()
        
        # Save converted audio
        sf.write(temp_path, audio, 16000)
        
        return temp_path
        
    except Exception as e:
        logger.error(f"Error converting audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error converting audio: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main HTML page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": pipe is not None,
        "device": DEVICE,
        "cuda_available": torch.cuda.is_available()
    }

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe uploaded audio file"""
    if not pipe:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    # Check file format
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )
    
    temp_original = None
    temp_converted = None
    
    try:
        # Save uploaded file temporarily
        temp_original = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        content = await file.read()
        temp_original.write(content)
        temp_original.close()
        
        logger.info(f"Processing file: {file.filename}")
        
        # Convert to 16kHz
        temp_converted = convert_to_16khz(temp_original.name)
        
        # Transcribe
        result = pipe(temp_converted)
        
        logger.info("Transcription completed successfully")
        
        return JSONResponse(content={
            "filename": file.filename,
            "transcription": result["text"],
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")
    
    finally:
        # Clean up temporary files
        for temp_file in [temp_original, temp_converted]:
            if temp_file and os.path.exists(temp_file.name if hasattr(temp_file, 'name') else temp_file):
                try:
                    os.unlink(temp_file.name if hasattr(temp_file, 'name') else temp_file)
                except:
                    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 