from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
import tempfile
import os

app = FastAPI(title="Whisper Assistant API")

# Initialize the model (already downloaded during build)
whisper_model = WhisperModel("large-v3", device="cuda", compute_type="float16")


@app.post("/v1/audio/transcriptions")
async def transcribe_audio(
    file: UploadFile = File(...),
    model_name: str = "whisper-1",  # Renamed parameter to avoid conflict
    language: str = "en",
):
    """Transcribe audio file to text"""
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file.flush()

        # Transcribe the audio
        segments, info = whisper_model.transcribe(
            temp_file.name, language=language, vad_filter=True
        )

        # Format response to match OpenAI API
        formatted_segments = []
        for i, segment in enumerate(segments):
            formatted_segments.append(
                {
                    "id": i,
                    "seek": 0,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "tokens": [],
                    "temperature": 0.0,
                }
            )

        # Clean up temp file
        os.unlink(temp_file.name)

        return {
            "text": " ".join(seg["text"] for seg in formatted_segments),
            "segments": formatted_segments,
            "language": info.language,
        }


@app.get("/v1/health")
async def health_check():
    """Check if the API is running"""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Get API information and available endpoints"""
    return {
        "message": "Whisper Assistant API",
        "docs": "/docs",
        "health_check": "/v1/health",
        "transcribe": "/v1/audio/transcriptions",
    }
