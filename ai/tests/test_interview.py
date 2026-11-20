# ai.tests.test_interview.py
from ai.services.interview_service import run_interview
from ai.services.memory_service import save_memory


# 테스트용 memory 저장
save_memory("어릴 때 부산에서 살았어요")
save_memory("젊을 때 배를 탔어요")
save_memory("손녀가 둘 있어요")


print(run_interview("요즘 옛날 생각이 나네요"))
print(run_interview("부산에서 살았어요"))
print(run_interview("바닷가에서 놀던 기억이 나네요"))