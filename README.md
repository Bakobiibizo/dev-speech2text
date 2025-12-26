# dev-speech2text

Whisper/ASR proxy backend for speech-to-text.

## Requirements
- Docker + GPU recommended (CPU works but slower)
- Built/tested on **aarch64**. For x86_64, use matching base image tag and rebuild locally.

## Build
```bash
docker build -t inference/speech2text:local .
```

## Run (standalone)
```bash
docker run --gpus all -d -p 7100:7100 inference/speech2text:local
```

## Run with docker-compose (root of repo)
```bash
docker compose up speech2text
```

## Test
Health:
```bash
curl http://localhost:7100/health
```

ASR (example payload depends on proxy; see service docs):
```bash
curl -X POST http://localhost:7100/asr ...
```
