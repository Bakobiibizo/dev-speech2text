#! /bin/bash

export WHISPER_CUDA=1
export WHISPER_CLBLAS=1

volumes/models/whisper/whisper.cpp/main -m volumes/models/whisper/ggml-large-v2.bin -f output.wav -t 32 -di -otxt converted.txt 

