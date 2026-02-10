import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import torch
import soundfile as sf
import io
from qwen_tts import Qwen3TTSModel
import os
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(title="ChiChi Speech Service")

# Global variables
model = None
VOICE_PROMPT = None

# Determine absolute path to assets
CURRENT_DIR = Path(__file__).parent.absolute()
ASSETS_DIR = CURRENT_DIR / "assets"
DEFAULT_REF_AUDIO = str(ASSETS_DIR / "coco.wav")
DEFAULT_REF_TEXT_PATH = ASSETS_DIR / "coco.txt"

# Default reference constants
REF_AUDIO = DEFAULT_REF_AUDIO
# Read default reference text from file
try:
    with open(DEFAULT_REF_TEXT_PATH, "r", encoding="utf-8") as f:
        REF_TEXT = f.read().strip()
except Exception as e:
    print(f"Warning: Could not read default reference text from {DEFAULT_REF_TEXT_PATH}: {e}")
    REF_TEXT = "Okay. Yeah. I resent you. I love you. I respect you. But you know what? You blew it! And thanks to you."

@app.on_event("startup")
async def startup_event():
    global model, VOICE_PROMPT
    print("Loading Qwen3 TTS Model...")
    # Initialize the model
    # Using the same parameters as voice_clone_basic.py
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        device_map="mps",
        dtype=torch.float32,
    )
    
    print("Creating Voice Clone Prompt...")
    # Pre-compute the prompt using the hardcoded reference audio and text
    # This corresponds to: prompt_items = tts.create_voice_clone_prompt(...)
    # We default x_vector_only_mode to False as the variable 'xvec_only' 
    # from the snippet is unknown, and typically such flags are optional.
    global REF_AUDIO, REF_TEXT
    
    # Check for environment variable overrides (important for Gunicorn usage)
    if "REF_AUDIO" in os.environ:
       REF_AUDIO = os.environ["REF_AUDIO"]
       
    if "REF_TEXT" in os.environ:
       ref_text_val = os.environ["REF_TEXT"]
       # Check if it is a file path
       if os.path.isfile(ref_text_val):
           try:
               with open(ref_text_val, "r", encoding="utf-8") as f:
                   REF_TEXT = f.read().strip()
               print(f"Loaded reference text from file (ENV): {ref_text_val}")
           except Exception as e:
               print(f"Error reading reference text file from ENV {ref_text_val}: {e}")
               # Fallback to using the value as text if read fails? Or exit?
               # For robustness in startup, maybe we fail hard if it looks like a file but fails?
               # But given previous logic, let's treat it as text if read fails or assume it wasn't a file 
               # (though isfile passes). 
               # Let's trust isfile for now.
               raise e
       else:
           REF_TEXT = ref_text_val

    print(f"Using Reference Audio: {REF_AUDIO}")
    print(f"Using Reference Text: {REF_TEXT}")

    VOICE_PROMPT = model.create_voice_clone_prompt(
        ref_audio=REF_AUDIO,
        ref_text=REF_TEXT,
        # x_vector_only_mode=False
    )
    print("Service Ready.")

class SynthesisRequest(BaseModel):
    text: str
    language: str = "auto"

@app.post("/synthesize")
def synthesize(request: SynthesisRequest):
    """
    Synthesize speech using the pre-loaded voice clone prompt.
    """
    if not model or VOICE_PROMPT is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Generate the voice clone
        # corresponding to: return tts.generate_voice_clone(...)
        wavs, sr = model.generate_voice_clone(
            text=request.text,
            language=request.language,
            voice_clone_prompt=VOICE_PROMPT,
        )
        
        # wavs[0] is the audio data. Ensure it's a numpy array for soundfile.
        audio_data = wavs[0]
        if hasattr(audio_data, "cpu"):
             audio_data = audio_data.cpu().float().numpy()
             
        # Write to an in-memory buffer
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sr, format='WAV')
        buffer.seek(0)
        
        return StreamingResponse(buffer, media_type="audio/wav")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

def main():
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Qwen3 TTS Service")
    parser.add_argument("--port", type=int, default=9090, help="Service port (default: 9090)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Service host (default: 0.0.0.0)")
    parser.add_argument("--ref-audio", type=str, help="Path to reference audio file for voice cloning")
    parser.add_argument("--ref-text", type=str, help="Reference text content or path to text file corresponding to the audio")

    args = parser.parse_args()

    # Environment variable overrides
    if "PORT" in os.environ:
        args.port = int(os.environ["PORT"])

    # Update global configuration if arguments specific
    global REF_AUDIO, REF_TEXT
    if args.ref_audio:
        REF_AUDIO = args.ref_audio
        
    if args.ref_text:
        # Check if argument is a file path
        if os.path.isfile(args.ref_text):
            try:
                with open(args.ref_text, "r", encoding="utf-8") as f:
                    REF_TEXT = f.read().strip()
                print(f"Loaded reference text from file: {args.ref_text}")
            except Exception as e:
                print(f"Error reading reference text file {args.ref_text}: {e}")
                exit(1)
        else:
            # Not a file, verify if it looks like a path but doesn't exist?
            # Or just treat as text.
            REF_TEXT = args.ref_text

    print(f"Starting server on {args.host}:{args.port}")
    if args.ref_audio:
        print(f"Overriding reference audio: {args.ref_audio}")

    # Run the server
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
