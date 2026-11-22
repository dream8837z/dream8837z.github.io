"""Central configuration, video forensic audit matrix, and default B2B client briefs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
OUTPUT_DIR = BASE_DIR / "output"

VIDEO_SOURCE = {
    "url": "https://youtu.be/mF7mxHau5dE",
    "title": '부산 달동네에서 50만원으로 3년만에 735억 회사 대표가 된 30대 남자의 하루 | "2027년 개꿀통 부업은 바로 이겁니다"',
    "channel": "이웃집사장 (@eut.sajang) · 출연: 타철 대표 (타이탄 철물점)",
    "duration": "35:56",
    "upload_date": "2026-11-22",
}


VIDEO_FORENSIC_AUDIT: List[Dict[str, str]] = [
    {
        "topic": "수익성 주장 (편당 25만원 · 월 3,000만원)",
        "video_claim": "AI 앱으로 6분 만에 1편 편집해 10편 250만원(편당 25만원) 납품, 두 달 만에 월 매출 3,000만원",
        "verdict": "REALITY_CHECK",
        "risk_found": "무료강의→단톡방→고가 유료강의(120만원+) 유도 퍼널 구조. 단순 컷편집만으로는 초보자가 편당 25만원 수주 불가",
        "our_solution": "기획(4단계 대본)+성과 리포트+수정 2회 제한 계약서를 묶은 3단계 현실 단가(5만→15만→25만원) 시뮬레이터 구축",
    },
    {
        "topic": "3초 후킹 문장 140개 사전 (단톡방 미끼)",
        "video_claim": "터진 영상에서 뽑은 140개 후킹 사전을 댓글·단톡방 참여자에게만 제공",
        "verdict": "OPEN_AUTOMATED",
        "risk_found": "외부 단톡방 가입·강의 영업에 묶여 있으며 업종별 자동 치환 및 점수화가 수동",
        "our_solution": "7대 카테고리 × 20개 = 140개 한국어 검증 후킹 템플릿 사전 + 업종·키워드 실시간 자동 치환 엔진 100% 내장",
    },
    {
        "topic": "4단계 기획·대본 생성기 (멈추고→궁금→알려주고→부탁)",
        "video_claim": "키워드 3줄 입력으로 ChatGPT/Claude에 대본 프롬프트를 자동 전송하고 사투리/페르소나 가미",
        "verdict": "ADOPT_AND_CODE",
        "risk_found": "외부 LLM 의존 시 매번 품질 편차 발생, 컷별 촬영 디렉팅과 오픈루프 검증이 누락됨",
        "our_solution": "4단계 구조 + 3종 페르소나(프로페셔널/구어체/부산 사투리) 자동 변환 + ChatGPT/Claude 원클릭 고도화 프롬프트 생성기 구현",
    },
    {
        "topic": "AI 6분 자동 컷편집 + CapCut/Premiere 내보내기",
        "video_claim": "고객이 폰으로 찍은 7분 NG 원본을 앱에 넣으면 1분 완성본 + 자막 + CapCut/Premiere 프로젝트로 출력",
        "verdict": "FULL_AUTOMATION",
        "risk_found": "단순 무음 제거만으로는 '죄송합니다/다시 할게요' 같은 발화 NG가 남고, 유료 SaaS 구독료가 발생",
        "our_solution": "FFmpeg 오디오 RMS 무음 컷 + NG 키워드 구간 자동 제거 + 1080×1920 자막·줌 MP4 + CapCut JSON & Premiere FCPXML 원가 $0 자동 생성",
    },
    {
        "topic": "3대 고객 모집 (Threads 무료 3편 · 숨고 · Meta 광고)",
        "video_claim": "Threads에 '포트폴리오용 무료 제작' 글로 100명 모객 + 인사이트 자랑 + 숨고 견적",
        "verdict": "GUARDRAILED",
        "risk_found": "무료 제작 후 무한 수정 지옥·저작권/초상권 분쟁·숨고 견적 캐시 적자(CAC 미계산) 리스크",
        "our_solution": "Threads/숨고/DM 영업 스크립트 + '10편 가격에 12편' 보너스 견적서 + 수정 2회 제한 B2B 표준 계약서 조항 자동 생성",
    },
]


@dataclass
class ClientBrief:
    client_id: str
    client_name: str
    industry: str
    topic: str
    compare_a: str
    compare_b: str
    cta_action: str
    persona_tone: str = "professional"  # professional | friendly | busan


DEFAULT_CLIENT_BRIEFS: List[ClientBrief] = [
    ClientBrief(
        client_id="clinic_skin",
        client_name="청담 리프팅 피부과",
        industry="피부과·의료 전문직",
        topic="연예인이 몰래 받는 비수술 리프팅 시술 3가지",
        compare_a="울쎄라",
        compare_b="써마지",
        cta_action="팔로우하고 댓글에 '시술' 남기면 원장님 비교표 DM 발송",
        persona_tone="professional",
    ),
    ClientBrief(
        client_id="agency_shortform",
        client_name="타이탄 숏폼 에이전시",
        industry="영상 제작 에이전시",
        topic="숏폼 조회수 망치는 치명적 실수 3가지",
        compare_a="AI 자동편집",
        compare_b="수동 외주편집",
        cta_action="팔로우하고 댓글에 '후킹' 남기면 140개 사전 링크 DM 발송",
        persona_tone="busan",
    ),
    ClientBrief(
        client_id="diet_clinic",
        client_name="강남 대사 클리닉",
        industry="비만·건강 클리닉",
        topic="마운자로와 위고비 실제 차이점과 부작용 체크",
        compare_a="마운자로",
        compare_b="위고비",
        cta_action="저장해 두고 댓글에 '비교' 남기면 처방 기준표 DM 발송",
        persona_tone="friendly",
    ),
]


@dataclass
class AgencyConfig:
    agency_name: str = "Shortform Agency Autopilot"
    output_dir: Path = OUTPUT_DIR
    fonts_dir: Path = FONTS_DIR
    client_briefs: List[ClientBrief] = field(default_factory=lambda: list(DEFAULT_CLIENT_BRIEFS))

    def resolve_font(self, weight: str = "black") -> Path:
        candidates = {
            "black": ["Pretendard-Black.otf", "NotoSansKR-Bold.ttf"],
            "extrabold": ["Pretendard-ExtraBold.otf", "NotoSansKR-Bold.ttf"],
            "bold": ["NotoSansKR-Bold.ttf", "Pretendard-ExtraBold.otf", "Pretendard-Black.otf"],
        }.get(weight, ["NotoSansKR-Bold.ttf"])
        for name in candidates:
            p = self.fonts_dir / name
            if p.exists():
                return p
        return Path("/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf")
