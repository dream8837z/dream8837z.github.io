"""Step 7 Master Evidence-First Verification Gate — Zero-Tolerance Anti-Hallucination Engine."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image, ImageStat

KST = timezone(timedelta(hours=9))


def compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MasterVerifier:
    """
    Implements the video's 2-line anti-hallucination rule in deterministic code:
      Rule 1: Open every claimed artifact directly and verify cryptographic/structural evidence.
      Rule 2: If anything cannot be verified, explicitly report UNVERIFIED_REJECTED (never pass).
    """

    ANTI_HALLUCINATION_RULES = [
        "다 됐다고 보고하기 전에 결과물을 직접 열어서 확인하고 증거(파일 경로·SHA-256·실측 수치)를 보여 줄 것.",
        "확인 못 한 건 못했다고 그대로 말할 것. 증거 없는 완료 보고는 코드 레벨에서 즉시 REJECT 처리한다.",
    ]

    def verify_department_reports(self, department_reports: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        verified_departments: Dict[str, Any] = {}
        total_evidence = 0
        passed_evidence = 0
        rejected_items: List[Dict[str, Any]] = []

        for dept_id, report in department_reports.items():
            evidence_list = report.get("evidence", [])
            dept_checks: List[Dict[str, Any]] = []
            dept_passed = True

            if not evidence_list:
                dept_passed = False
                rejected_items.append(
                    {
                        "dept_id": dept_id,
                        "reason": "NO_EVIDENCE_SUBMITTED — 증거 없이 완료 보고함 (거짓 보고 차단)",
                    }
                )

            for item in evidence_list:
                total_evidence += 1
                check = self._verify_single_artifact(dept_id, item)
                dept_checks.append(check)
                if check["status"] == "VERIFIED":
                    passed_evidence += 1
                else:
                    dept_passed = False
                    rejected_items.append(check)

            verified_departments[dept_id] = {
                "dept_name_ko": report.get("dept_name_ko", dept_id),
                "claimed_status": report.get("status", "UNKNOWN"),
                "master_verdict": "APPROVED" if dept_passed else "UNVERIFIED_REJECTED",
                "evidence_count": len(evidence_list),
                "verified_count": sum(1 for c in dept_checks if c["status"] == "VERIFIED"),
                "checks": dept_checks,
            }

        pass_rate = round((passed_evidence / total_evidence) * 100.0, 1) if total_evidence > 0 else 0.0
        overall_approved = (total_evidence > 0) and (len(rejected_items) == 0)

        return {
            "verified_at_kst": datetime.now(KST).isoformat(timespec="seconds"),
            "rules_enforced": self.ANTI_HALLUCINATION_RULES,
            "overall_verdict": "ALL_VERIFIED_PASS" if overall_approved else "REJECTED_UNVERIFIED_CLAIMS",
            "total_evidence_items": total_evidence,
            "verified_evidence_items": passed_evidence,
            "verification_pass_rate_pct": pass_rate,
            "rejected_count": len(rejected_items),
            "rejected_items": rejected_items,
            "departments": verified_departments,
        }

    def _verify_single_artifact(self, dept_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
        raw_path = item.get("file_path", "")
        claimed_sha = item.get("sha256", "")
        artifact_type = item.get("type", "file")
        path = Path(raw_path)

        if not raw_path or not path.exists() or not path.is_file():
            return {
                "dept_id": dept_id,
                "file_path": raw_path,
                "status": "UNVERIFIED_REJECTED",
                "reason": "파일이 디스크에 존재하지 않음 (확인 불가)",
            }

        byte_size = path.stat().st_size
        if byte_size <= 0:
            return {
                "dept_id": dept_id,
                "file_path": str(path),
                "status": "UNVERIFIED_REJECTED",
                "reason": "파일 크기가 0바이트임 (빈 산출물 차단)",
            }

        actual_sha = compute_sha256(path)
        if claimed_sha and actual_sha != claimed_sha:
            return {
                "dept_id": dept_id,
                "file_path": str(path),
                "status": "UNVERIFIED_REJECTED",
                "reason": f"SHA-256 불일치 (보고={claimed_sha[:12]} vs 실측={actual_sha[:12]})",
            }

        extra_proof: Dict[str, Any] = {"byte_size": byte_size, "sha256_prefix": actual_sha[:16]}

        if artifact_type == "json" or path.suffix.lower() == ".json":
            try:
                parsed = json.loads(path.read_text(encoding="utf-8"))
                extra_proof["json_keys"] = len(parsed) if isinstance(parsed, (dict, list)) else 1
            except Exception as exc:
                return {
                    "dept_id": dept_id,
                    "file_path": str(path),
                    "status": "UNVERIFIED_REJECTED",
                    "reason": f"JSON 파싱 실패: {exc}",
                }

        if artifact_type == "png" or path.suffix.lower() == ".png":
            try:
                with Image.open(path) as img:
                    w, h = img.size
                    stat = ImageStat.Stat(img.convert("RGB"))
                    stddev_avg = round(sum(stat.stddev) / 3.0, 2)
                expected_size = item.get("expected_size")
                if expected_size and [w, h] != list(expected_size):
                    return {
                        "dept_id": dept_id,
                        "file_path": str(path),
                        "status": "UNVERIFIED_REJECTED",
                        "reason": f"PNG 해상도 불일치 (기대={expected_size} vs 실측={[w, h]})",
                    }
                if stddev_avg < 5.0:
                    return {
                        "dept_id": dept_id,
                        "file_path": str(path),
                        "status": "UNVERIFIED_REJECTED",
                        "reason": f"단색/빈 이미지 감지 (stddev={stddev_avg})",
                    }
                extra_proof["dimensions"] = f"{w}x{h}"
                extra_proof["pixel_stddev"] = stddev_avg
            except Exception as exc:
                return {
                    "dept_id": dept_id,
                    "file_path": str(path),
                    "status": "UNVERIFIED_REJECTED",
                    "reason": f"PNG 이미지 열기 실패: {exc}",
                }

        return {
            "dept_id": dept_id,
            "file_path": str(path),
            "label": item.get("label", path.name),
            "status": "VERIFIED",
            "proof": extra_proof,
        }
