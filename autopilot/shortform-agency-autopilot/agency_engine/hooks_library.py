"""140+ Verified Korean 3-Second Short-form Hook Dictionary & Auto-Matcher."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from agency_engine.config import ClientBrief


@dataclass(frozen=True)
class HookTemplate:
    hook_id: str
    category: str
    category_ko: str
    template: str
    base_score: int


# 7 Categories x 20 Templates = 140 Verified Korean 3-Second Hooks
_RAW_HOOK_GROUPS: List[tuple[str, str, int, List[str]]] = [
    (
        "info_gap",
        "정보 격차·미공개형",
        94,
        [
            "{industry} 전문가들이 {topic} 할 때 다들 숨기는 게 딱 한 가지 있습니다.",
            "{topic}, 진짜 업계 사람들은 절대 이렇게 안 합니다.",
            "{industry} 10년 차만 알고 있는 {topic} 핵심 비밀 1가지 알려드릴게요.",
            "남들은 돈 내고 배우는 {topic}, 오늘 30초 만에 싹 다 털어드립니다.",
            "{topic} 검색해도 절대 안 나오는 실제 현장 기준만 말씀드릴게요.",
            "{industry}에서 {topic} 잘되는 분들은 시작부터 이 한 가지를 바꿉니다.",
            "아직도 {topic}을 예전 방식대로 하고 계신가요? 지금 당장 멈추세요.",
            "{topic} 관련해서 고객들이 절대 먼저 안 물어보는 치명적 포인트입니다.",
            "솔직히 {industry} 종사자 입장에서 {topic} 이건 말하면 욕먹는데 공개합니다.",
            "{topic}, 상위 1%만 조용히 쓰고 있는 공식이 따로 있습니다.",
            "{industry} 대표가 직접 밝히는 {topic} 성공의 숨은 변수 3가지입니다.",
            "{topic} 처음 시작할 때 아무도 안 알려주는 가장 중요한 첫 단추입니다.",
            "똑같이 {topic} 하는데 왜 누구는 터지고 누구는 망할까요? 이유는 딱 하나입니다.",
            "{topic} 때문에 시간만 버렸다면, 지금 이 3초가 전환점이 될 겁니다.",
            "{industry} 현장에서 100명 상담해 보니 {topic}의 정답은 의외로 간단했습니다.",
            "{topic}, 무료로 풀면 안 되는 내용인데 오늘만 공개합니다.",
            "지금 {topic} 고민 중이시라면, 돈 쓰기 전에 이 영상부터 저장하세요.",
            "{industry} 업계 내부 문서에만 적혀 있는 {topic} 체크리스트입니다.",
            "{topic}에서 가장 많이 놓치는 1% 디테일이 결과를 10배 바꿉니다.",
            "{topic}, 진짜 고수들은 절대 입 밖으로 안 내는 실전 노하우입니다.",
        ],
    ),
    (
        "comparison",
        "직접 비교·선택형",
        93,
        [
            "{compare_a}와 {compare_b} 직접 비교했습니다. 뭐가 다른지 30초 만에 확인하세요.",
            "{compare_a} vs {compare_b}, 내 상황에서 무조건 이득 보는 선택 기준입니다.",
            "{compare_a} 고르려다 멈추세요. {compare_b}와 실제 차이는 여기서 갈립니다.",
            "{compare_a}와 {compare_b} 둘 다 써본 {industry} 전문가가 결론 내드립니다.",
            "돈 아끼려면 {compare_a}, 결과 뽑으려면 {compare_b}? 진짜 팩트 체크합니다.",
            "{compare_a} 할까 {compare_b} 할까 고민 끝내드립니다. 딱 3가지 기준만 보세요.",
            "{compare_a}와 {compare_b}, 광고 말고 실제 후기 기준으로 비교해 봤습니다.",
            "{industry} 전문가가 가족에게 추천하는 건 {compare_a}일까요 {compare_b}일까요?",
            "{compare_a}에서 {compare_b}로 갈아탄 사람들이 공통으로 말하는 이유입니다.",
            "{compare_a} vs {compare_b}, 초보자가 가장 많이 후회하는 선택은 이쪽입니다.",
            "같은 예산으로 {compare_a}와 {compare_b} 중 하나만 고른다면 무조건 이겁니다.",
            "{compare_a}와 {compare_b} 차이, 이 표 하나로 평생 헷갈리지 마세요.",
            "{compare_a} 장점만 듣고 결정하면 큰일 납니다. {compare_b}와 나란히 봤습니다.",
            "{compare_a} vs {compare_b}, 2027년 기준으로 승자가 완전히 바뀌었습니다.",
            "{industry} 현장에서 {compare_a}보다 {compare_b}가 더 잘 팔리는 진짜 이유입니다.",
            "{compare_a}와 {compare_b}를 30일 동안 직접 테스트한 결과 공개합니다.",
            "{compare_a} 고민 중이라면 {compare_b} 가격 대비 효율부터 비교해 보세요.",
            "{compare_a}와 {compare_b}, 나에게 맞는 쪽을 10초 만에 찾는 질문 1가지입니다.",
            "{compare_a} vs {compare_b}, 전문가 10명 중 8명이 선택한 쪽은 따로 있습니다.",
            "{compare_a}와 {compare_b} 실제 데이터 비교, 마지막 숫자가 충격적입니다.",
        ],
    ),
    (
        "loss_warning",
        "실수·손실 경고형",
        95,
        [
            "잠깐만요! {topic} 이렇게 하시면 돈과 시간 그대로 날립니다.",
            "{topic} 할 때 90%가 저지르는 최악의 실수 3가지, 세 번째가 제일 치명적입니다.",
            "지금 {topic} 준비 중이시라면, 이 실수 하나만 피해도 100만원 아낍니다.",
            "{topic} 망하는 사람들의 공통점, 첫 3초에서 이미 티가 납니다.",
            "제발 {topic} 할 때 이것부터 하지 마세요. 결과 100% 망가집니다.",
            "{industry}에서 {topic} 실패하고 찾아오는 분들의 80%가 이걸 놓칩니다.",
            "{topic} 모르고 계약했다가 후회하는 포인트 딱 3개만 짚어드립니다.",
            "이거 모르면 {topic} 아무리 열심히 해도 제자리걸음입니다.",
            "{topic}에서 가장 비싼 수업료를 내게 만드는 함정 1가지입니다.",
            "{topic} 할 때 남들 말만 듣고 따라 했다가 큰코다치는 이유입니다.",
            "경고합니다. {topic}에서 이 신호가 보이면 즉시 멈추셔야 합니다.",
            "{topic} 실패하는 9가지 이유 중 가장 치명적인 상위 3가지만 뽑았습니다.",
            "아직도 {topic}에 불필요한 비용을 쓰고 계신가요? 새는 돈부터 막으세요.",
            "{topic} 처음 하시는 분들이 제일 많이 속는 마케팅 멘트 3가지입니다.",
            "{industry} 전문가가 말리는 {topic} 최악의 선택지 TOP 3입니다.",
            "{topic} 할 때 이 순서가 뒤바뀌면 처음부터 다시 해야 합니다.",
            "지금 당장 {topic}에서 빼야 할 쓸모없는 습관 2가지 알려드립니다.",
            "{topic} 잘하고 싶다면 잘하는 법보다 '망하는 법'부터 피하세요.",
            "{topic}, 남들 다 하는 방식 그대로 따라 하면 절대 성과 안 납니다.",
            "{topic}에서 손해 안 보려면 딱 이 체크리스트 3줄만 확인하세요.",
        ],
    ),
    (
        "listicle_number",
        "숫자·리스트·속도형",
        91,
        [
            "{topic} 완벽 정리, 딱 3가지만 기억하시면 끝입니다.",
            "{topic} 초보자도 5분 만에 적용하는 실전 루틴 3단계입니다.",
            "{topic} 성과를 2배 올리는 핵심 공식 3가지, 3번이 핵심입니다.",
            "하루 10분 투자로 {topic} 끝내는 가장 효율적인 순서 알려드릴게요.",
            "{topic} 고수들이 매일 아침 체크하는 숫자 3가지입니다.",
            "{topic} 시작 전 반드시 봐야 할 필수 기준 5가지 중 핵심 3개입니다.",
            "단 30초 만에 이해하는 {topic} 핵심 구조, 이대로만 따라 하세요.",
            "{topic} 100건 분석해서 뽑은 가장 효과 좋은 패턴 TOP 3입니다.",
            "예산 0원으로 {topic} 퀄리티를 프로 수준으로 올리는 3가지 팁입니다.",
            "{topic}에서 가장 빠르게 결과가 나오는 1단계부터 3단계까지입니다.",
            "{industry} 전문가가 정리한 {topic} 필수 용어 3개만 알면 전문가처럼 보입니다.",
            "{topic} 잘되는 계정의 공통 규칙 4가지, 마지막이 결정타입니다.",
            "단 3줄 입력으로 {topic} 기획을 끝내는 초효율 프레임워크입니다.",
            "{topic} 1년 걸릴 시행착오를 1분으로 줄여드리는 3가지 원칙입니다.",
            "{topic} 처음부터 끝까지, 딱 4단계만 지키면 실패할 수가 없습니다.",
            "{topic} 조회수와 전환을 동시에 잡는 황금 비율 3가지입니다.",
            "{topic} 실무에서 바로 써먹는 체크포인트 3개, 저장 필수입니다.",
            "초보자도 오늘 바로 시작할 수 있는 {topic} 3단계 실행 가이드입니다.",
            "{topic} 결과물을 3배 깔끔하게 만드는 디테일 3가지입니다.",
            "{topic} 상위 노출을 만드는 핵심 요소 3가지, 지금 바로 점검하세요.",
        ],
    ),
    (
        "contrarian",
        "반전·고정관념 파괴형",
        92,
        [
            "{topic}에 비싼 장비가 필요하다고요? 완전한 착각입니다.",
            "다들 {topic} 레드오션이라는데, 진짜 돈 버는 분들은 지금 들어옵니다.",
            "{topic} 잘하려면 말을 잘해야 한다? 오히려 반대입니다.",
            "{topic} 길게 설명할수록 망합니다. 짧을수록 돈이 됩니다.",
            "완벽하게 준비해서 {topic} 시작하면 100% 늦습니다.",
            "{topic}에서 가장 중요한 건 실력이 아니라 '이 구조'입니다.",
            "남들이 {topic} 어렵다고 포기할 때가 가장 쉽게 이기는 타이밍입니다.",
            "{topic} 공짜로 해주면 손해라고요? 오히려 가장 빨리 돈 버는 전략입니다.",
            "{industry}에서 {topic} 싸게 팔면 망한다? 초반엔 정반대가 정답입니다.",
            "{topic}, 열심히 하는 사람보다 시스템 만든 사람이 10배 더 법니다.",
            "비싼 외주 맡기지 마세요. {topic} 이제 스마트폰 하나로 충분합니다.",
            "{topic} 디자인 예쁘게 만드는 데 시간 쓰지 마세요. 중요한 건 따로 있습니다.",
            "{topic}에 재능이 필요하다는 말, 오늘 완전히 깨드리겠습니다.",
            "대부분 {topic}을 거꾸로 시작합니다. 결과부터 보여줘야 이깁니다.",
            "{topic}에서 '자기소개'로 시작하면 3초 만에 전부 이탈합니다.",
            "{topic}, 비싼 강의 듣기 전에 이 무료 원리 3개부터 적용해 보세요.",
            "초보자일수록 {topic}에서 이 한 가지를 버려야 성과가 터집니다.",
            "{topic} 시장이 포화됐다고 말하는 사람들의 공통점을 알려드릴게요.",
            "{topic}, 잘 찍는 것보다 '어떻게 자르느냐'가 90%를 결정합니다.",
            "{topic}은 전문가의 영역이 아닙니다. 이제는 도구 활용의 영역입니다.",
        ],
    ),
    (
        "authority_pro",
        "전문직·신뢰·데이터형",
        90,
        [
            "{industry} 현장에서 직접 검증한 {topic} 실제 데이터 공개합니다.",
            "월 300만 도달을 만든 {topic} 실제 기획안 그대로 보여드립니다.",
            "{industry} 전문가가 클라이언트에게 실제로 납품하는 {topic} 표준안입니다.",
            "의사·변호사 등 전문직 고객들이 {topic}에 지갑을 여는 결정적 이유입니다.",
            "{topic} 50편 이상 제작해 보니 터지는 영상엔 분명한 공식이 있었습니다.",
            "{industry} 대표가 직접 쓰는 {topic} 실무 템플릿을 그대로 공개합니다.",
            "실제 고객 문의가 3배 늘어난 {topic} 구성 방식, 30초 만에 보세요.",
            "{topic}에서 신뢰도를 단번에 끌어올리는 전문가의 화법 3가지입니다.",
            "숫자로 증명합니다. {topic} 구조만 바꿨을 때 달라진 실제 결과입니다.",
            "{industry} 현업자가 매일 사용하는 {topic} 자동화 워크플로우입니다.",
            "고객이 먼저 '계약하겠습니다'라고 말하게 만드는 {topic} 제안 포인트입니다.",
            "{topic} 품질을 한 단계 끌어올리는 전문가용 마무리 검수 기준입니다.",
            "실전 케이스 스터디: {topic} 하나로 문의가 쏟아진 비결입니다.",
            "{industry}에서 단가를 5배 올린 사람들이 {topic}을 다루는 방식입니다.",
            "{topic} 포트폴리오가 0개여도 전문성을 증명하는 가장 확실한 방법입니다.",
            "클라이언트 재계약률 90%를 만드는 {topic} 리포팅 노하우입니다.",
            "{topic}에서 아마추어와 프로를 가르는 결정적 차이 1가지입니다.",
            "현업 {industry} 팀이 매일 아침 9시에 점검하는 {topic} 지표입니다.",
            "{topic}, 감이 아니라 데이터와 구조로 접근해야 매번 성공합니다.",
            "{industry} 전문가가 추천하는 {topic} 가장 안전한 시작 전략입니다.",
        ],
    ),
    (
        "story_empathy",
        "스토리·공감·경험형",
        89,
        [
            "솔직히 저도 처음엔 {topic} 아무것도 몰라서 3개월을 헤맸습니다.",
            "월급 외에 딱 50만원만 더 벌고 싶어서 시작한 {topic}, 이렇게 바뀌었습니다.",
            "퇴근 후 하루 1시간, {topic}으로 첫 수익을 만들었던 실제 과정입니다.",
            "카메라 앞에서 말도 못 하던 분이 {topic}으로 조회수 15만 터뜨린 비결입니다.",
            "저도 예전에 {topic} 때문에 밤새 고생했는데, 이 방법 알고 6분 만에 끝냈습니다.",
            "50대·60대 초보자도 {topic}을 1주일 만에 따라 할 수 있었던 이유입니다.",
            "출퇴근 지하철에서 스마트폰으로 {topic} 처리하는 제 실제 루틴 보여드릴게요.",
            "처음 {topic} 제안했을 때 거절만 당하다가, 이 한 마디로 계약이 터졌습니다.",
            "시간 없는 직장인이 {topic}으로 가장 현실적으로 결과 내는 법입니다.",
            "과거의 저에게 딱 하나만 알려줄 수 있다면, 무조건 이 {topic} 공식을 말할 겁니다.",
            "솔직히 처음엔 저도 반신반의했습니다. 그런데 {topic} 결과가 숫자로 나왔습니다.",
            "남들 넷플릭스 볼 때 {topic} 1편씩 쌓았더니 3달 뒤에 생긴 변화입니다.",
            "전문 장비 없이 폰 하나로 {topic} 시작해서 첫 고객을 만든 실화입니다.",
            "막막하게만 느껴졌던 {topic}, 딱 이 4단계로 쪼개니 너무 쉬워졌습니다.",
            "내가 잘하는 게 없다고 느꼈을 때, {topic}이 돌파구가 되어주었습니다.",
            "클라이언트가 '너무 자연스럽다'며 극찬한 {topic} 촬영·편집 비하인드입니다.",
            "사투리가 심해서 고민이었는데, 오히려 {topic}에서 최강 무기가 됐습니다.",
            "처음엔 무료로 시작했던 {topic}이 어떻게 고단가 패키지가 되었는지 공개합니다.",
            "오늘 당장 시작하고 싶지만 어디서부터 해야 할지 모를 때 보는 {topic} 가이드입니다.",
            "딱 첫 50만원만 만들어 보세요. {topic}을 보는 눈이 완전히 달라집니다.",
        ],
    ),
]


def load_all_140_hooks() -> List[HookTemplate]:
    hooks: List[HookTemplate] = []
    counter = 1
    for cat_id, cat_ko, base_score, templates in _RAW_HOOK_GROUPS:
        for idx, tmpl in enumerate(templates):
            # Subtle deterministic score differentiation for ranking
            score = min(99, base_score + (3 if idx < 3 else (1 if idx < 8 else 0)))
            hooks.append(
                HookTemplate(
                    hook_id=f"HK-{counter:03d}",
                    category=cat_id,
                    category_ko=cat_ko,
                    template=tmpl,
                    base_score=score,
                )
            )
            counter += 1
    return hooks


class HooksLibrary:
    """Provides 140 Korean 3-second hook templates and ranks tailored hooks for any client brief."""

    def __init__(self) -> None:
        self.hooks: List[HookTemplate] = load_all_140_hooks()

    def export_catalog(self) -> List[Dict[str, Any]]:
        return [asdict(h) for h in self.hooks]

    def match_for_brief(self, brief: ClientBrief, top_k: int = 10) -> List[Dict[str, Any]]:
        rendered: List[Dict[str, Any]] = []
        for h in self.hooks:
            text = h.template.format(
                industry=brief.industry,
                topic=brief.topic,
                compare_a=brief.compare_a,
                compare_b=brief.compare_b,
            )
            bonus = 0
            if brief.compare_a and brief.compare_b and h.category == "comparison":
                bonus += 4
            if "실수" in brief.topic and h.category == "loss_warning":
                bonus += 4
            if "시술" in brief.topic and h.category in ("info_gap", "authority_pro"):
                bonus += 3
            final_score = min(100, h.base_score + bonus)
            rendered.append(
                {
                    "hook_id": h.hook_id,
                    "category": h.category,
                    "category_ko": h.category_ko,
                    "score": final_score,
                    "rendered_hook": text,
                }
            )
        rendered.sort(key=lambda x: (-x["score"], x["hook_id"]))
        # Diversify top_k across categories
        picked: List[Dict[str, Any]] = []
        cat_counts: Dict[str, int] = {}
        for item in rendered:
            c = item["category"]
            if cat_counts.get(c, 0) >= 2 and len(picked) < top_k:
                continue
            picked.append(item)
            cat_counts[c] = cat_counts.get(c, 0) + 1
            if len(picked) >= top_k:
                break
        return picked
