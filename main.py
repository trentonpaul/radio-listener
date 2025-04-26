# import subprocess
# import speech_recognition as sr
# from pydub import AudioSegment
# from io import BytesIO

STREAM_URL = "https://25053.live.streamtheworld.com/WTMXFM.mp3?dist=hubbard&source=hubbard-web&ttag=web&gdpr=0"

import whisper
import subprocess
import time
import numpy as np
import torch
from io import BytesIO

# Load the Whisper model (can try 'base', 'small', 'medium', or 'large')
model = whisper.load_model("tiny")

# Function to pull the radio stream via ffmpeg
def get_radio_stream(url):
    # Use ffmpeg to get audio as raw PCM (16-bit WAV)
    process = subprocess.Popen([
        "ffmpeg",
        "-i", url,
        "-f", "wav",            # Output format (WAV)
        "-ar", "16000",         # Sample rate (16 kHz)
        "-ac", "1",             # Mono channel
        "-loglevel", "quiet",   # Quiet output (no logs)
        "pipe:1"                # Send the audio to stdout
    ], stdout=subprocess.PIPE)
    return process

# Function to convert raw audio bytes to numpy array and normalize
def convert_audio_to_numpy(audio_bytes):
    # Convert raw audio bytes to numpy array (int16 PCM)
    audio = np.frombuffer(audio_bytes, dtype=np.int16)

    # Normalize to [-1, 1] (Whisper expects floating point values)
    audio = audio.astype(np.float32) / 32768.0
    
    # Convert to torch tensor (required by Whisper)
    audio_tensor = torch.from_numpy(audio)
    
    return audio_tensor

# Function to transcribe the radio stream in real-time
def transcribe_radio_stream(url):
    process = get_radio_stream(url)
    
    while True:
        # Read 5 seconds of audio (16000 samples/second * 2 bytes per sample * 5 seconds)
        audio_chunk = process.stdout.read(16000 * 2 * 5)  # 5 seconds of audio
        if not audio_chunk:
            break

        # Convert audio chunk (bytes) to numpy array
        audio_data = convert_audio_to_numpy(audio_chunk)

        # Feed the audio data to Whisper for transcription
        result = model.transcribe(audio_data)
        
        # Print the transcription
        print("TEXT:", result['text'])
        
        # Sleep to simulate real-time processing (optional)
        time.sleep(1)

transcribe_radio_stream(STREAM_URL)
