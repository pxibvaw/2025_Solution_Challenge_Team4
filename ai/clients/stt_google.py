# ai.clients.stt_google.py
# Google STT 호출 클라이언트
from google.cloud import speech

client = speech.SpeechClient()

def speech_to_text(audio_file):

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