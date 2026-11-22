"""Central configuration, 8-step forensic audit matrix, and path definitions."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
SCRATCH_ROOT = BASE_DIR.parent

VIDEO_SOURCE = {
    "url": "https://youtu.be/EDvnavKiWwI",
    "title": "클로드 직원 5명이 제 사이트로 알아서 돈 벌어줍니다 (ai 직원 세팅법 8가지)",
    "channel": "혼잡스 (@honjobs)",
    "duration": "9:28",
    "upload_date": "2026-07-08",
}

DEFAULT_TARGET_SITES: List[Path] = [
    SCRATCH_ROOT / "dream8837z.github.io",
    SCRATCH_ROOT / "pseo-revenue-autopilot" / "dist",
]


@dataclass(frozen=True)
class DepartmentSpec:
    dept_id: str
    name_ko: str
    role_title: str
    model_tier: str
    allowed_read_globs: List[str]
    allowed_write_dirs: List[str]
    forbidden_actions: List[str]
    daily_mission: str
    evidence_requirement: str


DEPARTMENT_SPECS: Dict[str, DepartmentSpec] = {
    "master": DepartmentSpec(
        dept_id="master",
        name_ko="총괄 마스터",
        role_title="Chief Verification & Orchestration Officer",
        model_tier="sonnet-or-deterministic",
        allowed_read_globs=["**/*"],
        allowed_write_dirs=["output/master", "output/studio"],
        forbidden_actions=["unverified_pass", "force_push", "delete_production_files"],
        daily_mission="매일 KST 09:00 5개 부서 지시 + 모든 산출물 SHA-256·파일 실존·픽셀/HTML 기계적 증거 검수",
        evidence_requirement="전 부서 증거 해시 재검증 + UNVERIFIED 항목 0건 확인",
    ),
    "planner": DepartmentSpec(
        dept_id="planner",
        name_ko="기획팀",
        role_title="SEO Index & Content Strategy Planner",
        model_tier="sonnet",
        allowed_read_globs=["*.html", "sitemap.xml", "robots.txt", "llms.txt", "data/**"],
        allowed_write_dirs=["output/planner"],
        forbidden_actions=["direct_code_edit", "secret_access", "external_post"],
        daily_mission="Google Search Console 색인/노출(또는 로컬 SEO 갭) 점검 + 고단가 키워드·콘텐츠 백로그 수립",
        evidence_requirement="실제 스캔 페이지 수, 누락 메타/구조화데이터 목록 JSON + SHA-256",
    ),
    "dev": DepartmentSpec(
        dept_id="dev",
        name_ko="개발팀",
        role_title="Site Reliability & Technical SEO Engineer",
        model_tier="sonnet",
        allowed_read_globs=["**/*.html", "**/*.css", "**/*.js", "robots.txt", "sitemap.xml", "ads.txt"],
        allowed_write_dirs=["output/dev"],
        forbidden_actions=["rm_rf", "force_push", "env_read", "unreviewed_prod_overwrite"],
        daily_mission="내부 깨진 링크·HTML/JSON-LD 오류·모바일 뷰포트 점검 및 안전한 SEO 자동 패치 번들 생성",
        evidence_requirement="헬스체크 로그, 검출 이슈 건수, 생성된 패치 Diff 파일 SHA-256",
    ),
    "design": DepartmentSpec(
        dept_id="design",
        name_ko="디자인팀",
        role_title="Visual Systems & SNS Card News Designer",
        model_tier="haiku-or-pillow",
        allowed_read_globs=["output/planner/**", "assets/**"],
        allowed_write_dirs=["output/design"],
        forbidden_actions=["code_edit", "secret_access", "cs_reply"],
        daily_mission="매일 1080×1350 인스타그램·유튜브 커뮤니티용 SNS 카드뉴스 5장 캐러셀 PNG 무인 렌더링",
        evidence_requirement="PNG 5장 실존 여부, 해상도 1080×1350 검증, 픽셀 분산(빈 이미지 방지), SHA-256",
    ),
    "cs": DepartmentSpec(
        dept_id="cs",
        name_ko="CS팀",
        role_title="Customer Support & Triage Specialist",
        model_tier="haiku",
        allowed_read_globs=["data/cs_inbox.json", "output/dev/**"],
        allowed_write_dirs=["output/cs"],
        forbidden_actions=["blind_auto_refund", "code_edit", "secret_access"],
        daily_mission="유입 문의 자동 분류(버그/제휴/콘텐츠요청/스팸), SLA 우선순위 지정, 정책 기반 한국어 응답 초안 작성",
        evidence_requirement="전체 티켓 처리 리포트 JSON + 인간 승인 필요(Escalation) 건 분리 기록 + SHA-256",
    ),
    "marketing": DepartmentSpec(
        dept_id="marketing",
        name_ko="마케팅팀",
        role_title="Growth Distribution & Monetization Marketer",
        model_tier="haiku",
        allowed_read_globs=["output/planner/**", "output/design/**"],
        allowed_write_dirs=["output/marketing"],
        forbidden_actions=["code_edit", "secret_access", "fake_metrics"],
        daily_mission="디자인팀 카드뉴스 5장 + 채널별(인스타/유튜브 커뮤니티/스레드/블로그) UTM 배포 패키지 생성",
        evidence_requirement="연결된 PNG 5장 경로 검증 + 채널별 카피·UTM 링크 번들 JSON/MD + SHA-256",
    ),
}


VIDEO_8STEP_AUDIT: List[Dict[str, str]] = [
    {
        "step": "① 채용 공고 쓰기",
        "video_claim": "목표·매일 업무·결과물 3줄로 직원의 업무를 명확히 정의",
        "verdict": "ADOPT_AND_EXPAND",
        "risk_found": "3줄만으로는 월 토큰 예산 상한, 실패 시 폴백, 금지 행동이 누락되어 폭주 가능",
        "our_solution": "3줄 핵심 채용 공고 + KPI/SLA/월간 토큰 상한($15)/보안 금지 조항을 구조화한 job_posting.md 자동 생성",
    },
    {
        "step": "② 업무 공간 만들기",
        "video_claim": "Claude Code PC 버전 설치 후 로컬 폴더에서 새 대화창 세팅",
        "verdict": "HYBRID_UPGRADE",
        "risk_found": "PC 전원 OFF·절전 모드 시 로컬 스케줄러가 즉시 중단되어 24/365 무인 운영 불가",
        "our_solution": "로컬 워크스페이스 + GitHub Actions 클라우드 Cron(매일 KST 09:00) 이중화 워크플로우 자동 생성",
    },
    {
        "step": "③ 직원 교육 (회사 매뉴얼)",
        "video_claim": "CLAUDE.md 매뉴얼을 공유하고 운영하면서 지속적으로 보완",
        "verdict": "ADOPT_CORE",
        "risk_found": "남의 템플릿(honjobs.com/47)을 그대로 쓰면 내 사이트 구조·수익화 모델과 괴리 발생",
        "our_solution": "실제 보유 사이트(dream8837z.github.io, pseo-revenue-autopilot) 구조가 반영된 맞춤형 CLAUDE.md 자동 생성",
    },
    {
        "step": "④ 장비와 권한 주기",
        "video_claim": "구글 드라이브/노션 커넥터 연동 + 내 컴퓨터 폴더 접근 '항상 허용'",
        "verdict": "SECURITY_REPLACE",
        "risk_found": "치명적 리스크: 무제한 '항상 허용'은 프롬프트 인젝션·오작동 시 파일 삭제/시크릿(.env) 유출 유발",
        "our_solution": "SecurityGuard 최소 권한 정책(부서별 읽기/쓰기 화이트리스트 + 파괴적 명령/시크릿 접근 원천 차단)",
    },
    {
        "step": "⑤ 에이전트 만들기",
        "video_claim": "~/.claude/settings.json에 CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 활성화",
        "verdict": "COST_OPTIMIZED",
        "risk_found": "실험적 멀티 에이전트 팀을 매일 풀가동하면 토큰 소모가 3~5배 폭증(월 $78~$240+)",
        "our_solution": "settings.json 패치 생성 + 일상 점검/SEO/카드뉴스/CS는 원가 $0 Python 엔진이 수행하는 Tier-0 하이브리드",
    },
    {
        "step": "⑥ 부서 나누기",
        "video_claim": "기획·개발·디자인·CS·마케팅 5개 부서 + 총괄 마스터 대화형 생성",
        "verdict": "ADOPT_AND_CODE",
        "risk_found": "부서 간 파일 소유권 미지정 시 동일 파일 동시 수정(충돌) 및 책임 소재 불명확",
        "our_solution": ".claude/agents/ 6개 에이전트 정의서 + 소유권 매트릭스 + 실제 실행 가능한 5개 Python 부서 워커 구현",
    },
    {
        "step": "⑦ 자동화 걸기 + 거짓말 방지",
        "video_claim": "/schedule 매일 오전 9시 실행 + 마스터 검수 2줄 규칙(직접 확인·증거 제시)",
        "verdict": "HARDENED_GATE",
        "risk_found": "프롬프트 2줄만으로는 LLM이 '확인했다'고 거짓 보고(환각)할 확률을 0%로 낮출 수 없음",
        "our_solution": "MasterVerifier 코드 레벨 증거 게이트: 실제 파일 재오픈, SHA-256 대조, PNG 해상도·픽셀 검증 미통과 시 강제 REJECT",
    },
    {
        "step": "⑧ 수익화 세팅",
        "video_claim": "GSC 색인/노출 확인 → SEO 코드 반영 + 매일 SNS 카드뉴스 자동 생성",
        "verdict": "FULL_AUTOMATION",
        "risk_found": "GSC API 미연동 시 멈추거나, 검증 없는 자동 코드 수정으로 라이브 사이트 장애 위험",
        "our_solution": "GSC API 연동 + 오프라인 정밀 SEO/링크/JSON-LD 감사 + 안전한 Diff 패치 생성 + 1080×1350 카드뉴스 5장 즉시 렌더링",
    },
]


@dataclass
class CompanyConfig:
    company_name: str = field(default_factory=lambda: os.getenv("COMPANY_NAME", "AI Autonomous Web Corp"))
    site_domain: str = field(default_factory=lambda: os.getenv("SITE_DOMAIN", "https://dream8837z.github.io"))
    target_site_dirs: List[Path] = field(default_factory=list)
    output_dir: Path = OUTPUT_DIR
    data_dir: Path = DATA_DIR
    fonts_dir: Path = FONTS_DIR
    schedule_kst_hour: int = field(default_factory=lambda: int(os.getenv("SCHEDULE_KST_HOUR", "9")))
    schedule_kst_minute: int = field(default_factory=lambda: int(os.getenv("SCHEDULE_KST_MINUTE", "0")))
    monthly_token_budget_usd: float = field(default_factory=lambda: float(os.getenv("MONTHLY_TOKEN_BUDGET_USD", "15.0")))
    gsc_service_account_json: str = field(default_factory=lambda: os.getenv("GSC_SERVICE_ACCOUNT_JSON", ""))

    def __post_init__(self) -> None:
        if not self.target_site_dirs:
            env_dirs = os.getenv("TARGET_SITE_DIRS", "").strip()
            if env_dirs:
                self.target_site_dirs = [Path(p.strip()) for p in env_dirs.split(",") if p.strip()]
            else:
                existing = [p for p in DEFAULT_TARGET_SITES if p.exists()]
                self.target_site_dirs = existing if existing else [BASE_DIR]

    def resolve_font(self, weight: str = "bold") -> Path:
        candidates = {
            "black": ["Pretendard-Black.otf", "NotoSansKR-Bold.ttf"],
            "extrabold": ["Pretendard-ExtraBold.otf", "NotoSansKR-Bold.ttf"],
            "bold": ["NotoSansKR-Bold.ttf", "Pretendard-ExtraBold.otf", "Pretendard-Black.otf"],
        }.get(weight, ["NotoSansKR-Bold.ttf"])
        for name in candidates:
            p = self.fonts_dir / name
            if p.exists():
                return p
        fallback = Path("/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf")
        return fallback
