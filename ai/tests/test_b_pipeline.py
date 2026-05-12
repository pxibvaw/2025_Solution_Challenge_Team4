"""
테스트 B: 가짜 노인 대화 로그 직접 주입
run_episode_pipeline() 직접 호출 — /turn API 없이
"""
from ai.app.schemas import UserProfileContext
from ai.services.episode_service import run_episode_pipeline
from ai.services.memory_service import memory_service
import json

SESSION_LOG = [
    {"user": "남편이 참... 부지런한 사람이었어요.", "ai": "어떤 분이셨나요?"},
    {"user": "새벽 네 시면 어김없이 일어나서 바다로 나갔지요. 아직 어두컴컴한데, 저는 반쯤 잠에 취해서 일어나서 밥을 해줬어요. 그 사람은 밥도 빨리 먹고, 국물만 홀짝이고는 금방 나갔지요. '다녀올게' 이 한마디 하고. 그 목소리가 아직도 귀에 남아요.", "ai": "정말 생생하게 기억하시네요."},
    {"user": "부산 영도에서 살았는데... 거기가 참 좋았어요. 창문 열면 바다가 보이고, 새벽에는 갈매기 소리가 들리고. 아, 그리고 그 짭짤한 냄새요. 비린내라고 하면 나쁜 것 같은데, 저한테는 그게 집 냄새였어요. 남편 냄새였고요.", "ai": "영도가 많이 그리우시겠어요."},
    {"user": "지금 노원구에 사는데, 여기는 아파트잖아요. 냄새가 없어요. 그냥 아무 냄새도 없어. 어머, 내가 무슨 얘기 하다가 이랬지.", "ai": "괜찮아요, 계속 말씀해 주세요."},
    {"user": "그래요, 남편이 바다 나가면 저 혼자서 다 했지요. 애들이 셋이었는데... 딸 둘에 막내가 아들. 막내가 많이 어려서, 기저귀도 갈고 밥도 먹이고, 그러고 나서 위에 애들 학교 챙겨 보내고, 그다음에 시장에 나가야 하고. 아이고, 그때는 몸이 여러 개였으면 싶었어요.", "ai": "정말 많이 힘드셨겠어요."},
    {"user": "저는 시장에서 생선을 팔았어요. 남편이 잡아오는 걸 받아다가 영도 시장에서 팔았지요. 새벽 다섯 시에 나가서, 다 팔면 들어오는데 보통 저녁 여섯 시, 일곱 시. 힘들었는데 그래도 사람들이 좋았어요. 뭐 하나라도 더 얹어주고, 그런 게 있었지요. 정이라는 게.", "ai": "그런 따뜻한 정이 있었군요."},
    {"user": "막내가 일곱 살 때 크게 아팠어요. 열이 얼마나 높았냐면, 손으로 만지면 뜨거울 정도로. 밤새 찬 수건 갈아주고 안고 있었는데 안 내리는 거예요. 남편은 바다에 나가 있고. 새벽에 옆집 아주머니 문 두드려서 같이 아이 들쳐업고 병원을 갔지요. 그때 의사 선생님이 '조금만 늦었으면 위험할 뻔했다' 하는 거예요. 그 자리에서 주저앉을 뻔했어요.", "ai": "얼마나 무서우셨을까요."},
    {"user": "근데 그 아이가 지금 소아과 의사예요. 자기가 왜 소아과 갔냐면, 그때 그 선생님 때문이래요. 이 얘기 하면 항상 눈물이 나려고 해요.", "ai": "정말 대견하시겠어요."},
    {"user": "남편이 태풍 때도 나갔어요. 제가 얼마나 말렸는지 몰라요. 그렇게 나가고. 저는 그날 하루 종일 창문만 봤어요. 비 오고 바람 불고. 그 날 남편이 들어왔을 때 '왜 이렇게 늦었어요' 하면서 툴툴댔지요. 속으로는 얼마나 반가웠는지.", "ai": "많이 걱정되셨겠어요."},
    {"user": "그때가 참 좋았는데... 외롭기도 했지요.", "ai": "그 복잡한 마음이 느껴져요."},
    {"user": "남편이 십 년 전에 갑자기 갔어요. 심장이었어요. 아침에 밥 같이 먹었는데, 텔레비전 보다가... 그렇게 됐지요. 그 날이 아직도 생생해요. 꿈에는 아직 나와요. 새벽에 바다 나가는 꿈.", "ai": "많이 그리우시겠어요."},
    {"user": "이사 온 게 오 년 됐나. 노원구요. 막내가 가까이 있어야 한다고 해서. 손자 둘이 자주 와요. 작은 손자가 저 껴안으면서 '할머니 냄새 좋아' 하는데, 그때 울 뻔했어요.", "ai": "정말 소중한 순간이네요."},
    {"user": "몸이... 무릎이 안 좋아요. 의사는 수술하자는데 겁도 나고. 막내한테는 그냥 괜찮다고 했어요. 걱정할까봐.", "ai": "많이 참고 계시는군요."},
    {"user": "살아있는 것만으로도 감사하지요. 남편은 못 보는 것들을 내가 보고 있잖아요. 막내가 의사 된 것도, 손자들이 크는 것도. 힘들었는데, 돌아보면 잘 살았어요.", "ai": "정말 따뜻한 말씀이에요."},
    {"user": "잘 살았다고 생각해요. 힘들었지만, 잘 살았어요.", "ai": "오늘 소중한 이야기 나눠주셔서 감사해요."},
]

