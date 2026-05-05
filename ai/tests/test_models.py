# ai.tests.test_models.py
from google import genai
from ai.app.settings import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

models = client.models.list()

for m in models:
    print(m.name)