"""Comprehensive Unit & End-to-End Integration Tests for AI Company Autopilot."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from company_engine.config import BASE_DIR, CompanyConfig
from company_engine.economics_auditor import EconomicsAuditor
from company_engine.master_verifier import MasterVerifier, compute_sha256
from company_engine.pipeline import run_daily_autopilot
from company_engine.security_guard import SecurityGuard


class TestSecurityGuard(unittest.TestCase):
    def setUp(self) -> None:
        self.guard = SecurityGuard(BASE_DIR)

    def test_blocks_cross_department_and_env_writes(self) -> None:
        self.assertTrue(self.guard.check_write_permission("design", BASE_DIR / "output/design/slide.png")["allowed"])
        self.assertFalse(self.guard.check_write_permission("design", BASE_DIR / "output/dev/patch.md")["allowed"])
        self.assertFalse(self.guard.check_write_permission("dev", BASE_DIR / ".env")["allowed"])
        self.assertFalse(self.guard.check_write_permission("planner", Path("/etc/passwd"))["allowed"])

    def test_blocks_dangerous_shell_commands(self) -> None:
        self.assertFalse(self.guard.inspect_command("rm -rf /")["safe"])
        self.assertFalse(self.guard.inspect_command("git push origin main --force")["safe"])
        self.assertFalse(self.guard.inspect_command("cat .env")["safe"])
        self.assertTrue(self.guard.inspect_command("python -m company_engine run")["safe"])

    def test_detects_leaked_secrets(self) -> None:
        hits = self.guard.scan_text_for_secrets("token=ghp_1234567890abcdef1234567890abcdef12")
        self.assertGreaterEqual(len(hits), 1)


class TestMasterVerifierAntiHallucination(unittest.TestCase):
    def test_rejects_missing_evidence_and_tampered_hash_and_blank_png(self) -> None:
        verifier = MasterVerifier()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            real_file = tmp_dir / "report.json"
            real_file.write_text('{"ok": true}', encoding="utf-8")

            blank_png = tmp_dir / "blank.png"
            Image.new("RGB", (1080, 1350), (0, 0, 0)).save(blank_png)

            fake_reports = {
                "lying_no_evidence": {"dept_name_ko": "거짓부서1", "status": "COMPLETED", "evidence": []},
                "lying_missing_file": {
                    "dept_name_ko": "거짓부서2",
                    "status": "COMPLETED",
                    "evidence": [{"file_path": str(tmp_dir / "ghost.json"), "type": "json", "sha256": "deadbeef"}],
                },
                "lying_bad_hash": {
                    "dept_name_ko": "거짓부서3",
                    "status": "COMPLETED",
                    "evidence": [{"file_path": str(real_file), "type": "json", "sha256": "0" * 64}],
                },
                "lying_blank_png": {
                    "dept_name_ko": "거짓부서4",
                    "status": "COMPLETED",
                    "evidence": [
                        {
                            "file_path": str(blank_png),
                            "type": "png",
                            "sha256": compute_sha256(blank_png),
                            "expected_size": [1080, 1350],
                        }
                    ],
                },
            }

            result = verifier.verify_department_reports(fake_reports)
            self.assertEqual(result["overall_verdict"], "REJECTED_UNVERIFIED_CLAIMS")
            self.assertEqual(result["verified_evidence_items"], 0)
            for dept_id in fake_reports:
                self.assertEqual(result["departments"][dept_id]["master_verdict"], "UNVERIFIED_REJECTED")


class TestEconomicsAuditor(unittest.TestCase):
    def test_tier0_is_recommended_and_saves_money(self) -> None:
        econ = EconomicsAuditor().evaluate_tiers(15.0)
        self.assertEqual(econ["recommended_tier"], "tier0_hybrid_autopilot")
        self.assertIn("tier0_hybrid_autopilot", econ["budget_compliant_tiers"])
        self.assertGreater(econ["savings_vs_full_agent_teams_usd_per_month"], 100.0)


class TestEndToEndPipeline(unittest.TestCase):
    def test_full_pipeline_runs_and_passes_master_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            fake_site = tmp_root / "sample-site"
            fake_site.mkdir()
            (fake_site / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
            (fake_site / "sitemap.xml").write_text("<urlset><url><loc>https://example.com/</loc></url></urlset>", encoding="utf-8")
            (fake_site / "index.html").write_text(
                "<!doctype html><html><head><title>Sample</title></head><body><h1>Hello</h1><a href='missing.html'>Broken</a></body></html>",
                encoding="utf-8",
            )

            cfg = CompanyConfig(
                company_name="Test AI Corp",
                site_domain="https://example.com",
                target_site_dirs=[fake_site],
                output_dir=tmp_root / "output",
            )
            res = run_daily_autopilot(config=cfg, run_date="2026-11-22", write_repo_workflow=False)

            mv = res["master_verification"]
            self.assertEqual(mv["overall_verdict"], "ALL_VERIFIED_PASS")
            self.assertEqual(mv["verification_pass_rate_pct"], 100.0)
            self.assertEqual(res["departments"]["design"]["summary"]["slides_rendered"], 5)
            self.assertGreaterEqual(res["departments"]["dev"]["summary"]["broken_internal_links_found"], 1)
            self.assertTrue(Path(res["studio_html_path"]).exists())
            self.assertTrue((cfg.output_dir / "claude_starter_pack" / "CLAUDE.md").exists())


if __name__ == "__main__":
    unittest.main()
