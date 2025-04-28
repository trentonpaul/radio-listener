import whisper
import ffmpeg
import numpy as np
import torch
import time
from telegram_bot import send_message

STREAM_URL = "https://25053.live.streamtheworld.com/WTMXFM.mp3?dist=hubbard&source=hubbard-web&ttag=web&gdpr=0"

model = whisper.load_model("medium")

KEY_PHRASES = [
    "101.9",
]

def on_phrase_detected(phrase, full_text):
    send_message(f"🔥 DETECTED: '{phrase}' inside: {full_text}")
    print(f"🔥 DETECTED: '{phrase}' inside: {full_text}")

def get_radio_stream(url):
    process = (
        ffmpeg
        .input(url)
        .output('pipe:', format='wav', acodec='pcm_s16le', ac=1, ar='16000')
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )
    return process

def convert_audio_to_numpy(audio_bytes):
    audio = np.frombuffer(audio_bytes, dtype=np.int16)
    audio = audio.astype(np.float32) / 32768.0
    return torch.from_numpy(audio)

def transcribe_radio_stream(url):
    seconds_per_chunk = 10
    overlap_seconds = 2

    sample_rate = 16000
    samples_per_chunk = sample_rate * seconds_per_chunk
    samples_overlap = sample_rate * overlap_seconds

    previous_audio = torch.tensor([])

    process = get_radio_stream(url)

    try:
        while True:
            # Read audio chunk
            audio_chunk = process.stdout.read(sample_rate * 2 * seconds_per_chunk)

            if not audio_chunk or len(audio_chunk) < sample_rate * 2 * seconds_per_chunk:
                print("⚠️ Stream hiccup detected. Restarting ffmpeg...")
                process.kill()
                time.sleep(1)
                process = get_radio_stream(url)
                continue

            current_audio = convert_audio_to_numpy(audio_chunk)

            # Concatenate previous overlap with current audio
            combined_audio = torch.cat((previous_audio, current_audio), dim=0)

            # Transcribe
            result = model.transcribe(combined_audio)
            text = result['text'].lower()

            print("📝:", text)

            # Detect key phrases
            for phrase in KEY_PHRASES:
                if phrase.lower() in text:
                    on_phrase_detected(phrase, text)

            # Save last N seconds for next overlap
            if len(current_audio) >= samples_overlap:
                previous_audio = current_audio[-samples_overlap:]
            else:
                previous_audio = current_audio

            time.sleep(0.2)  # Shorter sleep now, less lag buildup

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        process.kill()

transcribe_radio_stream(STREAM_URL)
