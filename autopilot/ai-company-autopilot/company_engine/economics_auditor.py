"""Token Unit Economics & Site Monetization BEP Auditor."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class OperatingTier:
    tier_id: str
    name: str
    architecture: str
    monthly_fixed_usd: float
    monthly_api_usd: float
    monthly_total_usd: float
    bep_adsense_pv: int
    bep_cpa_conversions: int
    recommended: bool
    verdict_ko: str


class EconomicsAuditor:
    """Computes realistic monthly token burn and monetization break-even points."""

    # Conservative Korean/Global finance-tech web benchmarks
    ADSENSE_RPM_USD: float = 3.50  # $3.50 per 1,000 pageviews
    CPA_COMMISSION_USD: float = 12.00  # Avg financial/SaaS CPA conversion

    def evaluate_tiers(self, monthly_budget_usd: float = 15.0) -> Dict[str, Any]:
        tiers: List[OperatingTier] = [
            self._build_tier(
                tier_id="tier0_hybrid_autopilot",
                name="Tier-0: 하이브리드 무인 오토파일럿 (본 시스템)",
                architecture="일일 SEO·헬스체크·카드뉴스·CS분류 Python 무인 엔진($0) + 주간 고난도 기획만 선택적 LLM 호출",
                monthly_fixed_usd=0.0,
                monthly_api_usd=3.60,
                recommended=True,
                verdict_ko="최적 — 월 $3.60(또는 완전 로컬 $0)로 트래픽 초기 단계부터 흑자 구조 확보",
            ),
            self._build_tier(
                tier_id="tier1_claude_pro_single",
                name="Tier-1: Claude Code Pro 단일 세션",
                architecture="PC 상시 가동 + 단일 대화창 /schedule 실행 (팀 기능 미사용)",
                monthly_fixed_usd=20.0,
                monthly_api_usd=0.0,
                recommended=False,
                verdict_ko="주의 — PC 절전 시 중단되며 5개 부서 동시 실행 시 5시간 사용량 한도(Rate Limit) 도달",
            ),
            self._build_tier(
                tier_id="tier2_agent_teams_daily_api",
                name="Tier-2: 5인 에이전트 팀 매일 풀가동 (영상 원안 API 기준)",
                architecture="CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 + 6개 세션(5부서+마스터) 매일 09:00 풀가동",
                monthly_fixed_usd=0.0,
                monthly_api_usd=138.0,
                recommended=False,
                verdict_ko="적자 위험 — 월 39,500 PV 이상 확보 전에는 토큰비가 수익을 초과(영상 8단계 경고와 일치)",
            ),
        ]

        within_budget = [t.tier_id for t in tiers if t.monthly_total_usd <= monthly_budget_usd]
        return {
            "monthly_budget_usd": monthly_budget_usd,
            "benchmarks": {
                "adsense_rpm_usd": self.ADSENSE_RPM_USD,
                "cpa_commission_usd": self.CPA_COMMISSION_USD,
            },
            "tiers": [asdict(t) for t in tiers],
            "budget_compliant_tiers": within_budget,
            "recommended_tier": "tier0_hybrid_autopilot",
            "savings_vs_full_agent_teams_usd_per_month": round(138.0 - 3.60, 2),
        }

    def _build_tier(
        self,
        tier_id: str,
        name: str,
        architecture: str,
        monthly_fixed_usd: float,
        monthly_api_usd: float,
        recommended: bool,
        verdict_ko: str,
    ) -> OperatingTier:
        total = round(monthly_fixed_usd + monthly_api_usd, 2)
        bep_pv = int(round((total / self.ADSENSE_RPM_USD) * 1000)) if total > 0 else 0
        bep_cpa = max(1, int(round(total / self.CPA_COMMISSION_USD))) if total > 0 else 0
        return OperatingTier(
            tier_id=tier_id,
            name=name,
            architecture=architecture,
            monthly_fixed_usd=monthly_fixed_usd,
            monthly_api_usd=monthly_api_usd,
            monthly_total_usd=total,
            bep_adsense_pv=bep_pv,
            bep_cpa_conversions=bep_cpa,
            recommended=recommended,
            verdict_ko=verdict_ko,
        )
