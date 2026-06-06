# ai.clients.stt_google.py
# Google STT 호출 클라이언트
import logging
from typing import Optional

from google.cloud import speech

logger = logging.getLogger(__name__)

# 모듈 로드 시 client 초기화 — 인증 실패해도 서버는 떠야 함.
# (TTS와 동일 패턴. 인증 깨진 머신에서 audio_pipeline import만으로
#  uvicorn startup 전체가 죽는 것을 방지.)
# 실제 STT 실패는 speech_to_text() 호출 시점에 RuntimeError로 노출 →
# /stt 라우터가 500 + 명확한 detail로 응답.
try:
    client: Optional["speech.SpeechClient"] = speech.SpeechClient()
except Exception as e:
    logger.warning(
        f"[stt_google] SpeechClient 초기화 실패: {e} "
        "(GOOGLE_APPLICATION_CREDENTIALS 또는 gcloud ADC 미설정 의심). "
        "/stt 호출 시 RuntimeError → 500이 반환됩니다.",
        exc_info=True,
    )
    client = None


def speech_to_text(audio_file):
    if client is None:
        raise RuntimeError(
            "STT 클라이언트가 초기화되지 않았어요. "
            "GOOGLE_APPLICATION_CREDENTIALS 환경변수 또는 "
            "`gcloud auth application-default login` 실행이 필요합니다."
        )

    with open(audio_file, "rb") as f:
        content = f.read()

    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ko-KR",
    )

    response = client.recognize(
        config=config,
        audio=audio
    )

    text = ""

    for result in response.results:
        text += result.alternatives[0].transcript

    return text