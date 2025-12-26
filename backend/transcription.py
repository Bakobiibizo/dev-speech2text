import base64
import subprocess
import uvicorn
from pathlib import Path
from fastapi.routing import APIRouter
from dotenv import load_dotenv
from loguru import logger
from utilities.data_models import TranscriptionRequest
from utilities.endpoint_configs import EndpointConfigManager

manager = EndpointConfigManager()
config = manager.speech2text
inpath = "speech2text_generation/in"
outpath = "speech2text_generation/out"
load_dotenv()

router = APIRouter()

logger.info(config.endpoint)


@logger.catch
@router.post(config.endpoint)
def transcribe(completion: TranscriptionRequest):
    logger.info("Transcribing")
    audio_bytes = base64.b64decode(completion.audio)

    with open(f"{inpath}/audio.wav", "wb") as file:
        file.write(audio_bytes)
    temp_path = convert_ffmpeg(f"{inpath}/audio.wav")
    run_whisper(temp_path)
    return Path(outpath).read_text("utf-8")


def convert_ffmpeg(in_path):
    output = subprocess.run(
        ["bash", "scripts/convert_ffmpeg.sh", f"{in_path}"],
        check=True,
        capture_output=True,
    )
    print(output)
    return output


def run_whisper(temp_path):
    command = [
        "bash",
        "scripts/run_whisper.sh",
        f"{temp_path}",
    ]
    print(command)
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        response = result.stdout.decode("utf-8")
        logger.debug(response)
        return response
    except subprocess.CalledProcessError as error:
        logger.error(error)
        return error


if __name__ == "__main__":
    uvicorn.run(
        "transcription:app",
        host=f"{config.host}",
        port=int(str(config.port)),
        reload=True,
    )
