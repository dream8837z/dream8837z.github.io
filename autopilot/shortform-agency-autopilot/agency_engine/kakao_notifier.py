"""Daily 18:00 KST KakaoTalk '나에게 보내기' (Send to Me) Executive Report Notifier."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

from agency_engine.config import BASE_DIR, AgencyConfig
from agency_engine.evolution_engine import load_learned_policy

KST = timezone(timedelta(hours=9))
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_MEMO_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
PUBLIC_URL = "https://dream8837z.github.io/shortform-agency/"


def _load_kakao_creds() -> Dict[str, str]:
    env_map: Dict[str, str] = {}
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            env_map[k.strip().removeprefix("export ").strip()] = v.strip().strip('"').strip("'")
    for key in ("KAKAO_REST_API_KEY", "KAKAO_REFRESH_TOKEN", "KAKAO_CLIENT_SECRET"):
        if os.getenv(key):
            env_map[key] = os.getenv(key, "")
    return {
        "rest_api_key": env_map.get("KAKAO_REST_API_KEY", "").strip(),
        "refresh_token": env_map.get("KAKAO_REFRESH_TOKEN", "").strip(),
        "client_secret": env_map.get("KAKAO_CLIENT_SECRET", "").strip(),
    }


def _refresh_kakao_access_token(creds: Dict[str, str]) -> str:
    form: Dict[str, str] = {
        "grant_type": "refresh_token",
        "client_id": creds["rest_api_key"],
        "refresh_token": creds["refresh_token"],
    }
    if creds.get("client_secret"):
        form["client_secret"] = creds["client_secret"]
    req = urllib.request.Request(
        KAKAO_TOKEN_URL,
        data=urllib.parse.urlencode(form).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode("utf-8"))
    token = data.get("access_token", "")
    if not token:
        raise RuntimeError(f"Kakao token refresh failed: {data}")
    return token


def build_daily_kakao_summary(config: AgencyConfig | None = None, run_date: str | None = None) -> str:
    cfg = config or AgencyConfig()
    date_str = run_date or datetime.now(KST).strftime("%Y-%m-%d")
    policy = load_learned_policy()

    # 1. Shortform Agency manifest metrics
    proj_count = 0
    avg_comp = 0.0
    manifests = sorted(cfg.output_dir.glob("*_agency_manifest.json"))
    if manifests:
        try:
            m = json.loads(manifests[-1].read_text(encoding="utf-8"))
            proj_count = len(m.get("projects", []))
            avg_comp = float(m.get("avg_compression_pct", 0.0))
        except Exception:
            pass

    # 2. CRM leads & projected MRR
    leads_count = 0
    mrr = 0
    crm_file = cfg.output_dir / "crm" / "leads_crm.json"
    if crm_file.exists():
        try:
            leads = json.loads(crm_file.read_text(encoding="utf-8"))
            leads_count = len(leads)
            mrr = sum(int(l.get("expected_mrr_krw", 0)) for l in leads if l.get("stage") != "LOST")
        except Exception:
            pass

    # 3. YouTube Shorts publish result
    yt_status = "대기"
    yt_log = cfg.output_dir / "publish_queue" / "last_publish_result.json"
    if yt_log.exists():
        try:
            yl = json.loads(yt_log.read_text(encoding="utf-8"))
            yt_status = yl.get("mode", "확인완료")
        except Exception:
            pass

    # 4. Daily SEO blog status
    blog_url = f"{PUBLIC_URL}blog/"
    dispatch_logs = sorted((cfg.output_dir / "promo_pack").glob("*_dispatch_log.json"))
    if dispatch_logs:
        try:
            dl = json.loads(dispatch_logs[-1].read_text(encoding="utf-8"))
            blog_url = dl.get("seo_blog_published", {}).get("public_url", blog_url)
        except Exception:
            pass

    return (
        f"[오후 6시 무인 자동화 일일 리포트 · {date_str}]\n\n"
        f"▶ 숏폼 에이전시 (Gen #{policy.get('generation', 0)} · v{policy.get('policy_version', 1)})\n"
        f"• 렌더링 릴스: {proj_count}편 (무음·NG -{avg_comp}%)\n"
        f"• YouTube 배포: {yt_status}\n"
        f"• CRM 리드: {leads_count}건 (예상 MRR {mrr:,}원)\n"
        f"• 학습 정책: TTS +{policy.get('tts_rate_pct', 14)}% / DM '{policy.get('dm_trigger_keyword', '비교표')}'\n\n"
        f"▶ 오늘의 SEO 블로그:\n{blog_url}"
    )


def send_kakao_to_me(dry_run: bool = False) -> Dict[str, Any]:
    text = build_daily_kakao_summary()
    creds = _load_kakao_creds()
    ready = bool(creds["rest_api_key"] and creds["refresh_token"])

    template_object = {
        "object_type": "text",
        "text": text[:200],  # Kakao text template max 200 chars for guaranteed delivery
        "link": {"web_url": PUBLIC_URL, "mobile_web_url": PUBLIC_URL},
        "button_title": "수주 페이지 & 리포트 보기",
    }

    if dry_run or not ready:
        return {
            "ok": True,
            "mode": "DRY_RUN_VERIFIED" if dry_run else "AWAITING_KAKAO_SECRETS",
            "creds_ready": ready,
            "message_preview": text,
            "template_object": template_object,
        }

    access_token = _refresh_kakao_access_token(creds)
    req = urllib.request.Request(
        KAKAO_MEMO_URL,
        data=urllib.parse.urlencode({"template_object": json.dumps(template_object, ensure_ascii=False)}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read().decode("utf-8"))

    return {
        "ok": resp.get("result_code") == 0,
        "mode": "SENT_KAKAO_MEMO",
        "result": resp,
        "sent_at_kst": datetime.now(KST).isoformat(timespec="seconds"),
    }


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Send Daily 18:00 KST Executive Report via KakaoTalk '나에게 보내기'")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    print(json.dumps(send_kakao_to_me(dry_run=args.dry_run), ensure_ascii=False, indent=2))
