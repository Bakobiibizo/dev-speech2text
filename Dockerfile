# Speech2Text Proxy + Backend
# Bundles the Rust proxy with the Python/whisper.cpp backend

FROM rust:1.83-bookworm AS builder

WORKDIR /build
COPY Cargo.toml ./
COPY src ./src
RUN cargo build --release

# Runtime image
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    python3 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Rust binary
COPY --from=builder /build/target/release/dev-speech2text /app/proxy

# Copy backend code
COPY backend/ /app/backend/

# Install Python dependencies
RUN python3 -m pip install --no-cache-dir --break-system-packages \
    fastapi uvicorn pydantic

# Environment defaults
# Proxy listens on 7100, backend on internal port 8100
ENV API_HOST=0.0.0.0
ENV API_PORT=7100
ENV BACKEND_URL=http://localhost:8100
ENV BACKEND_CMD=python3
ENV BACKEND_ARGS="-m uvicorn api:app --host 0.0.0.0 --port 8100"
ENV BACKEND_WORKDIR=/app/backend
ENV BACKEND_PORT=8100
ENV BACKEND_HEALTH_PATH=/health
ENV WHISPER_DIR=/app/backend
ENV PRELOAD=true

EXPOSE 7100

CMD ["/app/proxy"]
