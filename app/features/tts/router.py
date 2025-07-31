from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from piper import PiperVoice
import io
import wave
import os
import logging

router = APIRouter(prefix="/chat", tags=["chat"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
MODEL_DIR = os.path.join(BASE_DIR, "models", "tss-model")
os.makedirs(MODEL_DIR, exist_ok=True)

# Verify model files
VOICE_CONFIG = {
    "male": {
        "model": "en_US-ryan-medium.onnx",
        "json": "en_US-ryan-medium.onnx.json"
    },
    "female": {
        "model": "en_US-libritts-high.onnx", 
        "json": "en_US-libritts-high.onnx.json"
    }
}

# Load voices
voices = {}
for gender, files in VOICE_CONFIG.items():
    try:
        model_path = os.path.join(MODEL_DIR, files["model"])
        if not os.path.exists(model_path):
            logger.error(f"Missing model file: {model_path}")
            continue
            
        logger.info(f"Loading {gender} voice from: {model_path}")
        voices[gender] = PiperVoice.load(model_path)
        logger.info(f"{gender.capitalize()} voice loaded successfully")
    except Exception as e:
        logger.error(f"Error loading {gender} voice: {str(e)}")

if not voices:
    raise RuntimeError("No voice models could be loaded")

@router.post("/tts")
async def generate_speech(
    text: str = Query(..., min_length=1, max_length=500),
    gender: str = Query("male", regex="^(male|female)$")
):
    """Generate speech audio from text"""
    try:
        # Validate input
        gender = gender.lower()
        if gender not in voices:
            raise HTTPException(400, detail=f"Voice '{gender}' not available")
            
        text = text.strip()
        if not text:
            raise HTTPException(400, detail="Text cannot be empty")

        # Generate PCM audio
        pcm_buffer = io.BytesIO()
        voices[gender].synthesize(text, pcm_buffer)
        pcm_buffer.seek(0)
        
        # Convert to WAV format
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(22050)  # 22.05 kHz
            wav_file.writeframes(pcm_buffer.getvalue())
            
        wav_buffer.seek(0)
        audio_data = wav_buffer.read()
        
        # Validate audio
        if len(audio_data) < 44:  # WAV header size
            raise ValueError("Generated audio is too small")

        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=speech.wav",
                "Content-Length": str(len(audio_data))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS Error: {str(e)}", exc_info=True)
        raise HTTPException(500, detail="Audio generation failed")