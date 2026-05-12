# ai.tests.test_chroma.py
from ai.memory.chroma_store import add_memory, search_memory

# fake embedding (768차원 예시)
embedding = [0.1] * 768

add_memory(
    text="어릴 때 부산에서 살았다고 말함",
    embedding=embedding,
    memory_id="mem1"
)

results = search_memory(embedding)

print(results)