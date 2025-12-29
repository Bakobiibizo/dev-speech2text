#!/bin/bash

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

mv whisper.cpp/build/bin/whisper-cli .
mv whisper.cpp/models/ggml-base.en.bin .
mv whisper.cpp/samples/jfk.wav in

