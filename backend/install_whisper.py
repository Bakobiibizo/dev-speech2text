import subprocess
from pathlib import Path
from utilities.endpoint_configs import EndpointConfigManager

manager = EndpointConfigManager()

config = manager.speech2text


filename = "output"
filepath = "in/output.wav"
run_script = "scripts/run_whisper.sh"

subprocess.run(["pip", "install", "loguru", "-q"], check=True)

from loguru import logger

install_whisper_sh = """#!/bin/bash

# Update apt
apt update && apt upgrade -y

# Install dependencies
apt install -y python3.10 python3-pip build-essential libssl-dev libffi-dev python3-dev python3-venv python3-setuptools wget curl libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libxslt1.1 libxslt1-dev libxml2 libxml2-dev python-is-python3 libpugixml-dev libtbb-dev git git-lfs ffmpeg libclblast-dev cmake make 

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Update pip
python -m pip install --upgrade pip
pip install wheel setuptools
pip install -r requirements.txt

# Install whisper

# Install whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
make clean
WHISPER_CBLAST=1 make -j

# Download Whisper model
bash models/download-ggml-model.sh base.en
    
# Make in and out dirs
cd .. 
mkdir -p in out

mv whisper.cpp/main .
mv whisper.cpp/models/ggml-base.en.bin .
mv whisper.cpp/samples/jfk.wav in

"""
example_sh = """#! /bin/bash

python convert_file.py -f in/jfk.wav

python whisper.py -f in/jfk.wav -m ggml-base.en.bin -w ./main
"""

convert_file_py = """import argparse
import subprocess
from pathlib import Path

path = Path


def convert_to_wav(file_path):
    input_name = path.cwd() / file_path
    output_name = input_name.name.format("wav")
    output_path = path.cwd() / "out" / output_name
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            f"{input_name}",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            f"{output_path}",
        ],
        check=True,
    )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file_path", type=str, required=True)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    file_path = parse_args().file_path
    convert_to_wav(file_path)
"""

whisper_py = """import argparse
import subprocess
from pathlib import Path

subprocess.run(["pip", "install", "loguru", "-q"], check=True)

from loguru import logger

path = Path


def run_whisper(
    whisper_bin="./main",
    file_path="in/jfk.wav",
    model_path="ggml-base.en.bin",
):
    file_path = path.cwd() / file_path
    model_path = path.cwd() / model_path
    try:
        result = subprocess.run(
            [f"{whisper_bin}", "-m", f"{model_path}", "-f", f"{file_path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        logger.debug(result.stdout.decode("utf-8"))
        return result.stdout.decode("utf-8")
    except subprocess.CalledProcessError as error:
        logger.error(error)
        return error
    except RuntimeError as error:
        logger.error(error)
        return error


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--file_path", default="in/jfk.wav", type=str, required=False
    )
    parser.add_argument(
        "-m",
        "--model_path",
        default="ggml-base.en.bin",
        type=str,
        required=False,
    )
    parser.add_argument("-w", "--whisper_bin", default="./main", type=str)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    run_whisper(**vars(args))
"""

api_py = f"""import base64
import subprocess
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

path = Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TranscribeRequest(BaseModel):
    data: str
    filename: str


run_script = path.cwd() / "run.sh"

run_script.chmod(0o777)


@app.post(f"{manager.version}{config.endpoint}")
def transcribe(user_request: TranscribeRequest):
    filename = user_request.filename
    filepath = path.cwd() / "in" / f"{'filename'}.wav"
    data = base64.b64decode(user_request.data)
    filepath.write_bytes(data)
    resp = subprocess.run(
        ["bash", f"{'run_script'}", f"{'filepath'}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=600,
    )

    response = resp.stdout
    print(response)

    return response


if __name__ == "__main__":
    uvicorn.run("api:app", host="{config.host}", port=int({config.port}), reload=True)
"""


run_sh = """#! /bin/bash

export WHISPER_CUDA=1
export WHISPER_CLBLAS=1

volumes/models/whisper/whisper.cpp/main -m volumes/models/whisper/ggml-large-v2.bin -f output.wav -t 32 -di -otxt converted.txt 

"""

requirements_txt = """fastapi
uvicorn
loguru
requests"""

run_api_sh = """"""

Dockerfile = """FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip \
    && pip install setuptools wheel

WORKDIR /app

COPY . /app/

EXPOSE 4900:4900

RUN pip install -r requirements.txt

CMD ["python", "run_api.py"]
"""
docker_compose_yaml = f"""version: "3"
services:
  whisper:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: whisper
    ports:
      - 4900:4900
    volumes:
      - .:/app
    working_dir: /app
    command: bash run_api.sh
  ngrok:
    image: ngrok/ngrok:latest
    restart: unless-stopped
    command:
      - "start"
      - "--all"
      - "--config"
      - "/etc/ngrok.yml"
    volumes:
      - ./ngrok.yml:/etc/ngrok.yml
    ports:
      - {config.port}:{config.port}
"""

paths = {
    "install_whisper_sh": "install_whisper.sh",
    "example_sh": "example.sh",
    "convert_file_py": "convert_file.py",
    "whisper_py": "whisper.py",
    "api_py": "api.py",
    "run_sh": "run.sh",
    "requirements_txt": "requirements.txt",
    "run_api_sh": "run_api.sh",
    "Dockerfile": "Dockerfile",
    "docker_compose_yaml": "docker-compose.yaml",
}

data = {
    "install_whisper_sh": install_whisper_sh,
    "example_sh": example_sh,
    "convert_file_py": convert_file_py,
    "whisper_py": whisper_py,
    "api_py": api_py,
    "run_sh": run_sh,
    "requirements_txt": requirements_txt,
    "run_api_sh": run_api_sh,
    "Dockerfile": Dockerfile,
    "docker_compose_yaml": docker_compose_yaml,
}

path = Path


def write_file(file_data: str, file_path: str) -> None:
    logger.debug(f"\\nfile_data: {file_data}\\nfile_path: {file_path}\\n")
    save_path = path.cwd() / file_path
    save_path.write_text(file_data)
    save_path.chmod(0o777)


for file, pat in paths.items():
    write_file(data[file], paths[file])
    logger.debug(f"\\nfile: {file}\\n")

subprocess.run(["bash", "./install_whisper.sh"], check=True)
