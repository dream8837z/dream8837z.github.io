"""Department 5: 마케팅팀 (Marketing) — Multi-Channel SNS Distribution & UTM Monetization Pack."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from company_engine.config import CompanyConfig
from company_engine.master_verifier import compute_sha256


class MarketingDepartment:
    """Pairs Design team's 5-slide Card News with channel-optimized copy and UTM tracking links."""

    dept_id = "marketing"
    dept_name_ko = "마케팅팀"

    def __init__(self, config: CompanyConfig) -> None:
        self.config = config

    def run(
        self,
        run_date: str,
        planner_result: Dict[str, Any],
        design_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        out_dir = self.config.output_dir / "marketing"
        out_dir.mkdir(parents=True, exist_ok=True)

        base_url = self.config.site_domain.rstrip("/")
        campaign = f"ai_corp_{run_date.replace('-', '')}"
        slides = design_result.get("slides", [])
        brief = planner_result.get("daily_card_news_brief", {})
        p_sum = planner_result.get("summary", {})

        channels = {
            "instagram_carousel": {
                "channel_name": "Instagram 4:5 캐러셀 (5장)",
                "utm_url": f"{base_url}/?utm_source=instagram&utm_medium=card_news&utm_campaign={campaign}",
                "assets": [s["file_path"] for s in slides],
                "caption": (
                    f"{brief.get('cover_headline', '').replace(chr(10), ' ')}\n\n"
                    f"매일 아침 9시, AI 직원 5명이 사이트 {p_sum.get('total_html_pages_scanned', 0)}개 페이지를 자동 점검하고 "
                    f"SEO 평균 {p_sum.get('average_seo_score', 0)}점을 유지하는 무인 운영 리포트입니다.\n\n"
                    "✔ 총괄 마스터 SHA-256 증거 검증으로 거짓 보고 0%\n"
                    "✔ 토큰비 월 $138 → $3.60 하이브리드 최적화\n\n"
                    f"👉 프로필 링크에서 확인: {base_url}/?utm_source=instagram&utm_medium=card_news&utm_campaign={campaign}\n\n"
                    "#클로드코드 #AI자동화 #AI직원 #사이트운영 #SEO자동화 #부업자동화 #1인기업"
                ),
            },
            "youtube_community": {
                "channel_name": "YouTube 커뮤니티 포스트 (5장)",
                "utm_url": f"{base_url}/?utm_source=youtube&utm_medium=community&utm_campaign={campaign}",
                "assets": [s["file_path"] for s in slides],
                "caption": (
                    f"[오늘의 무인 사이트 운영 리포트 · {run_date}]\n"
                    f"AI 직원 5명이 방금 사이트 {p_sum.get('total_html_pages_scanned', 0)}개 페이지 SEO 감사를 마쳤습니다!\n"
                    "거짓말 방지 SHA-256 검증을 통과한 실제 결과와 무료 도구는 아래 링크에서 바로 확인해 보세요 👇\n"
                    f"{base_url}/?utm_source=youtube&utm_medium=community&utm_campaign={campaign}"
                ),
            },
            "threads_x_post": {
                "channel_name": "Threads / X 단문 스레드",
                "utm_url": f"{base_url}/?utm_source=threads&utm_medium=social&utm_campaign={campaign}",
                "assets": [slides[0]["file_path"]] if slides else [],
                "caption": (
                    f"AI 직원 5명에게 사이트를 맡길 때 가장 위험한 2가지:\n"
                    "1) 폴더 '항상 허용' 보안 사고\n"
                    "2) 일 안 하고 '다 했다'고 거짓 보고\n\n"
                    "그래서 최소 권한 가드 + SHA-256 기계적 검증 게이트로 완전 자동화했습니다.\n"
                    f"상세 결과 👉 {base_url}/?utm_source=threads&utm_medium=social&utm_campaign={campaign}"
                ),
            },
        }

        pack_payload = {
            "dept_id": self.dept_id,
            "dept_name_ko": self.dept_name_ko,
            "run_date": run_date,
            "campaign_id": campaign,
            "summary": {
                "channels_prepared": len(channels),
                "linked_card_slides": len(slides),
                "utm_tracking_enabled": True,
            },
            "channels": channels,
        }

        json_path = out_dir / f"{run_date}_social_pack.json"
        json_path.write_text(json.dumps(pack_payload, ensure_ascii=False, indent=2), encoding="utf-8")

        md_lines: List[str] = [f"# 마케팅팀 일일 멀티채널 배포 패키지 ({run_date})", ""]
        for key, ch in channels.items():
            md_lines.append(f"## {ch['channel_name']}")
            md_lines.append(f"- **UTM 링크**: `{ch['utm_url']}`")
            md_lines.append(f"- **연결 이미지**: {len(ch['assets'])}장")
            md_lines.append("")
            md_lines.append("```text")
            md_lines.append(ch["caption"])
            md_lines.append("```")
            md_lines.append("")

        md_path = out_dir / f"{run_date}_social_pack.md"
        md_path.write_text("\n".join(md_lines), encoding="utf-8")

        return {
            "dept_id": self.dept_id,
            "dept_name_ko": self.dept_name_ko,
            "status": "COMPLETED",
            "summary": pack_payload["summary"],
            "channels": channels,
            "json_path": str(json_path),
            "md_path": str(md_path),
            "evidence": [
                {
                    "label": "마케팅팀 멀티채널 배포 번들 JSON",
                    "type": "json",
                    "file_path": str(json_path),
                    "sha256": compute_sha256(json_path),
                },
                {
                    "label": "마케팅팀 채널별 카피·UTM 문서 MD",
                    "type": "file",
                    "file_path": str(md_path),
                    "sha256": compute_sha256(md_path),
                },
            ],
        }
