"""Main Autonomous Orchestration Pipeline for AI Company Autopilot."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from company_engine.config import BASE_DIR, CompanyConfig
from company_engine.departments.cs_dept import CSDepartment
from company_engine.departments.design_dept import DesignDepartment
from company_engine.departments.dev_dept import DevDepartment
from company_engine.departments.marketing_dept import MarketingDepartment
from company_engine.departments.planner_dept import PlannerDepartment
from company_engine.economics_auditor import EconomicsAuditor
from company_engine.master_verifier import MasterVerifier
from company_engine.security_guard import SecurityGuard
from company_engine.studio_builder import StudioBuilder
from company_engine.workspace_bootstrapper import WorkspaceBootstrapper

KST = timezone(timedelta(hours=9))


def run_daily_autopilot(
    config: CompanyConfig | None = None,
    run_date: str | None = None,
    write_repo_workflow: bool = True,
) -> Dict[str, Any]:
    cfg = config or CompanyConfig()
    date_str = run_date or datetime.now(KST).strftime("%Y-%m-%d")

    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Step 4 Security Guard — Export Least-Privilege RBAC Policy
    guard = SecurityGuard(BASE_DIR)
    policy_path = guard.export_policy(cfg.output_dir / "security" / "permissions_policy.json")

    # 2. Steps 1, 2, 3, 5, 6, 7 — Generate Claude Code 8-Step Starter Pack + Cloud Cron
    bootstrapper = WorkspaceBootstrapper(cfg)
    workflow_target = (BASE_DIR / ".github" / "workflows" / "daily_ai_company.yml") if write_repo_workflow else None
    starter_pack = bootstrapper.generate_all(cfg.output_dir / "claude_starter_pack", workflow_path=workflow_target)

    # 3. Token Unit Economics & BEP Audit
    economics = EconomicsAuditor().evaluate_tiers(cfg.monthly_token_budget_usd)

    # 4. Run 5 Autonomous AI Departments
    planner_res = PlannerDepartment(cfg).run(date_str)
    dev_res = DevDepartment(cfg).run(date_str, planner_res)
    design_res = DesignDepartment(cfg).run(date_str, planner_res["daily_card_news_brief"])
    cs_res = CSDepartment(cfg).run(date_str)
    marketing_res = MarketingDepartment(cfg).run(date_str, planner_res, design_res)

    dept_reports = {
        "planner": planner_res,
        "dev": dev_res,
        "design": design_res,
        "cs": cs_res,
        "marketing": marketing_res,
    }

    # 5. Step 7 Master Evidence-First Verification Gate (Zero-Tolerance Anti-Hallucination)
    verifier = MasterVerifier()
    master_verification = verifier.verify_department_reports(dept_reports)

    master_dir = cfg.output_dir / "master"
    master_dir.mkdir(parents=True, exist_ok=True)
    master_report_path = master_dir / f"{date_str}_master_audit_report.json"

    full_payload: Dict[str, Any] = {
        "run_date": date_str,
        "company_name": cfg.company_name,
        "site_domain": cfg.site_domain,
        "security_policy_path": str(policy_path),
        "economics": economics,
        "starter_pack": starter_pack,
        "departments": dept_reports,
        "master_verification": master_verification,
    }
    master_report_path.write_text(json.dumps(full_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # 6. Build Executive HQ Web Dashboard
    studio_html_path = StudioBuilder().build(full_payload, cfg.output_dir / "studio" / "index.html")
    full_payload["master_report_path"] = str(master_report_path)
    full_payload["studio_html_path"] = str(studio_html_path)
    return full_payload


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Company Autopilot — 5 AI Employees + Master Verifier")
    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="Run full daily autonomous pipeline across all 5 departments + Master Gate")
    run_p.add_argument("--date", dest="run_date", default=None, help="Override run date (YYYY-MM-DD)")

    sub.add_parser("verify", help="Re-verify the latest master report artifacts on disk")

    args = parser.parse_args(argv)
    cmd = args.command or "run"

    if cmd == "run":
        result = run_daily_autopilot(run_date=getattr(args, "run_date", None))
        mv = result["master_verification"]
        print(f"[AI Company Autopilot] Date: {result['run_date']}")
        print(f"  Master Verdict : {mv['overall_verdict']} ({mv['verified_evidence_items']}/{mv['total_evidence_items']} verified, {mv['verification_pass_rate_pct']}%)")
        print(f"  Sites Scanned  : {result['departments']['planner']['summary']['sites_audited']} sites / {result['departments']['planner']['summary']['total_html_pages_scanned']} HTML pages")
        print(f"  SNS Card News  : {result['departments']['design']['summary']['slides_rendered']} slides (1080x1350 PNG)")
        print(f"  CS Tickets     : {result['departments']['cs']['summary']['total_tickets']} triaged ({result['departments']['cs']['summary']['spam_blocked']} spam blocked)")
        print(f"  HQ Dashboard   : {result['studio_html_path']}")
        return 0 if mv["overall_verdict"] == "ALL_VERIFIED_PASS" else 2

    if cmd == "verify":
        cfg = CompanyConfig()
        master_files = sorted((cfg.output_dir / "master").glob("*_master_audit_report.json"))
        if not master_files:
            print("No master audit report found. Run `python -m company_engine run` first.")
            return 1
        latest = json.loads(master_files[-1].read_text(encoding="utf-8"))
        mv = MasterVerifier().verify_department_reports(latest["departments"])
        print(f"[Re-Verify] {master_files[-1].name} -> {mv['overall_verdict']} ({mv['verified_evidence_items']}/{mv['total_evidence_items']})")
        return 0 if mv["overall_verdict"] == "ALL_VERIFIED_PASS" else 2

    return 0
