# ai.services.audio_pipeline.py
from ai.audio.convert_audio import convert_to_wav16k
from ai.clients.stt_google import speech_to_text


def process_audio(audio_path: str):

    wav_path = convert_to_wav16k(audio_path)

    text = speech_to_text(wav_path)

    return text