"""7-Day Omnichannel Promotion Pack Generator (Threads + YouTube Community + Naver Blog SEO + LinkedIn) with UTM Attribution."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Dict, List

from agency_engine.config import AgencyConfig, ClientBrief
from agency_engine.hooks_library import HooksLibrary

BASE_PUBLIC_URL = "https://dream8837z.github.io/shortform-agency/"

DAY_PLANS: List[Dict[str, str]] = [
    {"day": "1", "industry_slug": "clinic", "industry_ko": "피부과·성형외과 클리닉", "topic": "병원 릴스 대행 비용과 울쎄라 vs 써마지 비교 쇼폼", "a": "울쎄라", "b": "써마지", "naver_kw": "병원 릴스 대행 비용"},
    {"day": "2", "industry_slug": "lawyer", "industry_ko": "변호사·세무사 전문직", "topic": "변호사 쇼츠 외주 기획과 상담 문의 3배 만드는 3초 훅", "a": "표준계약서", "b": "구두합의", "naver_kw": "변호사 쇼츠 제작 외주"},
    {"day": "3", "industry_slug": "clinic", "industry_ko": "치과·임플란트 클리닉", "topic": "원장님 폰 촬영 3분으로 만드는 임플란트 비교 릴스", "a": "오스템", "b": "스트라우만", "naver_kw": "치과 숏폼 마케팅 대행"},
    {"day": "4", "industry_slug": "instructor", "industry_ko": "온라인 강사·컨설턴트", "topic": "강의 수강생 모으는 4단계 숏폼 대본과 댓글 DM 자동화", "a": "무료특강", "b": "유료광고", "naver_kw": "강사 릴스 편집 외주"},
    {"day": "5", "industry_slug": "local", "industry_ko": "로컬·커머스 브랜드", "topic": "광고비 0원 릴스 조회수 터뜨리는 무음 45% 자동 컷편집", "a": "AI 자동컷편집", "b": "수동 편집외주", "naver_kw": "숏폼 편집 외주 단가"},
    {"day": "6", "industry_slug": "clinic", "industry_ko": "비만·대사 클리닉", "topic": "마운자로 vs 위고비 의료법 심의 준수 교육형 쇼츠 제작법", "a": "마운자로", "b": "위고비", "naver_kw": "의료법 준수 병원 쇼츠"},
    {"day": "7", "industry_slug": "lawyer", "industry_ko": "전문직·B2B 대표", "topic": "3편 파일럿 본계약 전액 차감 & 10+2편 보너스 선착순 마감", "a": "파일럿 3편", "b": "월간 12편", "naver_kw": "B2B 숏폼 에이전시 추천"},
]


class OmnichannelPromoAutopilot:
    """Generates a ready-to-post 7-day multi-channel promotion calendar with per-channel UTM tracking links."""

    def __init__(self, config: AgencyConfig) -> None:
        self.config = config
        self.promo_dir = self.config.output_dir / "promo_pack"
        self.promo_dir.mkdir(parents=True, exist_ok=True)

    def generate_7day_pack(self, run_date: str) -> Dict[str, Any]:
        hooks_lib = HooksLibrary()
        days_out: List[Dict[str, Any]] = []

        for plan in DAY_PLANS:
            brief = ClientBrief(
                client_id=f"day{plan['day']}_{plan['industry_slug']}",
                client_name=plan["industry_ko"],
                industry=plan["industry_ko"],
                topic=plan["topic"],
                compare_a=plan["a"],
                compare_b=plan["b"],
                cta_action="댓글에 '체크리스트' 남기기",
            )
            top_hooks = hooks_lib.match_for_brief(brief, top_k=3)
            h1 = top_hooks[0]["rendered_hook"]
            h2 = top_hooks[1]["rendered_hook"] if len(top_hooks) > 1 else h1

            d = plan["day"]
            slug = plan["industry_slug"]
            u_threads = f"{BASE_PUBLIC_URL}?industry={slug}&utm_source=threads&utm_medium=organic_social&utm_campaign=7day_sprint&utm_content=day{d}"
            u_yt = f"{BASE_PUBLIC_URL}?industry={slug}&utm_source=youtube_community&utm_medium=organic_social&utm_campaign=7day_sprint&utm_content=day{d}"
            u_naver = f"{BASE_PUBLIC_URL}?industry={slug}&utm_source=naver_blog&utm_medium=seo&utm_campaign=7day_sprint&utm_content=day{d}"
            u_li = f"{BASE_PUBLIC_URL}?industry={slug}&utm_source=linkedin&utm_medium=b2b_social&utm_campaign=7day_sprint&utm_content=day{d}"

            channels = {
                "threads": {
                    "utm_url": u_threads,
                    "copy": (
                        f"{h1}\n\n"
                        f"{plan['industry_ko']} 대표님들이 스마트폰으로 3분만 찍어 보내시면\n"
                        "① 무음·NG 45% 자동 컷편집\n"
                        "② 방송 표준 -14 LUFS 마스터링 + 카라오케 자막\n"
                        "③ CapCut/Premiere 원본 ZIP 일괄 납품까지 끝내드립니다.\n\n"
                        f"👉 우리 업종 맞춤 3초 후킹 5개 & ROI 계산기 바로 해보기:\n{u_threads}"
                    ),
                },
                "youtube_community": {
                    "utm_url": u_yt,
                    "copy": (
                        f"[투표] {plan['industry_ko']} 숏폼 마케팅에서 가장 막막한 부분은?\n"
                        "1) 매번 터지는 3초 후킹 기획\n"
                        "2) NG·무음 컷편집 + 자막 시간 부족\n"
                        "3) 조회수가 실제 상담 문의로 안 이어짐\n\n"
                        f"🔥 업종별 무료 3초 후킹 15선 키트 & ROI 계산기 👉 {u_yt}"
                    ),
                },
                "naver_blog_seo": {
                    "target_keyword": plan["naver_kw"],
                    "utm_url": u_naver,
                    "copy": (
                        f"# {plan['naver_kw']} — 실패 없는 {plan['industry_ko']} 숏폼 제작 기준 3가지\n\n"
                        f"> 핵심 요약: {h2}\n\n"
                        f"## 1. 왜 {plan['a']} vs {plan['b']} 비교형 숏폼이 문의 전환이 높을까?\n"
                        "고객은 단순 홍보 영상은 0.3초 만에 넘기지만, 명확한 선택 기준표가 담긴 30~45초 릴스는 끝까지 시청하고 댓글로 문의합니다.\n\n"
                        "## 2. 대표님 촬영 시간 3분으로 줄이는 무인 제작 프로세스\n"
                        "- 1단계: 스마트폰으로 3~5분 자연스럽게 설명 녹화\n"
                        "- 2단계: 5축 리텐션 대본 기획 + 무음·NG 45% 자동 컷 + 방송급 -14 LUFS 오디오 마스터링\n"
                        "- 3단계: 최종 MP4 + CapCut/Premiere 원본 ZIP 납품 (무료 수정 2회, 착수금 50% 분할 결제)\n\n"
                        f"## 3. 우리 업종은 신규 고객 몇 명만 오면 본전일까? (무료 ROI 계산기)\n"
                        f"👉 [무료 ROI 계산기 & 맞춤 3초 후킹 5개 받기]({u_naver})"
                    ),
                },
                "linkedin": {
                    "utm_url": u_li,
                    "copy": (
                        f"{plan['industry_ko']} B2B 마케팅 팀장·대표님께 공유합니다.\n\n"
                        "월 25시간 이상 걸리던 숏폼 기획·컷편집을 4단계 리텐션 프레임워크와 방송급(-14 LUFS) 자동화 파이프라인으로 전환했을 때,\n"
                        "신규 고객 1~2명 유입만으로 월간 제작비 손익분기점(BEP)을 넘기는 구조를 설계할 수 있습니다.\n\n"
                        f"인터랙티브 B2B ROI 계산기와 업종별 3초 후킹 15선 키트를 무료로 공개해 두었습니다:\n{u_li}"
                    ),
                },
            }

            day_entry = {
                "day": int(d),
                "industry": plan["industry_ko"],
                "industry_slug": slug,
                "naver_keyword": plan["naver_kw"],
                "channels": channels,
            }
            days_out.append(day_entry)

            # Write individual day markdown
            md_parts = [f"# Day {d} 옴니채널 홍보팩 ({plan['industry_ko']} · {run_date})", ""]
            for ch_name, ch_data in channels.items():
                md_parts.append(f"## {ch_name.upper()}\n- UTM: `{ch_data['utm_url']}`\n\n```text\n{ch_data['copy']}\n```\n")
            (self.promo_dir / f"day{d}.md").write_text("\n".join(md_parts), encoding="utf-8")

        json_path = self.promo_dir / "7day_omnichannel_pack.json"
        json_path.write_text(json.dumps({"run_date": run_date, "days": days_out}, ensure_ascii=False, indent=2), encoding="utf-8")

        dash_path = self.promo_dir / "copy_paste_dashboard.html"
        dash_path.write_text(self._build_dashboard_html(days_out, run_date), encoding="utf-8")

        return {
            "json_path": str(json_path),
            "dashboard_html": str(dash_path),
            "total_days": len(days_out),
            "total_posts": len(days_out) * 4,
        }

    def _build_dashboard_html(self, days: List[Dict[str, Any]], run_date: str) -> str:
        blocks = []
        for d in days:
            cards = []
            for ch_k, ch_v in d["channels"].items():
                el_id = f"d{d['day']}_{ch_k}"
                cards.append(
                    f"<div class='card'><div class='hd'><strong>{html.escape(ch_k.upper())}</strong>"
                    f"<button onclick=\"navigator.clipboard.writeText(document.getElementById('{el_id}').textContent)\">복사</button></div>"
                    f"<pre id='{el_id}'>{html.escape(ch_v['copy'])}</pre></div>"
                )
            blocks.append(f"<h2>Day {d['day']} · {html.escape(d['industry'])} (SEO: {html.escape(d['naver_keyword'])})</h2><div class='grid'>{''.join(cards)}</div>")

        return f"""<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><title>7-Day Omnichannel Promo Pack ({run_date})</title>
<style>body{{margin:0;background:#09090b;color:#fafafa;font-family:-apple-system,sans-serif;padding:28px;max-width:1200px;margin:0 auto;}}
h1{{margin:0 0 8px;}}h2{{margin:28px 0 12px;color:#f5c451;font-size:17px;}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:12px;}}
.card{{background:#111114;border:1px solid #27272a;border-radius:10px;padding:14px;}}.hd{{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;}}
button{{background:#fafafa;color:#09090b;border:none;padding:5px 10px;border-radius:6px;font-weight:700;cursor:pointer;}}
pre{{white-space:pre-wrap;font-size:12px;color:#d4d4d8;background:#09090b;padding:10px;border-radius:8px;max-height:220px;overflow-y:auto;margin:0;}}</style></head>
<body><h1>7일 옴니채널 무인 홍보 복붙 대시보드 ({run_date})</h1><p style="color:#a1a1aa">Threads · YouTube Community · Naver Blog SEO · LinkedIn — 전 채널 UTM 어트리뷰션 자동 포함 (총 28개 포스트)</p>{''.join(blocks)}</body></html>"""
