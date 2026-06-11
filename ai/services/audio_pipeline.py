# ai.services.audio_pipeline.py
import logging
import os
from ai.audio.convert_audio import convert_to_wav16k
from ai.clients.stt_google import speech_to_text

logger = logging.getLogger(__name__)


def process_audio(audio_path: str):
    wav_path = convert_to_wav16k(audio_path)
    try:
        text = speech_to_text(wav_path)
    finally:
        try:
            os.unlink(wav_path)
        except OSError as e:
            logger.warning(f"[audio_pipeline] 임시 WAV 삭제 실패: {e}")
    return text