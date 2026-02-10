import numpy as np
import re
import uvicorn
import torch
import soundfile as sf
import io
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from qwen_tts import Qwen3TTSModel
from pathlib import Path

from . import config

# Initialize FastAPI app
app = FastAPI(title="ChiChi Speech Service")

# Global variables
model = None
VOICE_PROMPT = None


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
    # config.REF_AUDIO and config.REF_TEXT are already loaded
    print(f"Using Reference Audio: {config.REF_AUDIO}")
    print(f"Using Reference Text: {config.REF_TEXT}")

    VOICE_PROMPT = model.create_voice_clone_prompt(
        ref_audio=config.REF_AUDIO,
        ref_text=config.REF_TEXT,
        # x_vector_only_mode=False
    )
    print("Service Ready.")

class SynthesisRequest(BaseModel):
    text: str
    language: str = "auto"


def chunk_text(text: str, max_chars: int = config.MAX_CHUNK_CHARS) -> list[str]:
    """
    Split text into chunks based on punctuation to avoid cutting words,
    keeping chunks under max_chars.
    """
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
        
    chunks = []
    current_chunk = ""
    
    # Split by sentence-ending punctuation, keeping the punctuation
    # This regex splits by (. ! ? ...) and keeps the delimiter
    # We also handle newlines as splits if needed, but basic punctuation is a start.
    sentences = re.split(r'([.!?\n]+)', text)
    
    # Re-attach punctuation to sentences
    real_sentences = []
    for i in range(0, len(sentences) - 1, 2):
        s = sentences[i] + sentences[i+1]
        if s.strip():
            real_sentences.append(s)
    
    # Handle the last part if it didn't end with punctuation
    if len(sentences) % 2 == 1 and sentences[-1].strip():
        real_sentences.append(sentences[-1])
        
    for sentence in real_sentences:
        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    # Fallback: if a single sentence is still too long (rare), forced split could be added here
    # For now, we assume sentences are reasonable.
    
    return chunks or [text]


@app.post("/synthesize")
def synthesize(request: SynthesisRequest):
    """
    Synthesize speech using the pre-loaded voice clone prompt.
    Uses batch processing for long texts.
    """
    if not model or VOICE_PROMPT is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # 1. Chunk the text
        text_chunks = chunk_text(request.text)
        print(f"Synthesizing text of length {len(request.text)} in {len(text_chunks)} chunks...")

        all_audio_segments = []
        sample_rate = None

        # 2. Process in batches
        for i in range(0, len(text_chunks), config.BATCH_SIZE):
            batch = text_chunks[i : i + config.BATCH_SIZE]
            print(f"Processing batch {i//config.BATCH_SIZE + 1}/{(len(text_chunks)+config.BATCH_SIZE-1)//config.BATCH_SIZE} with size {len(batch)}")
            
            # Generate the voice clone (batch)
            wavs, sr = model.generate_voice_clone(
                text=batch,
                language=request.language,
                voice_clone_prompt=VOICE_PROMPT,
            )
            
            # Record sample rate (should be constant)
            if sample_rate is None:
                sample_rate = sr
                
            # Collect audio segments
            for wav in wavs:
                if hasattr(wav, "cpu"):
                    wav = wav.cpu().float().numpy()
                all_audio_segments.append(wav)
        
        if not all_audio_segments:
             raise HTTPException(status_code=400, detail="No audio generated")

        # 3. Concatenate all segments
        final_audio = np.concatenate(all_audio_segments)
        
        # Write to an in-memory buffer
        buffer = io.BytesIO()
        sf.write(buffer, final_audio, sample_rate, format='WAV')
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
    # Update global configuration if arguments specific
    if args.ref_audio:
        config.REF_AUDIO = args.ref_audio
        
    if args.ref_text:
        # Check if argument is a file path
        if os.path.isfile(args.ref_text):
            try:
                with open(args.ref_text, "r", encoding="utf-8") as f:
                    config.REF_TEXT = f.read().strip()
                print(f"Loaded reference text from file: {args.ref_text}")
            except Exception as e:
                print(f"Error reading reference text file {args.ref_text}: {e}")
                exit(1)
        else:
            config.REF_TEXT = args.ref_text

    print(f"Starting server on {args.host}:{args.port}")
    if args.ref_audio:
        print(f"Overriding reference audio: {args.ref_audio}")

    # Run the server
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
