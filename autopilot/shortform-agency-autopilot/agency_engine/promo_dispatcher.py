"""v7.0 Full-Automation Omnichannel Promotion Dispatcher:
1. Auto-publishes daily compounding Korean B2B SEO/GEO Case-Study Blog Articles into `shortform-agency/blog/` + updates `sitemap.xml` ($0, zero API keys needed!).
2. Auto-submits URLs to IndexNow (Naver / Bing / Yandex instant search indexing).
3. Auto-publishes to Threads Graph API (when `THREADS_USER_ID` & `THREADS_ACCESS_TOKEN` are set) and/or Slack/Discord/Telegram Webhook (`PROMO_WEBHOOK_URL`).
"""

from __future__ import annotations

import html
import json
import os
import shutil
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from agency_engine.config import BASE_DIR, AgencyConfig
from agency_engine.promo_autopilot import BASE_PUBLIC_URL, DAY_PLANS, OmnichannelPromoAutopilot

KST = timezone(timedelta(hours=9))
GH_PAGES_REPO = BASE_DIR.parent / "dream8837z.github.io"


class FullAutoPromoDispatcher:
    """Zero-touch daily promotion engine: Compounding SEO/GEO Blog + IndexNow Ping + Threads API + Webhook."""

    def __init__(self, config: AgencyConfig | None = None) -> None:
        self.config = config or AgencyConfig()
        self.promo_dir = self.config.output_dir / "promo_pack"
        self.blog_local_dir = self.config.output_dir / "public_funnel" / "blog"
        self.promo_dir.mkdir(parents=True, exist_ok=True)
        self.blog_local_dir.mkdir(parents=True, exist_ok=True)

    def run_daily_promotion(self, run_date: str | None = None, sync_gh_pages: bool = True) -> Dict[str, Any]:
        date_str = run_date or datetime.now(KST).strftime("%Y-%m-%d")
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        day_idx = (dt.timetuple().tm_yday % len(DAY_PLANS))  # 0..6 deterministic daily rotation

        # Ensure 7-day promo pack exists
        pack_info = OmnichannelPromoAutopilot(self.config).generate_7day_pack(date_str)
        pack_data = json.loads(Path(pack_info["json_path"]).read_text(encoding="utf-8"))
        today_plan = pack_data["days"][day_idx]

        # 1. Auto-Publish Daily SEO/GEO Case-Study Blog Post (Compounding Organic Traffic — $0, 100% Autonomous!)
        blog_res = self._publish_daily_seo_blog(today_plan, date_str, sync_gh_pages=sync_gh_pages)

        # 2. Auto-Ping IndexNow (Naver / Bing instant crawl notification)
        urls_to_ping = [
            BASE_PUBLIC_URL,
            blog_res["public_url"],
            f"{BASE_PUBLIC_URL}magnets/{today_plan['industry_slug']}-hooks-kit.html",
        ]
        indexnow_res = self._ping_indexnow(urls_to_ping)

        # 3. Auto-Publish to Threads Graph API (if credentials configured in env/Secrets)
        threads_res = self._dispatch_threads_api(today_plan["channels"]["threads"]["copy"])

        # 4. Auto-Notify via Webhook (Slack / Discord / Telegram if PROMO_WEBHOOK_URL set)
        webhook_res = self._dispatch_webhook(today_plan, blog_res["public_url"], date_str)

        report = {
            "ok": True,
            "run_date": date_str,
            "day_slot": today_plan["day"],
            "industry": today_plan["industry"],
            "seo_blog_published": blog_res,
            "indexnow_ping": indexnow_res,
            "threads_api": threads_res,
            "webhook_notify": webhook_res,
        }
        log_path = self.promo_dir / f"{date_str}_dispatch_log.json"
        log_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return report

    def _publish_daily_seo_blog(self, day_plan: Dict[str, Any], run_date: str, sync_gh_pages: bool) -> Dict[str, Any]:
        from agency_engine.config import ClientBrief
        from agency_engine.hooks_library import HooksLibrary

        slug = f"{run_date}-{day_plan['industry_slug']}-shortform-guide"
        naver = day_plan["channels"]["naver_blog_seo"]
        kw = day_plan["naver_keyword"]
        ind = day_plan["industry"]
        utm_cta = f"{BASE_PUBLIC_URL}?industry={day_plan['industry_slug']}&utm_source=seo_blog&utm_medium=organic&utm_campaign={run_date}"
        public_url = f"{BASE_PUBLIC_URL}blog/{slug}.html"

        # Generate 5 unique industry-specific hooks so every daily article has distinct, high-value non-duplicate content
        brief = ClientBrief(
            client_id=slug, client_name=ind, industry=ind, topic=kw,
            compare_a=day_plan.get("industry_slug", "A안"), compare_b="기존 방식", cta_action="댓글 DM",
        )
        unique_hooks = HooksLibrary().match_for_brief(brief, top_k=5)
        hooks_li = "".join(f"<li><strong>[{html.escape(h['category_ko'])}]</strong> {html.escape(h['rendered_hook'])}</li>" for h in unique_hooks)
        naver_paragraphs = "".join(
            f"<p>{html.escape(line)}</p>"
            for line in naver["copy"].splitlines()
            if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("👉")
        )
        linkedin_note = html.escape(day_plan["channels"]["linkedin"]["copy"])

        article_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(kw)} — {html.escape(ind)} 숏폼 마케팅 실전 가이드 ({run_date})</title>
  <meta name="description" content="{html.escape(kw)}: {html.escape(ind)} 대표님·원장님을 위한 맞춤 3초 후킹 5선, 무음 45% 자동 컷편집, 방송급 -14 LUFS 릴스 제작 ROI 분석." />
  <link rel="canonical" href="{html.escape(public_url)}" />
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-J0Z7NXJMWJ"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-J0Z7NXJMWJ');</script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{html.escape(kw)} — {html.escape(ind)} 숏폼 마케팅 실전 가이드",
    "datePublished": "{run_date}",
    "author": {{ "@type": "Organization", "name": "Shortform Studio Pro" }},
    "mainEntityOfPage": "{html.escape(public_url)}"
  }}
  </script>
  <style>
    body{{margin:0;background:#09090b;color:#fafafa;font-family:'Pretendard',-apple-system,'Noto Sans KR',sans-serif;line-height:1.75;}}
    .wrap{{max-width:780px;margin:0 auto;padding:44px 20px 80px;}}
    .tag{{display:inline-block;padding:4px 12px;border-radius:999px;font-size:12px;font-weight:700;background:rgba(245,196,81,.12);color:#f5c451;border:1px solid rgba(245,196,81,.4);}}
    h1{{font-size:28px;line-height:1.3;margin:14px 0 12px;}}
    h2{{font-size:20px;color:#f5c451;margin:32px 0 10px;}}
    .box{{background:#111114;border:1px solid #27272a;border-radius:12px;padding:20px;margin:18px 0;}}
    .cta{{display:inline-block;background:#ff4d2e;color:#fff;padding:13px 22px;border-radius:10px;text-decoration:none;font-weight:800;margin-top:10px;}}
    a{{color:#f5c451;}}
  </style>
</head>
<body>
<article class="wrap">
  <span class="tag">{html.escape(ind)} · Day {day_plan['day']} 실전 리포트 · {run_date}</span>
  <h1>{html.escape(kw)} — 실패 없는 {html.escape(ind)} 숏폼 제작 전략</h1>
  <div class="box">{naver_paragraphs}</div>
  <h2>1. {html.escape(ind)} 전용 검증된 3초 후킹 TOP 5 ({html.escape(kw)})</h2>
  <ol>{hooks_li}</ol>
  <h2>2. B2B 의사결정권자 관점 ROI 요약</h2>
  <div class="box"><p style="white-space:pre-wrap;margin:0;">{linkedin_note}</p></div>
  <div class="box">
    <h2>3. 우리 업종은 신규 고객 몇 명만 오면 본전일까?</h2>
    <p>3편 파일럿(50만 원, 본계약 전환 시 100% 차감) 및 착수금 50% 분할 결제로 리스크 없이 시작하실 수 있습니다.</p>
    <a class="cta" href="{html.escape(utm_cta)}">무료 ROI 계산기 &amp; 맞춤 3초 후킹 5개 받기 →</a>
  </div>
  <p style="margin-top:32px;font-size:13px;color:#a1a1aa;"><a href="../index.html">← Shortform Studio Pro 메인으로 돌아가기</a> · <a href="index.html">전체 아카이브 보기</a></p>
</article>
</body>
</html>
"""
        local_article = self.blog_local_dir / f"{slug}.html"
        local_article.write_text(article_html, encoding="utf-8")

        # Update blog index
        articles = sorted(self.blog_local_dir.glob("20*.html"), reverse=True)
        list_items = "".join(
            f"<li><a href='{html.escape(a.name)}'>{html.escape(a.stem)}</a></li>" for a in articles[:50]
        )
        index_html = (
            "<!DOCTYPE html><html lang='ko'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>B2B 숏폼 마케팅 실전 인사이트 아카이브 — Shortform Studio Pro</title>"
            "<style>body{margin:0;background:#09090b;color:#fafafa;font-family:-apple-system,sans-serif;max-width:780px;margin:0 auto;padding:40px 20px;line-height:1.8;}a{color:#f5c451;}</style></head>"
            f"<body><h1>B2B 숏폼 마케팅 인사이트 아카이브</h1><ul>{list_items}</ul>"
            "<p><a href='../index.html'>← 메인 수주 페이지로 이동</a></p></body></html>"
        )
        (self.blog_local_dir / "index.html").write_text(index_html, encoding="utf-8")

        # Sync to GitHub Pages & append to shortform-agency/sitemap.xml
        gh_article = ""
        if sync_gh_pages and GH_PAGES_REPO.exists():
            gh_blog = GH_PAGES_REPO / "shortform-agency" / "blog"
            gh_blog.mkdir(parents=True, exist_ok=True)
            shutil.copy2(local_article, gh_blog / local_article.name)
            shutil.copy2(self.blog_local_dir / "index.html", gh_blog / "index.html")
            gh_article = str(gh_blog / local_article.name)

            sm_path = GH_PAGES_REPO / "shortform-agency" / "sitemap.xml"
            if sm_path.exists():
                sm_txt = sm_path.read_text(encoding="utf-8")
                if public_url not in sm_txt:
                    entry = f"  <url><loc>{html.escape(public_url)}</loc><lastmod>{run_date}</lastmod></url>\n</urlset>"
                    sm_path.write_text(sm_txt.replace("</urlset>", entry), encoding="utf-8")

        return {"local_path": str(local_article), "gh_pages_path": gh_article, "public_url": public_url}

    def _ping_indexnow(self, urls: List[str]) -> Dict[str, Any]:
        """Submits updated URLs to IndexNow (Bing / Naver / Yandex) at $0 cost."""
        key = os.getenv("INDEXNOW_KEY", "shortformstudiopro2026indexnowkey").strip()
        payload = json.dumps(
            {
                "host": "dream8837z.github.io",
                "key": key,
                "urlList": urls,
            }
        ).encode("utf-8")
        try:
            req = urllib.request.Request(
                "https://api.indexnow.org/indexnow",
                data=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as r:
                return {"status": "PINGED", "http_code": r.status, "urls_submitted": len(urls)}
        except Exception as exc:
            return {"status": "QUEUED_OFFLINE", "note": str(exc)[:120], "urls_submitted": len(urls)}

    def _dispatch_threads_api(self, text: str) -> Dict[str, Any]:
        uid = os.getenv("THREADS_USER_ID", "").strip()
        tok = os.getenv("THREADS_ACCESS_TOKEN", "").strip()
        if not uid or not tok:
            return {"status": "AWAITING_THREADS_TOKEN", "note": "Set THREADS_USER_ID & THREADS_ACCESS_TOKEN in GitHub Secrets for auto-posting"}
        try:
            # Step 1: Create Threads media container
            c_url = f"https://graph.threads.net/v1.0/{uid}/threads"
            c_data = urllib.parse.urlencode({"media_type": "TEXT", "text": text[:500], "access_token": tok}).encode("utf-8")
            with urllib.request.urlopen(urllib.request.Request(c_url, data=c_data, method="POST"), timeout=15) as r:
                cid = json.loads(r.read().decode("utf-8")).get("id", "")
            # Step 2: Publish container
            p_url = f"https://graph.threads.net/v1.0/{uid}/threads_publish"
            p_data = urllib.parse.urlencode({"creation_id": cid, "access_token": tok}).encode("utf-8")
            with urllib.request.urlopen(urllib.request.Request(p_url, data=p_data, method="POST"), timeout=15) as r:
                pub = json.loads(r.read().decode("utf-8"))
            return {"status": "PUBLISHED", "thread_id": pub.get("id", "")}
        except Exception as exc:
            return {"status": "ERROR", "error": str(exc)[:160]}

    def _dispatch_webhook(self, day_plan: Dict[str, Any], blog_url: str, run_date: str) -> Dict[str, Any]:
        hook_url = os.getenv("PROMO_WEBHOOK_URL", "").strip()
        if not hook_url:
            return {"status": "AWAITING_WEBHOOK_URL", "note": "Optional: set PROMO_WEBHOOK_URL (Slack/Discord) for daily push"}
        msg = (
            f"[Shortform Auto-Promo · {run_date}] Day {day_plan['day']} ({day_plan['industry']})\n"
            f"• SEO 블로그 자동 발행 완료: {blog_url}\n"
            f"• Threads 추천글:\n{day_plan['channels']['threads']['copy']}"
        )
        try:
            body = json.dumps({"content": msg, "text": msg}, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(hook_url, data=body, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as r:
                return {"status": "NOTIFIED", "http_code": r.status}
        except Exception as exc:
            return {"status": "ERROR", "error": str(exc)[:120]}


if __name__ == "__main__":
    out = FullAutoPromoDispatcher().run_daily_promotion()
    print(json.dumps(out, ensure_ascii=False, indent=2))
