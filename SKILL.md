---
name: chichi-speech-skill
description: A RESTful service for high-quality text-to-speech using Qwen3 and specialized voice cloning. Optimized for reusing a specific voice prompt to avoid re-computation.
---

# Chichi Speech Service

This skill provides a FastAPI-based REST service for Qwen3 TTS, specifically configured for reusing a high-quality reference audio prompt for efficient and consistent voice cloning. This service is packaged as an installable CLI.

## Installation

Prerequisites: `git`, `uv`, `python >= 3.10`.

```bash
export CHICHI_SPEECH_HOME="~/chichi-speech/"
git clone https://github.com/yourusername/chichi-speech.git $CHICHI_SPEECH_HOME
cd $CHICHI_SPEECH_HOME

uv venv .venv --python 3.10
source .venv/bin/activate

uv pip install -e .
```

## Usage

### 1. Start the Service

The service runs on port **9090** by default.

```bash
# Start the server (runs in foreground, use & for background or a separate terminal)
source $CHICHI_SPEECH_HOME/.venv/bin/activate
chichi-speech-server
# OR specify the port explicitly
chichi-speech-server --port 9090 --host 0.0.0.0
# OR specify a different reference audio path (Recommended)
chichi-speech-server --ref-audio /path/to/my/voice.wav --ref-text "caption of the reference audio"
```

### 2. Verify Service is Running
Check the health/docs:
```bash
curl http://localhost:9090/docs
```

### 3. Generate Speech

**Option A: Using Client CLI**
```bash
# Basic usage
source $CHICHI_SPEECH_HOME/.venv/bin/activate
chichi-speech-client "你好，我是Qwen TTS助手。" -o /tmp/output.wav

# Specify language
chichi-speech-client "Hello world" -l English -o /tmp/hello.wav
```

**Option B: Using CURL (Direct API)**
```bash
curl -X POST "http://localhost:9090/synthesize" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "Hello world",
           "language": "English"
         }' \
     --output /tmp/output.wav
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
