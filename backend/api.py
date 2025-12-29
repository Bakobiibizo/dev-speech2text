"""Speech2Text Backend API.

Exposes /transcribe endpoint for the Rust proxy.
Uses whisper.cpp for transcription.
"""

import base64
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
# Prefer explicit env; default to repo mount (/workspace/backend) then legacy /opt/whisper.
WHISPER_DIR_PRIMARY = Path(os.getenv("WHISPER_DIR", "/workspace/backend"))
WHISPER_DIR_FALLBACK = Path("/opt/whisper")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "ggml-base.en.bin")
WHISPER_THREADS = int(os.getenv("WHISPER_THREADS", "32"))
WHISPER_DEFAULT_LANG = os.getenv("WHISPER_LANG", "en")


class TranscribeRequest(BaseModel):
    audio: str  # base64 encoded audio
    filename: str = "input.wav"


class TranscribeResponse(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/transcribe")
def transcribe(request: TranscribeRequest) -> TranscribeResponse:
    """Transcribe audio to text using whisper.cpp."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Write input audio
        input_path = tmpdir / request.filename
        audio_bytes = base64.b64decode(request.audio)
        input_path.write_bytes(audio_bytes)
        
        # Convert to WAV if needed
        wav_path = tmpdir / "converted.wav"
        convert_cmd = [
            "ffmpeg", "-i", str(input_path),
            "-af", "pan=stereo|c0=c0|c1=c1",
            "-ar", "16000", "-ac", "2",
            "-acodec", "pcm_s16le",
            "-y", str(wav_path)
        ]
        subprocess.run(convert_cmd, check=True, capture_output=True, timeout=300)
        
        # Run whisper
        # Resolve whisper binary and model by probing locations
        candidate_dirs = [WHISPER_DIR_PRIMARY, WHISPER_DIR_FALLBACK]
        main_binary = None
        model_path = None

        for d in candidate_dirs:
            if (d / "whisper-cli").exists():
                main_binary = d / "whisper-cli"
                break
        if main_binary is None:
            for d in candidate_dirs:
                if (d / "main").exists():
                    main_binary = d / "main"
                    break
        if main_binary is None:
            return TranscribeResponse(text="[whisper error] whisper binary not found (whisper-cli or main)")

        for d in candidate_dirs:
            if (d / WHISPER_MODEL).exists():
                model_path = d / WHISPER_MODEL
                break
        if model_path is None:
            return TranscribeResponse(text=f"[whisper error] model not found: {WHISPER_MODEL}")

        threads = min(WHISPER_THREADS, max(os.cpu_count() or 1, 1))

        whisper_cmd = [
            str(main_binary),
            "-m", str(model_path),
            "-f", str(wav_path),
            "-t", str(threads),
            "-otxt",
            "-l", WHISPER_DEFAULT_LANG,
            "-ng",  # force CPU to avoid GPU/driver issues
        ]
        try:
            subprocess.run(
                whisper_cmd,
                check=True,
                capture_output=True,
                cwd=str(tmpdir),
                timeout=600,
            )
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode("utf-8", errors="ignore") if e.stderr else ""
            out = e.stdout.decode("utf-8", errors="ignore") if e.stdout else ""
            # Surface detailed error for debugging
            return TranscribeResponse(text=f"[whisper error] {e} stdout: {out[:500]} stderr: {err[:500]}")
        
        # Read output
        txt_path = Path(str(wav_path) + ".txt")
        if txt_path.exists():
            text = txt_path.read_text().strip()
        else:
            text = ""
        
        return TranscribeResponse(text=text)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "7100"))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)
