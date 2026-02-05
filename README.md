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

Ensure you have Python 3.10 or higher.

```bash
# Clone the repository
git clone https://github.com/yourusername/chichi-speech.git
cd chichi-speech

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies (for users)
uv pip install -e .
```

## Quick Start

### 1. Run the Server

Start the TTS server locally. It will download the necessary models on the first run.

```bash
chichi-speech-server
```

By default, the server runs on `http://0.0.0.0:9090`.

### 2. Generate Speech

Use the client to generate audio:

```bash
chichi-speech-client "Hello, welcome to Chichi Speech!" -o welcome.wav
```

### Advanced Usage

#### Custom Voice Cloning

You can start the server with a specific reference audio to clone a custom voice:

```bash

## Development
Install dev dependencies:
```bash
uv pip install -e ".[dev]"
```

Run tests:
pytest
```

## License

MIT
