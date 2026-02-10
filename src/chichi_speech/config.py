import os
from pathlib import Path

# Base directory
CURRENT_DIR = Path(__file__).parent.absolute()
ASSETS_DIR = CURRENT_DIR / "assets"

# Model Configuration
MODEL_ID = os.getenv("MODEL_ID", "Qwen/Qwen3-TTS-12Hz-1.7B-Base")
DEVICE_MAP = os.getenv("DEVICE_MAP", "mps")

# Inference Configuration
# Batch size for parallel generation
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "4"))
# Max characters per chunk for text splitting
MAX_CHUNK_CHARS = int(os.getenv("MAX_CHUNK_CHARS", "300"))

# Voice Cloning Defaults
DEFAULT_REF_AUDIO_PATH = ASSETS_DIR / "coco.wav"
DEFAULT_REF_TEXT_PATH = ASSETS_DIR / "coco.txt"

# Default prompt (can be overridden by params/env)
REF_AUDIO = os.getenv("REF_AUDIO", str(DEFAULT_REF_AUDIO_PATH))
_ref_text_env = os.getenv("REF_TEXT", str(DEFAULT_REF_TEXT_PATH))

# Load text from file if it's a file path, otherwise use as string
REF_TEXT = _ref_text_env
if os.path.isfile(_ref_text_env):
    try:
        with open(_ref_text_env, "r", encoding="utf-8") as f:
            REF_TEXT = f.read().strip()
    except Exception as e:
        print(f"Warning: Failed to read REF_TEXT from file {_ref_text_env}: {e}")
else:
    # If it's not a file, assumes it's the raw text.
    # But if default was a path that doesn't exist? 
    # The default path MUST exist for the app to work out of box.
    if _ref_text_env == str(DEFAULT_REF_TEXT_PATH) and not os.path.exists(DEFAULT_REF_TEXT_PATH):
        # Fallback text if asset missing (shouldn't happen)
        REF_TEXT = "Okay. Yeah. I resent you. I love you. I respect you. But you know what? You blew it! And thanks to you."
