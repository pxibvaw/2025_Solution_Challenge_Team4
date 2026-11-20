# ai/clients/tts_google.py
# Google TTS 호출 클라이언트
import base64
import logging
from typing import Optional

from google.cloud import texttospeech

logger = logging.getLogger(__name__)

# 모듈 로드 시 client 초기화 — 인증 실패해도 서버는 떠야 함.
# (TTS는 보조 기능이므로 audioContent=None으로 degrade)
try:
    client: Optional["texttospeech.TextToSpeechClient"] = (
        texttospeech.TextToSpeechClient()
    )
except Exception as e:
    logger.warning(
        f"[tts_google] TextToSpeechClient 초기화 실패: {e} "
        "(GOOGLE_APPLICATION_CREDENTIALS 미설정 의심). "
        "audioContent는 None으로 반환됩니다.",
        exc_info=True,
    )
    client = None


def text_to_speech(text: str) -> Optional[str]:
    """
    텍스트를 음성으로 변환 후 base64 인코딩된 문자열 반환.
    api.py의 audioContent 필드에 바로 넣을 수 있는 형식.

    실패 시 None 반환 (audioContent는 Optional이라 인터뷰 흐름은 계속됨).
    실패 원인:
      - GCP 인증 미설정
      - 할당량 초과
      - 일시적 네트워크 장애
    """
    if client is None:
        return None

    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name="ko-KR-Wavenet-B",   # 자연스러운 한국어 남성 음성
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        return base64.b64encode(response.audio_content).decode("utf-8")
    except Exception as e:
        logger.warning(f"[tts_google] 합성 실패: {e}", exc_info=True)
        return None