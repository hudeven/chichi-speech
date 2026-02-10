---
name: chichi-speech
description: A RESTful service for high-quality text-to-speech using Qwen3 and specialized voice cloning. Optimized for reusing a specific voice prompt to avoid re-computation.
metadata: {"openclaw":{"always":true,"emoji":"🦞","homepage":"https://github.com/hudeven/chichi-speech/blob/main/SKILL.md","os":["darwin","linux"],"tags":["python","tts", "text-to-speech", "voice-cloning"],"requires":{"anyBins":["brew","uv"]}}}
---

# Chichi Speech Service

This skill provides a FastAPI-based REST service for Qwen3 TTS, specifically configured for reusing a high-quality reference audio prompt for efficient and consistent voice cloning. This service is packaged as an installable CLI.

## Installation

Prerequisites: `uv` and `python >= 3.10`.

### If uv not installed, install it first
```bash
command -v uv || brew install uv || (curl -LsSf https://astral.sh/uv/install.sh | sh)
```
### Install chichi-speech
```bash
export CHICHI_SPEECH_VENV="/Users/$USER/envs/chichi-speech"
uv venv $CHICHI_SPEECH_VENV --allow-existing
source $CHICHI_SPEECH_VENV/bin/activate
uv pip install -e .
```

## Usage

### 1. Start the Service

The service runs on port **9090** by default.

```bash
# Production: Use the included script to run as a daemon with auto-restart
./scripts/start_server.sh --ref-audio src/assets/coco.wav --ref-text src/assets/coco.txt

# To stop:
# ./scripts/stop_server.sh

# Logs are written to /tmp/chichi_server.log
```

### 2. Verify Service is Running
Wait for ~15s for model to be loaded. Then Check the health/docs:
```bash
sleep 15 && curl http://localhost:9090/docs
```

### 3. Generate Speech
If the "text" is longer than 10 sentences, split it to smaller chunks(10 sentences per chunk) and synthesized separately.
Specify the "language" based on the input "text".
Available languages:
- Chinese
- English
- Japanese
- Korean
- German
- French
- Russian
- Portuguese
- Spanish
- Italian

```bash
curl -X POST "http://localhost:9090/synthesize" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "Nice to meet you",
           "language": "auto",
           "format": "ogg"
         }' \
     --output output/nice_to_meet.ogg
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
    -   **CRITICAL**: You can provide your own reference audio using the `--ref-audio` and `--ref-text` flags.
