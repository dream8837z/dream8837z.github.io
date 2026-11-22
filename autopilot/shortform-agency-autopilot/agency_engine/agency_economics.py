"""Realistic B2B Short-form Agency Unit Economics, CAC & Net Margin Simulator."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class AgencyPackageTier:
    tier_id: str
    name: str
    videos_delivered: int
    package_price_krw: int
    unit_price_krw: int
    ai_edit_minutes_per_video: int
    planning_and_revision_minutes_per_video: int
    total_hours_per_package: float
    estimated_cac_krw: int
    net_profit_per_package_krw: int
    effective_hourly_rate_krw: int
    clients_for_500k_krw: int
    clients_for_3m_krw: int
    clients_for_10m_krw: int
    positioning_note: str


class AgencyEconomicsAuditor:
    """Computes honest hourly rates, CAC, and client counts needed for revenue milestones."""

    def evaluate(self) -> Dict[str, Any]:
        tiers: List[AgencyPackageTier] = [
            self._calc(
                tier_id="tier1_portfolio_entry",
                name="1단계: 포트폴리오 진입형 (Threads·숨고 초저가)",
                videos_delivered=10,
                package_price_krw=500_000,
                ai_edit_min=8,
                plan_rev_min=22,
                cac_krw=30_000,
                note="초기 레퍼런스·후기 10개 확보 구간. Threads 무료 3편 샘플 후 10편 50만원 업셀링",
            ),
            self._calc(
                tier_id="tier2_standard_retainer",
                name="2단계: 스탠다드 월간 리테이너 (기획+편집+자막)",
                videos_delivered=10,
                package_price_krw=1_500_000,
                ai_edit_min=8,
                plan_rev_min=32,
                cac_krw=120_000,
                note="4단계 대본 기획 + AI 컷편집 + 2회 수정 포함. 1인 부업자 현실 주력 상품",
            ),
            self._calc(
                tier_id="tier3_premium_bonus12",
                name="3단계: 전문직 프리미엄 (10편 가격에 12편 보너스 전략)",
                videos_delivered=12,
                package_price_krw=2_500_000,
                ai_edit_min=8,
                plan_rev_min=37,
                cac_krw=250_000,
                note="의사·변호사·클리닉 타깃. 영상 속 '편당 25만(10편 250만)+2편 보너스' + 성과 리포트 필수",
            ),
        ]

        return {
            "currency": "KRW",
            "reality_check_summary": (
                "영상은 '6분 편집 = 25만원(시급 250만원)'처럼 보이지만, 실제로는 기획·클라이언트 소통·수정 2회·"
                "영업 CAC를 포함해 편당 약 30~45분이 소요됩니다. 그럼에도 AI 자동 컷편집 덕분에 실질 시급 15만~25만원의 "
                "고효율 B2B 모델은 충분히 성립합니다."
            ),
            "tiers": [asdict(t) for t in tiers],
        }

    def _calc(
        self,
        tier_id: str,
        name: str,
        videos_delivered: int,
        package_price_krw: int,
        ai_edit_min: int,
        plan_rev_min: int,
        cac_krw: int,
        note: str,
    ) -> AgencyPackageTier:
        total_min = videos_delivered * (ai_edit_min + plan_rev_min)
        total_hours = round(total_min / 60.0, 1)
        net_profit = max(1, package_price_krw - cac_krw)
        hourly = int(round(net_profit / total_hours)) if total_hours > 0 else 0
        return AgencyPackageTier(
            tier_id=tier_id,
            name=name,
            videos_delivered=videos_delivered,
            package_price_krw=package_price_krw,
            unit_price_krw=int(round(package_price_krw / videos_delivered)),
            ai_edit_minutes_per_video=ai_edit_min,
            planning_and_revision_minutes_per_video=plan_rev_min,
            total_hours_per_package=total_hours,
            estimated_cac_krw=cac_krw,
            net_profit_per_package_krw=net_profit,
            effective_hourly_rate_krw=hourly,
            clients_for_500k_krw=max(1, -(-500_000 // net_profit)),
            clients_for_3m_krw=max(1, -(-3_000_000 // net_profit)),
            clients_for_10m_krw=max(1, -(-10_000_000 // net_profit)),
            positioning_note=note,
        )
