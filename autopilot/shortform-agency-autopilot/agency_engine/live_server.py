"""Pro v4.0 Hardened Live Automation Server:
- Security Hardening: 64KB JSON / 150MB MP4 caps (413), MP4/MOV/WebM magic-byte check, param clamping, Path Traversal guards
- Non-blocking Concurrency: FFmpeg/TTS runs outside self.lock + Atomic os.replace() manifest/HTML writes
- One-Click Client Handoff ZIP Streaming API (`GET /api/download-bundle/<client_id>`)
- Live CRM Lead Capture (`POST /api/lead`) & Stage Transition (`POST /api/crm/stage`)
- Fault-Isolated Inbox Auto-Watcher (`inbox/` -> `inbox/processed/` or `inbox/failed/`)
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import threading
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

from agency_engine.config import AgencyConfig, ClientBrief
from agency_engine.evolution_engine import AutonomousEvolutionEngine
from agency_engine.hooks_library import HooksLibrary
from agency_engine.monetization_engine import MonetizationEngine
from agency_engine.pipeline import run_agency_pipeline
from agency_engine.script_planner import ScriptPlanner
from agency_engine.studio_builder import AgencyStudioBuilder
from agency_engine.video_autocutter import VideoAutoCutter

KST = timezone(timedelta(hours=9))
MAX_JSON_BYTES = 64 * 1024
MAX_VIDEO_BYTES = 150 * 1024 * 1024
SAFE_ID_RE = re.compile(r"^[a-z0-9_]{1,64}$")


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return cleaned[:48] or f"client_{int(time.time())}"


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + f".tmp.{os.getpid()}.{threading.get_ident()}")
    tmp_path.write_text(content, encoding="utf-8")
    os.replace(tmp_path, path)


def _is_valid_video_magic(header: bytes) -> bool:
    if len(header) < 12:
        return False
    # MP4/MOV ISO BMFF (`ftyp` at offset 4) or WebM/MKV (`1A 45 DF A3`)
    if header[4:8] == b"ftyp":
        return True
    if header[:4] == b"\x1a\x45\xdf\xa3":
        return True
    return False


class AgencyAutomationDaemon:
    """Watches `inbox/` safely and serves non-blocking live video & monetization APIs."""

    def __init__(self, config: AgencyConfig | None = None) -> None:
        self.config = config or AgencyConfig()
        self.inbox_dir = self.config.output_dir.parent / "inbox"
        self.processed_dir = self.inbox_dir / "processed"
        self.failed_dir = self.inbox_dir / "failed"
        self.uploads_dir = self.config.output_dir / "uploads"
        for d in (self.inbox_dir, self.processed_dir, self.failed_dir, self.uploads_dir):
            d.mkdir(parents=True, exist_ok=True)

        self.started_at = datetime.now(KST).isoformat(timespec="seconds")
        self.lock = threading.Lock()
        self._stop_event = threading.Event()
        self._watcher_thread: threading.Thread | None = None
        self.latest_payload: Dict[str, Any] = {}
        self.processed_inbox_count = 0
        self.autocut_jobs: list[Dict[str, Any]] = []

    def bootstrap(self) -> Dict[str, Any]:
        with self.lock:
            manifests = sorted(self.config.output_dir.glob("*_agency_manifest.json"))
            if manifests and (self.config.output_dir / "studio" / "index.html").exists():
                self.latest_payload = json.loads(manifests[-1].read_text(encoding="utf-8"))
                return self.latest_payload
            self.latest_payload = run_agency_pipeline(config=self.config)
            return self.latest_payload

    def process_real_mp4_file(
        self,
        in_path: Path,
        job_dir: Path,
        silence_db: int = -32,
        min_silence_sec: float = 0.45,
    ) -> Dict[str, Any]:
        # Clamp parameters safely
        silence_db = max(-60, min(-10, int(silence_db)))
        min_silence_sec = max(0.15, min(3.0, float(min_silence_sec)))

        # Run heavy FFmpeg OUTSIDE self.lock (non-blocking concurrency)
        cutter = VideoAutoCutter(self.config)
        result = cutter.cut_uploaded_mp4(
            input_mp4=in_path,
            out_dir=job_dir,
            silence_db=silence_db,
            min_silence_sec=min_silence_sec,
        )
        with self.lock:
            self.autocut_jobs.insert(0, result)
        return result

    def process_real_mp4_bytes(
        self,
        filename: str,
        raw_bytes: bytes,
        silence_db: int = -32,
        min_silence_sec: float = 0.45,
    ) -> Dict[str, Any]:
        if not _is_valid_video_magic(raw_bytes[:16]):
            raise ValueError("Invalid video file signature (expected MP4/MOV/WebM)")
        safe_stem = _slugify(Path(filename).stem)
        ext = Path(filename).suffix.lower() or ".mp4"
        if ext not in (".mp4", ".mov", ".m4v", ".webm"):
            ext = ".mp4"
        job_dir = self.uploads_dir / f"{int(time.time())}_{safe_stem}"
        job_dir.mkdir(parents=True, exist_ok=True)
        in_path = job_dir / f"{safe_stem}_original{ext}"
        in_path.write_bytes(raw_bytes)
        return self.process_real_mp4_file(in_path, job_dir, silence_db=silence_db, min_silence_sec=min_silence_sec)

    def generate_new_client(self, req: Dict[str, Any]) -> Dict[str, Any]:
        client_name = str(req.get("client_name", "")).strip()[:80] or "신규 B2B 클라이언트"
        industry = str(req.get("industry", "")).strip()[:60] or "전문직·로컬 비즈니스"
        topic = str(req.get("topic", "")).strip()[:120] or "고객이 절대 모르는 핵심 선택 기준 3가지"
        compare_a = str(req.get("compare_a", "")).strip()[:40] or "A방식"
        compare_b = str(req.get("compare_b", "")).strip()[:40] or "B방식"
        cta_action = str(req.get("cta_action", "")).strip()[:140] or "팔로우하고 댓글에 '가이드' 남기면 무료 체크리스트 DM 발송"
        persona_tone = str(req.get("persona_tone", "professional")).strip()
        if persona_tone not in ("professional", "friendly", "busan"):
            persona_tone = "professional"

        cid = _slugify(f"{client_name}_{int(time.time()) % 10000}")
        brief = ClientBrief(
            client_id=cid,
            client_name=client_name,
            industry=industry,
            topic=topic,
            compare_a=compare_a,
            compare_b=compare_b,
            cta_action=cta_action,
            persona_tone=persona_tone,
        )

        # Run Edge-TTS + FFmpeg OUTSIDE self.lock
        date_str = datetime.now(KST).strftime("%Y-%m-%d")
        script_plan = ScriptPlanner(HooksLibrary()).plan_for_brief(brief)
        deliverable = VideoAutoCutter(self.config).process_client_project(script_plan, date_str)
        new_project = {"script": script_plan, "deliverable": deliverable}

        mon = MonetizationEngine(self.config)
        handoff_zip = mon.build_client_handoff_bundle(new_project, date_str)
        new_project["deliverable"]["handoff_zip_path"] = str(handoff_zip)

        with self.lock:
            if not self.latest_payload:
                self.latest_payload = run_agency_pipeline(config=self.config, run_date=date_str)
            self.latest_payload["projects"].insert(0, new_project)
            projects = self.latest_payload["projects"]
            self.latest_payload["avg_compression_pct"] = round(
                sum(p["deliverable"]["compression_pct"] for p in projects) / len(projects), 1
            )
            manifest_path = self.config.output_dir / f"{date_str}_agency_manifest.json"
            _atomic_write_text(manifest_path, json.dumps(self.latest_payload, ensure_ascii=False, indent=2))
            tmp_html = self.config.output_dir / "studio" / f".index.{os.getpid()}.tmp.html"
            AgencyStudioBuilder().build(self.latest_payload, tmp_html)
            os.replace(tmp_html, self.config.output_dir / "studio" / "index.html")

        return new_project

    def get_handoff_zip(self, client_id: str) -> Path:
        if not SAFE_ID_RE.match(client_id):
            raise ValueError("Invalid client_id")
        with self.lock:
            projects = list(self.latest_payload.get("projects", []))
            run_date = self.latest_payload.get("run_date") or datetime.now(KST).strftime("%Y-%m-%d")
        match = next((p for p in projects if p["script"]["client_id"] == client_id), None)
        if match is None:
            raise FileNotFoundError(f"Client not found: {client_id}")
        zip_path = MonetizationEngine(self.config).build_client_handoff_bundle(match, run_date).resolve()
        if not zip_path.is_relative_to(self.config.output_dir.resolve()):
            raise PermissionError("Path traversal blocked")
        return zip_path

    def poll_inbox_once(self) -> int:
        processed = 0
        for json_file in sorted(self.inbox_dir.glob("*.json")):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                self.generate_new_client(data)
                json_file.rename(self.processed_dir / f"{int(time.time())}_{json_file.name}")
                with self.lock:
                    self.processed_inbox_count += 1
                processed += 1
            except Exception as exc:
                json_file.rename(self.failed_dir / f"{int(time.time())}_{json_file.name}")
                (self.failed_dir / f"{json_file.name}.error.txt").write_text(str(exc), encoding="utf-8")

        for mp4_file in sorted(self.inbox_dir.glob("*.mp4")):
            try:
                self.process_real_mp4_bytes(mp4_file.name, mp4_file.read_bytes())
                mp4_file.rename(self.processed_dir / f"{int(time.time())}_{mp4_file.name}")
                with self.lock:
                    self.processed_inbox_count += 1
                processed += 1
            except Exception as exc:
                mp4_file.rename(self.failed_dir / f"{int(time.time())}_{mp4_file.name}")
                (self.failed_dir / f"{mp4_file.name}.error.txt").write_text(str(exc), encoding="utf-8")
        return processed

    def start_watcher(self, interval_sec: float = 5.0) -> None:
        def _loop() -> None:
            while not self._stop_event.is_set():
                self.poll_inbox_once()
                self._stop_event.wait(interval_sec)

        self._watcher_thread = threading.Thread(target=_loop, daemon=True, name="inbox-watcher")
        self._watcher_thread.start()

    def stop_watcher(self) -> None:
        self._stop_event.set()

    def status_dict(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "status": "RUNNING",
                "version": "4.0.0-broadcast-enterprise",
                "started_at_kst": self.started_at,
                "inbox_dir": str(self.inbox_dir),
                "pending_inbox_files": len(list(self.inbox_dir.glob("*.json"))) + len(list(self.inbox_dir.glob("*.mp4"))),
                "processed_inbox_count": self.processed_inbox_count,
                "autocut_uploads_count": len(self.autocut_jobs),
                "total_projects_rendered": len(self.latest_payload.get("projects", [])),
                "hooks_catalog_count": self.latest_payload.get("hooks_count", 140),
            }


def make_handler(daemon: AgencyAutomationDaemon):
    output_dir = str(daemon.config.output_dir.resolve())

    class LiveStudioHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=output_dir, **kwargs)

        def do_GET(self) -> None:
            parsed = urllib.parse.urlsplit(self.path)
            if parsed.path in ("/", ""):
                self.send_response(HTTPStatus.FOUND)
                self.send_header("Location", "/studio/index.html")
                self.end_headers()
                return
            if parsed.path == "/api/status":
                self._send_json(HTTPStatus.OK, daemon.status_dict())
                return
            if parsed.path == "/api/crm":
                self._send_json(HTTPStatus.OK, MonetizationEngine(daemon.config).crm_summary())
                return
            if parsed.path == "/api/evolution":
                self._send_json(HTTPStatus.OK, AutonomousEvolutionEngine(daemon.config).summary())
                return
            if parsed.path.startswith("/api/download-bundle/"):
                client_id = parsed.path.removeprefix("/api/download-bundle/").strip("/")
                try:
                    zip_path = daemon.get_handoff_zip(client_id)
                    size = zip_path.stat().st_size
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "application/zip")
                    self.send_header("Content-Disposition", f'attachment; filename="{client_id}_deliverables.zip"')
                    self.send_header("Content-Length", str(size))
                    self.send_header("Cache-Control", "no-store")
                    self.end_headers()
                    with zip_path.open("rb") as f:
                        while chunk := f.read(65536):
                            self.wfile.write(chunk)
                except ValueError:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "Invalid client_id"})
                except FileNotFoundError:
                    self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "Bundle not found"})
                except Exception as exc:
                    self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": str(exc)})
                return
            super().do_GET()

        def do_POST(self) -> None:
            parsed = urllib.parse.urlsplit(self.path)
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "Invalid Content-Length"})
                return

            if parsed.path in ("/api/lead", "/api/crm/stage", "/api/generate-client", "/api/evolution/run", "/api/evolution/rollback"):
                if length > MAX_JSON_BYTES:
                    self._send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"ok": False, "error": "JSON payload exceeds 64KB limit"})
                    return
                try:
                    req = json.loads(self.rfile.read(length).decode("utf-8") if length > 0 else "{}")
                except Exception:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "Malformed JSON"})
                    return

                try:
                    if parsed.path == "/api/evolution/run":
                        evo = AutonomousEvolutionEngine(daemon.config)
                        res = evo.run_evolution_cycle()
                        self._send_json(HTTPStatus.OK, {**res, "summary": evo.summary()})
                        return
                    if parsed.path == "/api/evolution/rollback":
                        evo = AutonomousEvolutionEngine(daemon.config)
                        res = evo.rollback_to_generation(int(req.get("generation", 0)))
                        self._send_json(HTTPStatus.OK, {**res, "summary": evo.summary()})
                        return
                    if parsed.path == "/api/lead":
                        mon = MonetizationEngine(daemon.config)
                        lead = mon.capture_lead_and_generate_proposal(req)
                        self._send_json(HTTPStatus.OK, {"ok": True, "lead": lead, "crm": mon.crm_summary()})
                        return
                    if parsed.path == "/api/crm/stage":
                        mon = MonetizationEngine(daemon.config)
                        lead = mon.update_lead_stage(str(req.get("lead_id", "")), str(req.get("stage", "")))
                        self._send_json(HTTPStatus.OK, {"ok": True, "lead": lead, "crm": mon.crm_summary()})
                        return
                    if parsed.path == "/api/generate-client":
                        project = daemon.generate_new_client(req)
                        self._send_json(HTTPStatus.OK, {"ok": True, "project": project})
                        return
                except Exception as exc:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return

            if parsed.path == "/api/autocut-upload":
                if length <= 0:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "Empty video upload"})
                    return
                if length > MAX_VIDEO_BYTES:
                    self._send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"ok": False, "error": "Video exceeds 150MB limit"})
                    return
                qs = urllib.parse.parse_qs(parsed.query)
                filename = qs.get("filename", ["upload.mp4"])[0]
                try:
                    silence_db = int(qs.get("silence_db", ["-32"])[0])
                    min_silence = float(qs.get("min_silence", ["0.45"])[0])
                except ValueError:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "Invalid silence parameters"})
                    return

                safe_stem = _slugify(Path(filename).stem)
                ext = Path(filename).suffix.lower() or ".mp4"
                if ext not in (".mp4", ".mov", ".m4v", ".webm"):
                    ext = ".mp4"
                job_dir = daemon.uploads_dir / f"{int(time.time())}_{safe_stem}"
                job_dir.mkdir(parents=True, exist_ok=True)
                in_path = job_dir / f"{safe_stem}_original{ext}"

                try:
                    remaining = length
                    header = bytearray()
                    with in_path.open("wb") as out_f:
                        while remaining > 0:
                            chunk = self.rfile.read(min(65536, remaining))
                            if not chunk:
                                break
                            if len(header) < 16:
                                header.extend(chunk[: 16 - len(header)])
                            out_f.write(chunk)
                            remaining -= len(chunk)
                    if not _is_valid_video_magic(bytes(header)):
                        in_path.unlink(missing_ok=True)
                        self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "Invalid video magic bytes (MP4/MOV/WebM only)"})
                        return
                    result = daemon.process_real_mp4_file(in_path, job_dir, silence_db=silence_db, min_silence_sec=min_silence)
                    self._send_json(HTTPStatus.OK, {"ok": True, "result": result})
                except Exception as exc:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return

            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")

        def _send_json(self, status: HTTPStatus, payload: Dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return LiveStudioHandler


def run_live_server(host: str = "127.0.0.1", port: int = 8796) -> None:
    daemon = AgencyAutomationDaemon()
    daemon.bootstrap()
    daemon.start_watcher(interval_sec=5.0)
    server = ThreadingHTTPServer((host, port), make_handler(daemon))
    print(f"[Shortform Agency Pro v4.0] http://{host}:{port}/studio/index.html", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        daemon.stop_watcher()
        server.server_close()


if __name__ == "__main__":
    run_live_server()
