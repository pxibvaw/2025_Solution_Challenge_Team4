# ai.tests.test_stt.py
from ai.clients.stt_google import speech_to_text

print("STT result:", speech_to_text("ai/audio/samples/test_stt.wav"))