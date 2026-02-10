# Chichi Speech

**A high-quality, voice-cloning TTS service powered by Qwen3.**

Chichi Speech provides a robust REST API and CLI tools for text-to-speech synthesis, featuring efficient voice cloning capabilities. It is designed to be easily deployed or integrated into other AI agents and workflows.

Acknowledgement: This project is just a simple wrapper of [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS), the SOTA TTS model as of 2/5/2025.

## Features

-   **High Quality**: Utilizes the Qwen3-TTS model for state-of-the-art speech synthesis.
-   **Voice Cloning**: Clone voices from reference audio files.
-   **Efficient**: Optimized for reusing voice prompts to minimize computation for repeated requests.
-   **Production Ready**: Includes scripts for daemonized execution, auto-restart, and concurrency management (via Gunicorn).
-   **Standardized API**: Simple REST API (`/synthesize`) for easy integration.
-   **CLI Tools**: Includes `chichi-speech` and `chichi-speech-client` for immediate use.

## Installation

Prerequisites: `python >= 3.10`.

```bash
pip install chichi-speech

# Recommended: Use uv for faster installation and environment management
uv pip install chichi-speech

```

## Usage

### 1. Start the Service

The service runs on port **9090** by default, using the bundled "Coco" voice.

#### A. Production (Recommended)
Use the included scripts to run as a daemon with auto-restart, logging, and concurrency management.

```bash
# Start the service
./scripts/start_server.sh
# OR with custom voice:
# ./scripts/start_server.sh --ref-audio src/assets/coco.wav --ref-text src/assets/coco.txt

# Stop the service
./scripts/stop_server.sh

# Follow logs
tail -f /tmp/chichi_server.log
```

#### B. Quick Start / Development
Run directly in the foreground:

```bash
# Start with defaults (bundled "Coco" voice)
chichi-speech

# OR specify custom port and host
chichi-speech --port 9090 --host 0.0.0.0

# OR specify your own reference audio and text for voice cloning
chichi-speech --ref-audio src/assets/coco.wav --ref-text src/assets/coco.txt
```

### 2. Verify Service is Running
Check the health/docs:
```bash
curl http://localhost:9090/docs
```

### 3. Generate Speech

Use cURL:
```bash
curl -X POST "http://localhost:9090/synthesize" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "Nice to meet you",
           "language": "English"
         }' \
     --output output/nice_to_meet.wav
```

## Functionality
-   **Endpoint**: `POST /synthesize`
-   **Default Port**: 9090
-   **Voice Cloning**: Uses a pre-computed voice prompt from reference files to ensure the cloned voice is consistent and generation is fast.

# Development

Install dev dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

## License

MIT
