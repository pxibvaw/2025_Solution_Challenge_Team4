# ai.embedding.embedder.py
from google import genai
from ai.app.settings import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def embed_text(text: str):

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    embedding = response.embeddings[0].values

    return embedding