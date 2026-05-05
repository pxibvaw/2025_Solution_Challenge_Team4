# ai/tests/test_tts.py
from ai.clients.tts_google import text_to_speech
import base64

text = "할아버지, 부산에서 사셨군요. 그때 어떤 기억이 나세요?"
result = text_to_speech(text)

print(f"base64 길이: {len(result)}")
print(f"앞 20자: {result[:20]}")

# base64 디코딩해서 mp3 파일로 저장 (귀로 확인)
with open("ai/audio/samples/test_tts_output.mp3", "wb") as f:
    f.write(base64.b64decode(result))
print("저장 완료: ai/audio/samples/test_tts_output.mp3")