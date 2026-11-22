"""Unit & End-to-End Integration Tests for Shortform Agency Autopilot."""

from __future__ import annotations

import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from agency_engine.agency_economics import AgencyEconomicsAuditor
from agency_engine.config import AgencyConfig, ClientBrief
from agency_engine.hooks_library import HooksLibrary
from agency_engine.pipeline import run_agency_pipeline
from agency_engine.script_planner import ScriptPlanner


class TestHooksLibrary(unittest.TestCase):
    def test_contains_exact_140_unique_hooks_and_matches_brief(self) -> None:
        lib = HooksLibrary()
        catalog = lib.export_catalog()
        self.assertEqual(len(catalog), 140)
        self.assertEqual(len({h["hook_id"] for h in catalog}), 140)

        brief = ClientBrief(
            client_id="test_cli",
            client_name="테스트 클리닉",
            industry="치과",
            topic="임플란트 선택 기준 3가지",
            compare_a="오스템",
            compare_b="스트라우만",
            cta_action="댓글에 치과 남기기",
        )
        matched = lib.match_for_brief(brief, top_k=10)
        self.assertEqual(len(matched), 10)
        self.assertNotIn("{topic}", matched[0]["rendered_hook"])


class TestScriptPlanner(unittest.TestCase):
    def test_builds_4stage_script_and_3_personas(self) -> None:
        lib = HooksLibrary()
        planner = ScriptPlanner(lib)
        brief = AgencyConfig().client_briefs[0]
        plan = planner.plan_for_brief(brief)
        self.assertEqual(len(plan["active_scenes"]), 6)
        self.assertIn("professional", plan["personas"])
        self.assertIn("friendly", plan["personas"])
        self.assertIn("busan", plan["personas"])
        self.assertIn("1) 멈추기", plan["llm_upgrade_prompt"])


class TestAgencyEconomics(unittest.TestCase):
    def test_calculates_honest_hourly_rates_and_milestones(self) -> None:
        econ = AgencyEconomicsAuditor().evaluate()
        self.assertEqual(len(econ["tiers"]), 3)
        for tier in econ["tiers"]:
            self.assertGreater(tier["effective_hourly_rate_krw"], 50_000)
            self.assertGreaterEqual(tier["clients_for_10m_krw"], tier["clients_for_3m_krw"])


class TestEndToEndAgencyPipeline(unittest.TestCase):
    def test_renders_mp4_srt_capcut_fcpxml_and_studio_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            cfg = AgencyConfig(
                output_dir=tmp_dir / "output",
                client_briefs=[AgencyConfig().client_briefs[0]],
            )
            res = run_agency_pipeline(config=cfg, run_date="2026-11-22")

            self.assertEqual(res["hooks_count"], 140)
            self.assertEqual(len(res["projects"]), 1)

            deliv = res["projects"][0]["deliverable"]
            self.assertGreater(deliv["ng_takes_removed"], 0)
            self.assertGreater(deliv["silence_gaps_removed"], 0)
            self.assertGreater(deliv["compression_pct"], 20.0)
            self.assertTrue(Path(deliv["mp4_path"]).exists())
            self.assertGreater(Path(deliv["mp4_path"]).stat().st_size, 10_000)
            self.assertTrue(Path(deliv["srt_path"]).exists())

            # Validate CapCut JSON
            capcut = json.loads(Path(deliv["capcut_draft_path"]).read_text(encoding="utf-8"))
            self.assertEqual(capcut["canvas_config"]["width"], 1080)
            self.assertEqual(capcut["canvas_config"]["height"], 1920)

            # Validate Premiere FCPXML parses as valid XML
            tree = ET.parse(deliv["premiere_fcpxml_path"])
            self.assertEqual(tree.getroot().tag, "fcpxml")

            # Validate Executive Studio HTML
            self.assertTrue(Path(res["studio_html_path"]).exists())

    def test_inbox_watcher_and_live_client_generation(self) -> None:
        from agency_engine.live_server import AgencyAutomationDaemon

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            cfg = AgencyConfig(
                output_dir=tmp_dir / "output",
                client_briefs=[AgencyConfig().client_briefs[0]],
            )
            daemon = AgencyAutomationDaemon(config=cfg)
            daemon.bootstrap()
            (daemon.inbox_dir / "new_brief.json").write_text(
                json.dumps(
                    {
                        "client_name": "부산 해운대 정형외과",
                        "industry": "정형외과·도수치료",
                        "topic": "허리 디스크 시술 전 반드시 확인할 3가지",
                        "compare_a": "도수치료",
                        "compare_b": "신경차단술",
                        "persona_tone": "busan",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            count = daemon.poll_inbox_once()
            self.assertEqual(count, 1)
            self.assertEqual(daemon.status_dict()["processed_inbox_count"], 1)
            self.assertEqual(daemon.status_dict()["total_projects_rendered"], 2)

    def test_real_ffmpeg_silencedetect_mp4_autocut(self) -> None:
        import subprocess
        from agency_engine.video_autocutter import VideoAutoCutter

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            cfg = AgencyConfig(output_dir=tmp_dir / "output")
            cutter = VideoAutoCutter(cfg)

            # Create a real 4.5s MP4 with 1.5s tone + 1.5s silence + 1.5s tone
            raw_mp4 = tmp_dir / "raw_with_silence.mp4"
            subprocess.run(
                [
                    cutter.ffmpeg_exe,
                    "-y",
                    "-f", "lavfi", "-i", "color=c=black:s=540x960:d=4.5:r=30",
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=1.5",
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono:d=1.5",
                    "-f", "lavfi", "-i", "sine=frequency=520:duration=1.5",
                    "-filter_complex", "[1:a][2:a][3:a]concat=n=3:v=0:a=1[a]",
                    "-map", "0:v", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac",
                    str(raw_mp4),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            res = cutter.cut_uploaded_mp4(raw_mp4, tmp_dir / "output" / "cuts", silence_db=-32, min_silence_sec=0.45)
            self.assertIn("REAL_FFMPEG_SILENCEDETECT", res["mode"])
            self.assertGreaterEqual(res["silence_gaps_removed"], 1)
            self.assertLess(res["final_duration_sec"], res["raw_duration_sec"])
            self.assertTrue(Path(res["output_mp4"]).exists())
            self.assertTrue(Path(res["capcut_draft_path"]).exists())
            self.assertTrue(Path(res["premiere_fcpxml_path"]).exists())

    def test_autonomous_evolution_cycle_stays_within_safe_bounds(self) -> None:
        from agency_engine.evolution_engine import AutonomousEvolutionEngine, load_learned_policy

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            cfg = AgencyConfig(output_dir=tmp_dir / "output")
            pol_p = tmp_dir / "learned_policy.json"
            hist_p = tmp_dir / "evolution_history.json"

            eng = AutonomousEvolutionEngine(config=cfg, policy_path=pol_p, history_path=hist_p)
            r1 = eng.run_evolution_cycle(run_date="2026-11-23")
            r2 = eng.run_evolution_cycle(run_date="2026-11-26")

            self.assertEqual(r1["generation"], 1)
            self.assertEqual(r2["generation"], 2)
            pol = load_learned_policy(pol_p)
            self.assertTrue(8 <= pol["tts_rate_pct"] <= 22)
            self.assertTrue(3 <= pol["caption_max_words"] <= 6)
            for w in pol["hook_category_weights"].values():
                self.assertTrue(0.80 <= w <= 1.35)
            self.assertTrue(Path(r2["report_path"]).exists())


if __name__ == "__main__":
    unittest.main()
