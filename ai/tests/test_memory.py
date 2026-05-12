# ai.tests.test_memory.py
from ai.services.memory_service import save_memory, retrieve_memory

# memory 저장
save_memory("어릴 때 부산에서 살았어요")
save_memory("젊을 때 배를 탔어요")
save_memory("손녀가 둘 있어요")

# memory 검색
results = retrieve_memory("바닷가에서 놀던 기억")

print(results)