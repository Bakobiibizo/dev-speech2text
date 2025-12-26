#! /bin/bash

python convert_file.py -f in/jfk.wav

python whisper.py -f in/jfk.wav -m ggml-base.en.bin -w ./main