profile = UserProfileContext(
    userTitle="김복순 할머니",
    speechLevel="HONORIFIC",
    memorableAge="30대",
    coreValue="가족",
    birthYear=1945,
)


def _divider(title=""):
    print(f"\n{'='*60}")
    if title:
        print(f"  {title}")
        print(f"{'='*60}")


# run_episode_pipeline 원본 패치 — 에피소드 내용 캡처용
_captured_episodes = []
_orig_post = None

def _patch_callback():
    """Spring Boot 콜백 대신 로컬에서 에피소드 캡처."""
    import ai.services.episode_service as svc
    orig = svc._post_callback

    def fake_post(payload):
        _captured_episodes.extend(payload.get("newEpisodes", []))
        _captured_episodes.extend(payload.get("mergedEpisodes", []))
        print(f"[테스트] 콜백 캡처: 신규 {len(payload.get('newEpisodes',[]))}개, 보강 {len(payload.get('mergedEpisodes',[]))}개")
        if payload.get("warnings"):
            print(f"[테스트] 경고: {payload['warnings']}")
        return True, "mocked"

    svc._post_callback = fake_post
    return orig, svc

def _restore_callback(orig, svc):
    svc._post_callback = orig


if __name__ == "__main__":
    _divider("테스트 B 시작")
    print(f"대화 로그: {len(SESSION_LOG)}턴")

    orig, svc = _patch_callback()
    try:
        result = run_episode_pipeline(
            session_id="test-b-001",
            user_id="test-b-user",
            session_log=SESSION_LOG,
            profile=profile,
            memory_service=memory_service,
        )
    finally:
        _restore_callback(orig, svc)

    _divider("파이프라인 결과")
    print(f"생성된 에피소드: {result.episodes_created}개")
    print(f"보강된 에피소드: {result.episodes_merged}개")
    print(f"약한 에피소드:   {result.weak_episodes}개")

    if not _captured_episodes:
        print("\n⚠ 캡처된 에피소드 없음")
    else:
        for i, ep in enumerate(_captured_episodes):
            _divider(f"에피소드 {i+1}: {ep.get('title', '제목 없음')}")
            print(f"  타입:      {ep.get('type')}")
            print(f"  테마:      {ep.get('theme')}")
            print(f"  감정:      {ep.get('emotion_tone')}")
            print(f"  시기:      {ep.get('period_label')}")
            print(f"  중요도:    {ep.get('importance_score')}")
            q = ep.get("quality", {})
            print(f"  품질:")
            print(f"    faithfulness:  {q.get('faithfulness_score')}")
            print(f"    coverage:      {q.get('coverage_score')}")
            print(f"    emotional:     {q.get('emotional_authenticity')}")
            print(f"    sensory:       {q.get('sensory_vividness')}")
            print(f"    voice:         {q.get('personal_voice')}")
            print(f"    flow:          {q.get('narrative_flow')}")
            print(f"\n  [서술]")
            print(f"  {ep.get('narrative', '없음')}")
            if ep.get("quote"):
                print(f"\n  [인용] {ep.get('quote')}")
            if ep.get("life_value"):
                print(f"  [삶의 가치] {ep.get('life_value')}")

    _divider("테스트 B 완료")
