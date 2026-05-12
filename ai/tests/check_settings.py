# ai.tests.check_settings.py
from ai.app.settings import settings

print("PROJECT:", settings.GOOGLE_CLOUD_PROJECT)
print("LOCATION:", settings.GOOGLE_CLOUD_LOCATION)
print("GEMINI KEY SET:", bool(settings.GEMINI_API_KEY))