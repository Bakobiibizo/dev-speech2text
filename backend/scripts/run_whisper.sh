#! /bin/bash

filepath=$1

if [ -z "$filepath" ]; then
    echo "Usage: $0 <filepath>"
    exit 1
fi

if [ -f in/audio_data.wav ]; then
    rm in/audio_data.wav
fi  

if [ -f in/output.wav ]; then
    rm in/output.wav
fi

if [ -f out/output.wav ]; then
    rm out/output.wav
fi

if [ -f out/output.wav.txt ]; then
    rm out/output.wav.txt
fi

if [ -f ${filepath} ]; then
    bash scripts/convert_ffmpeg.sh ${filepath}
fi

if [ -f in/output.wav ]; then
    ./main -m ggml-base.en.bin -f in/output.wav -t 32 -di -otxt out/output.txt
fi
