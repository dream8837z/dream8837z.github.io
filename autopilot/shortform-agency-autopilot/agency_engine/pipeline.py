"""Main End-to-End Orchestration Pipeline for Shortform Agency Autopilot."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from agency_engine.agency_economics import AgencyEconomicsAuditor
from agency_engine.client_acquisition import ClientAcquisitionKit
from agency_engine.config import AgencyConfig
from agency_engine.hooks_library import HooksLibrary
from agency_engine.monetization_engine import MonetizationEngine
from agency_engine.script_planner import ScriptPlanner
from agency_engine.studio_builder import AgencyStudioBuilder
from agency_engine.video_autocutter import VideoAutoCutter

KST = timezone(timedelta(hours=9))


def run_agency_pipeline(
    config: AgencyConfig | None = None,
    run_date: str | None = None,
) -> Dict[str, Any]:
    cfg = config or AgencyConfig()
    date_str = run_date or datetime.now(KST).strftime("%Y-%m-%d")
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Export 140+ Verified Korean 3-Second Hook Dictionary
    hooks_lib = HooksLibrary()
    hooks_catalog = hooks_lib.export_catalog()
    hooks_path = cfg.output_dir / "hooks_140_catalog.json"
    hooks_path.write_text(json.dumps(hooks_catalog, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2. Plan 4-Stage Scripts + Render Auto-Cut 1080x1920 MP4 + SRT + CapCut + Premiere FCPXML
    planner = ScriptPlanner(hooks_lib)
    cutter = VideoAutoCutter(cfg)

    projects: List[Dict[str, Any]] = []
    for brief in cfg.client_briefs:
        script_plan = planner.plan_for_brief(brief)
        deliverable = cutter.process_client_project(script_plan, date_str)
        projects.append({"script": script_plan, "deliverable": deliverable})

    avg_comp = round(
        sum(p["deliverable"]["compression_pct"] for p in projects) / len(projects), 1
    ) if projects else 0.0

    # 3. Generate 3-Channel Client Acquisition Kit & B2B Contract Guardrails
    acq_kit = ClientAcquisitionKit(cfg).generate(cfg.output_dir / "acquisition")

    # 4. Compute Realistic Unit Economics & Hourly Rate Matrix
    economics = AgencyEconomicsAuditor().evaluate()

    # 5. End-to-End Monetization Funnel + Client Handoff ZIPs + YouTube Shorts Publish Queue + CRM Summary
    monetization = MonetizationEngine(cfg)
    for proj in projects:
        hz = monetization.build_client_handoff_bundle(proj, date_str)
        proj["deliverable"]["handoff_zip_path"] = str(hz)
    public_funnel = monetization.build_public_b2b_funnel(projects, date_str, sync_gh_pages=(config is None))
    youtube_queue = monetization.build_youtube_publish_queue(projects, date_str)
    crm = monetization.crm_summary()

    payload: Dict[str, Any] = {
        "run_date": date_str,
        "agency_name": cfg.agency_name,
        "hooks_count": len(hooks_catalog),
        "hooks_catalog_path": str(hooks_path),
        "hooks_catalog_140": hooks_catalog,
        "avg_compression_pct": avg_comp,
        "projects": projects,
        "acquisition_kit": acq_kit,
        "economics": economics,
        "monetization": {
            "public_funnel": public_funnel,
            "youtube_queue": youtube_queue,
            "crm": crm,
        },
    }

    manifest_path = cfg.output_dir / f"{date_str}_agency_manifest.json"
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # 5. Build Executive Agency Studio Web Dashboard
    studio_html = AgencyStudioBuilder().build(payload, cfg.output_dir / "studio" / "index.html")
    payload["manifest_path"] = str(manifest_path)
    payload["studio_html_path"] = str(studio_html)
    return payload


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Shortform Agency Autopilot — B2B Reels/Shorts Automation Factory")
    sub = parser.add_subparsers(dest="command")
    run_p = sub.add_parser("run", help="Run full B2B short-form agency pipeline")
    run_p.add_argument("--date", dest="run_date", default=None, help="Override run date (YYYY-MM-DD)")

    srv_p = sub.add_parser("serve", help="Start live automation server + inbox folder watcher")
    srv_p.add_argument("--host", default="127.0.0.1")
    srv_p.add_argument("--port", type=int, default=8796)

    sub.add_parser("evolve", help="Run periodic 3-Expert Autonomous Self-Learning & Upgrade cycle")

    args = parser.parse_args(argv)
    if args.command == "serve":
        from agency_engine.live_server import run_live_server

        run_live_server(host=args.host, port=args.port)
        return 0
    if args.command == "evolve":
        from agency_engine.evolution_engine import AutonomousEvolutionEngine

        res = AutonomousEvolutionEngine().run_evolution_cycle()
        print(f"[Autonomous Evolution] Generation #{res['generation']} (policy v{res['policy_version']})")
        print(f"  Changes : {json.dumps(res['changes'], ensure_ascii=False)}")
        print(f"  Report  : {res['report_path']}")
        return 0

    result = run_agency_pipeline(run_date=getattr(args, "run_date", None))
    print(f"[Shortform Agency Autopilot] Date: {result['run_date']}")
    print(f"  3-Sec Hook Library : {result['hooks_count']} verified Korean templates")
    print(f"  B2B MP4 Rendered   : {len(result['projects'])} client reels (avg -{result['avg_compression_pct']}% NG/silence cut)")
    print(f"  Exports Generated  : MP4 + .srt + CapCut JSON + Premiere .fcpxml per client")
    print(f"  Agency Studio HTML : {result['studio_html_path']}")
    return 0
