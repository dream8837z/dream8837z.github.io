"""YouTube Data API v3 Auto-Publisher for Shortform Agency Autopilot (reuses existing OAuth2 .env)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from agency_engine.config import BASE_DIR, AgencyConfig

KST = timezone(timedelta(hours=9))
OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
YOUTUBE_UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
YOUTUBE_COMMENT_URL = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet"
SHARED_ENV_PATH = BASE_DIR.parent / "youtube-shorts-autopilot" / ".env"


def _load_env_file(path: Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _get_youtube_creds() -> Dict[str, str]:
    merged = _load_env_file(SHARED_ENV_PATH)
    merged.update(_load_env_file(BASE_DIR / ".env"))
    for key in ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"):
        if os.getenv(key):
            merged[key] = os.getenv(key, "")
    return {
        "client_id": merged.get("YOUTUBE_CLIENT_ID", "").strip(),
        "client_secret": merged.get("YOUTUBE_CLIENT_SECRET", "").strip(),
        "refresh_token": merged.get("YOUTUBE_REFRESH_TOKEN", "").strip(),
    }


def _refresh_access_token(creds: Dict[str, str]) -> str:
    body = urllib.parse.urlencode(
        {
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "refresh_token": creds["refresh_token"],
            "grant_type": "refresh_token",
        }
    ).encode("utf-8")
    req = urllib.request.Request(OAUTH_TOKEN_URL, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode("utf-8"))
    token = data.get("access_token", "")
    if not token:
        raise RuntimeError("Empty OAuth2 access_token returned")
    return token


def _upload_single_video(token: str, item: Dict[str, Any]) -> Dict[str, Any]:
    mp4_path = Path(item["mp4_path"])
    video_bytes = mp4_path.read_bytes()

    snippet_body = json.dumps(
        {
            "snippet": {
                "title": item["youtube_title"][:100],
                "description": item["youtube_description"][:5000],
                "tags": item.get("tags") or [item.get("client_name", "Shorts"), item.get("industry", "리뷰"), "Shorts"],
                "categoryId": str(item.get("category_id") or "22"),
                "defaultLanguage": "ko",
                "defaultAudioLanguage": "ko",
            },
            "status": {
                "privacyStatus": item.get("privacy_status", "public"),
                "selfDeclaredMadeForKids": False,
            },
        },
        ensure_ascii=False,
    ).encode("utf-8")

    init_req = urllib.request.Request(
        YOUTUBE_UPLOAD_URL,
        data=snippet_body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Length": str(len(video_bytes)),
            "X-Upload-Content-Type": "video/mp4",
        },
        method="POST",
    )
    with urllib.request.urlopen(init_req, timeout=30) as init_resp:
        upload_url = init_resp.headers.get("Location", "")
    if not upload_url:
        raise RuntimeError("Missing YouTube resumable upload Location header")

    put_req = urllib.request.Request(
        upload_url,
        data=video_bytes,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "video/mp4",
            "Content-Length": str(len(video_bytes)),
        },
        method="PUT",
    )
    with urllib.request.urlopen(put_req, timeout=180) as put_resp:
        uploaded = json.loads(put_resp.read().decode("utf-8"))

    video_id = uploaded.get("id", "")
    comment_ok = False
    if video_id and item.get("pinned_comment"):
        try:
            c_body = json.dumps(
                {
                    "snippet": {
                        "videoId": video_id,
                        "topLevelComment": {"snippet": {"textOriginal": item["pinned_comment"]}},
                    }
                },
                ensure_ascii=False,
            ).encode("utf-8")
            c_req = urllib.request.Request(
                YOUTUBE_COMMENT_URL,
                data=c_body,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(c_req, timeout=15):
                comment_ok = True
        except Exception:
            comment_ok = False

    return {
        "client_id": item["client_id"],
        "status": "UPLOADED",
        "video_id": video_id,
        "shorts_url": f"https://www.youtube.com/shorts/{video_id}" if video_id else "",
        "comment_posted": comment_ok,
        "uploaded_at_kst": datetime.now(KST).isoformat(timespec="seconds"),
    }


def publish_latest_queue(max_uploads: int = 1, dry_run: bool = False) -> Dict[str, Any]:
    cfg = AgencyConfig()
    q_dir = cfg.output_dir / "publish_queue"
    q_files = sorted(q_dir.glob("*_youtube_shorts_queue.json"))
    if not q_files:
        return {"ok": False, "error": "No publish queue found"}

    q_path = q_files[-1]
    items: List[Dict[str, Any]] = json.loads(q_path.read_text(encoding="utf-8"))
    creds = _get_youtube_creds()
    creds_ready = all(bool(creds[k]) for k in ("client_id", "client_secret", "refresh_token"))

    results: List[Dict[str, Any]] = []
    if dry_run or not creds_ready:
        for item in items[:max_uploads]:
            results.append(
                {
                    "client_id": item["client_id"],
                    "status": "DRY_RUN_VERIFIED" if dry_run else "AWAITING_OAUTH_TOKEN",
                    "mp4_exists": Path(item["mp4_path"]).exists(),
                    "title": item["youtube_title"],
                    "funnel_utm_url": item["funnel_utm_url"],
                }
            )
    else:
        token = _refresh_access_token(creds)
        uploaded_count = 0
        for item in items:
            if item.get("upload_status") == "UPLOADED" or uploaded_count >= max_uploads:
                continue
            res = _upload_single_video(token, item)
            item["upload_status"] = "UPLOADED"
            item["shorts_url"] = res["shorts_url"]
            results.append(res)
            uploaded_count += 1
        q_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "ok": True,
        "creds_ready": creds_ready,
        "mode": "LIVE_UPLOAD" if (creds_ready and not dry_run) else ("DRY_RUN" if dry_run else "AWAITING_OAUTH"),
        "queue_file": str(q_path),
        "results": results,
    }
    log_path = q_dir / "last_publish_result.json"
    log_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Publish queued Shortform Agency reels to YouTube Shorts")
    p.add_argument("--max", type=int, default=1)
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    out = publish_latest_queue(max_uploads=a.max, dry_run=a.dry_run)
    print(json.dumps(out, ensure_ascii=False, indent=2))
