# ai.tests.test_embedding.py
from ai.embedding.embedder import embed_text

vector = embed_text("어릴 때 부산에서 살았어요")

print(len(vector))
print(vector[:10])