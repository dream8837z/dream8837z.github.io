"""Department 4: CS팀 (Customer Support) — Ticket Triage, Spam Filter & Human-Approval Escalation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from company_engine.config import CompanyConfig
from company_engine.master_verifier import compute_sha256


class CSDepartment:
    """Triages customer inquiries, drafts policy-grounded Korean responses, and gates high-risk tickets."""

    dept_id = "cs"
    dept_name_ko = "CS팀"

    SPAM_KEYWORDS = ("airdrop", "seed phrase", "usdt bonus", "click here now", "scam.example")
    BUG_KEYWORDS = ("잘려", "오류", "버그", "안 열", "깨져", "404", "스크롤", "고장")
    PARTNERSHIP_KEYWORDS = ("제휴", "협업", "광고", "단가", "입점", "환불", "결제")

    def __init__(self, config: CompanyConfig) -> None:
        self.config = config

    def run(self, run_date: str) -> Dict[str, Any]:
        out_dir = self.config.output_dir / "cs"
        out_dir.mkdir(parents=True, exist_ok=True)

        inbox_path = self.config.data_dir / "cs_inbox.json"
        tickets: List[Dict[str, Any]] = []
        if inbox_path.exists():
            tickets = json.loads(inbox_path.read_text(encoding="utf-8"))

        processed: List[Dict[str, Any]] = []
        category_counts: Dict[str, int] = {"bug_report": 0, "partnership_billing": 0, "content_request": 0, "spam_blocked": 0}
        escalated_to_human = 0
        forwarded_to_dev = 0

        for t in tickets:
            result = self._triage_ticket(t)
            processed.append(result)
            category_counts[result["category"]] = category_counts.get(result["category"], 0) + 1
            if result["requires_human_approval"]:
                escalated_to_human += 1
            if result["routed_dept"] == "dev":
                forwarded_to_dev += 1

        report_payload = {
            "dept_id": self.dept_id,
            "dept_name_ko": self.dept_name_ko,
            "run_date": run_date,
            "summary": {
                "total_tickets": len(processed),
                "auto_drafted": sum(1 for p in processed if p["category"] != "spam_blocked"),
                "spam_blocked": category_counts["spam_blocked"],
                "escalated_to_human": escalated_to_human,
                "forwarded_to_dev": forwarded_to_dev,
                "category_counts": category_counts,
            },
            "tickets": processed,
        }

        report_path = out_dir / f"{run_date}_cs_triage_report.json"
        report_path.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "dept_id": self.dept_id,
            "dept_name_ko": self.dept_name_ko,
            "status": "COMPLETED",
            "summary": report_payload["summary"],
            "tickets": processed,
            "report_path": str(report_path),
            "evidence": [
                {
                    "label": "CS팀 고객 문의 분류·응답 초안 리포트 JSON",
                    "type": "json",
                    "file_path": str(report_path),
                    "sha256": compute_sha256(report_path),
                }
            ],
        }

    def _triage_ticket(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        combined = f"{ticket.get('subject', '')} {ticket.get('message', '')}".lower()
        name = ticket.get("customer_name", "고객")

        if any(k in combined for k in self.SPAM_KEYWORDS):
            return {
                "ticket_id": ticket["ticket_id"],
                "customer_name": name,
                "subject": ticket["subject"],
                "category": "spam_blocked",
                "priority": "LOW",
                "routed_dept": "cs",
                "requires_human_approval": False,
                "draft_reply": "(스팸/피싱 패턴 감지 — 자동 차단 및 미응답 처리)",
            }

        if any(k in combined for k in self.PARTNERSHIP_KEYWORDS):
            return {
                "ticket_id": ticket["ticket_id"],
                "customer_name": name,
                "subject": ticket["subject"],
                "category": "partnership_billing",
                "priority": "HIGH",
                "routed_dept": "marketing",
                "requires_human_approval": True,
                "draft_reply": (
                    f"안녕하세요, {name}님. {self.config.company_name} 담당팀입니다. "
                    "제휴/협업 문의 감사드립니다. 최근 트래픽 지표 및 단가 안내서는 대표자 검토 후 영업일 1일 이내 회신드리겠습니다."
                ),
            }

        if any(k in combined for k in self.BUG_KEYWORDS):
            return {
                "ticket_id": ticket["ticket_id"],
                "customer_name": name,
                "subject": ticket["subject"],
                "category": "bug_report",
                "priority": "HIGH",
                "routed_dept": "dev",
                "requires_human_approval": False,
                "draft_reply": (
                    f"안녕하세요, {name}님. 소중한 오류 제보 감사드립니다! "
                    "개발팀에 즉시 전달하여 모바일 표 가로 스크롤(overflow-x) 패치를 우선 배정했습니다. 수정 완료 후 다시 안내드리겠습니다."
                ),
            }

        return {
            "ticket_id": ticket["ticket_id"],
            "customer_name": name,
            "subject": ticket["subject"],
            "category": "content_request",
            "priority": "MEDIUM",
            "routed_dept": "planner",
            "requires_human_approval": False,
            "draft_reply": (
                f"안녕하세요, {name}님! 유익하게 봐주셔서 감사합니다. "
                "요청하신 주제는 기획팀 콘텐츠 백로그에 등록했으며, 최신 공식 데이터 검증 후 우선 발행하도록 하겠습니다."
            ),
        }
