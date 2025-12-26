import json
import base64
import argparse
import requests
from loguru import logger
from pathlib import Path
import os
from pydantic import BaseModel
from utilities.data_models import TranscriptionComplete
from utilities.endpoint_configs import EndpointConfigManager

manager = EndpointConfigManager()

config = manager.speech2text


def transcribe(
    file_path="download.wav",
    temperature="0.0",
    temperature_inc="0.2",
    response_format="json",
):
    with open(file_path, "rb") as file:
        data = base64.b64encode(file.read()).decode("utf-8")
    # normal

    transcription_request = TranscriptionComplete(
        audio=data,
        audio_filename=file_path
    )
    #logger.debug(transcription_request)

    resp = requests.post(
        url=f"http://{config.host}:{config.port}{config.endpoint}",
        json=transcription_request.model_dump(),
        timeout=6000,
    )
    if resp.status_code == 200:
        return resp.json()
    logger.error(resp.status_code)

    return resp


if __name__ == "__main__":
    response = transcribe("download.wav")
    print(response)
