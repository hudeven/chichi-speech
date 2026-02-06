# Chichi Speech

**A high-quality, voice-cloning TTS service powered by Qwen3.**

Chichi Speech provides a robust REST API and CLI tools for text-to-speech synthesis, featuring efficient voice cloning capabilities. It is designed to be easily deployed or integrated into other AI agents and workflows.

## Features

-   **High Quality**: Utilizes the Qwen3-TTS model for state-of-the-art speech synthesis.
-   **Voice Cloning**: Clone voices from reference audio files.
-   **Efficient**: Optimized for reusing voice prompts to minimize computation for repeated requests.
-   **Standardized API**: Simple REST API (`/synthesize`) for easy integration.
-   **CLI Tools**: Includes `chichi-speech-server` and `chichi-speech-client` for immediate use.

## Installation

Prerequisites: `git`, `uv`, `python >= 3.10`.

```bash
export CHICHI_SPEECH_HOME="~/chichi-speech/"
export CHICHI_SPEECH_ENV="~/chichi-speech/.venv"
git clone https://github.com/yourusername/chichi-speech.git $CHICHI_SPEECH_HOME
cd $CHICHI_SPEECH_HOME

uv venv $CHICHI_SPEECH_ENV --python 3.10
source $CHICHI_SPEECH_ENV/bin/activate

uv pip install -e .
```

## Usage

### 1. Start the Service

The service runs on port **9090** by default.

```bash
# Start the server (runs in foreground, use & for background or a separate terminal)
source $$CHICHI_SPEECH_ENV/bin/activate
chichi-speech-server
# OR specify the port explicitly
chichi-speech-server --port 9090 --host 0.0.0.0
# OR specify your reference audio and text for voice cloning (Recommended)
chichi-speech-server --ref-audio /path/to/my/voice.wav --ref-text "caption of the reference audio"
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
uv pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

## License

MIT
