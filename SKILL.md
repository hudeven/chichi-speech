---
name: qwen3-tts-service
description: A RESTful service for high-quality text-to-speech using Qwen3 and specialized voice cloning. Optimized for reusing a specific voice prompt to avoid re-computation.
---

# Chichi Speech Service

This skill provides a FastAPI-based REST service for Qwen3 TTS, specifically configured for reusing a high-quality reference audio prompt for efficient and consistent voice cloning. This service is packaged as an installable CLI.

## Installation

Run the following command to install the service and client CLIs:

```bash
cd chichi-speech
# Create and activate a virtual environment using uv
uv venv .venv --python 3.10
source .venv/bin/activate

# Install the package
uv pip install -e .
```

## Usage

### 1. Start the Service

The service runs on port **9090** by default.

```bash
# Start the server (runs in foreground, use & for background or a separate terminal)
chichi-speech-server
# OR specify the port explicitly
PORT=9090 chichi-speech-server
# OR use command line flags
chichi-speech-server --port 9090 --host 0.0.0.0
# OR specify a different reference audio path (Recommended)
chichi-speech-server --ref-audio /path/to/my/voice.wav --ref-text "caption of the reference audio"
```

### 2. Generate Speech

Use the client CLI to send requests to the service.

```bash
# Basic usage
chichi-speech-client "你好，我是Qwen TTS助手。" -o output.wav

# Specify language
chichi-speech-client "Hello world" -l English -o hello.wav

# Specify custom service URL explicitly
chichi-speech-client "Test" --url http://localhost:9090
```

## Functionality

-   **Endpoint**: `POST /synthesize`
-   **Default Port**: 9090
-   **Voice Cloning**: Uses a pre-computed voice prompt from reference files to ensure the cloned voice is consistent and generation is fast.

## Requirements

-   Python 3.10+
-   `qwen-tts` (Qwen3 model library)
-   Access to a reference audio file for voice cloning.
    -   By default, it uses public sample audio from Qwen3.
    -   **CRITICAL**: You can provide your own reference audio using the `--ref-audio` flag.
