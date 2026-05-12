# ai/clients/tts_google.py
# Google TTS 호출 클라이언트
import base64
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()

def text_to_speech(text: str) -> str:
    """
    텍스트를 음성으로 변환 후 base64 인코딩된 문자열 반환.
    api.py의 audioContent 필드에 바로 넣을 수 있는 형식.
    """
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