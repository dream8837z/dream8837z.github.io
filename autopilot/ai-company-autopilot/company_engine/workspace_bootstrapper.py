"""Generates the complete 8-step Claude Code Agent Teams Starter Pack & GitHub Actions Cron."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from company_engine.config import CompanyConfig, DEPARTMENT_SPECS


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class WorkspaceBootstrapper:
    """Produces ready-to-paste Claude Code 8-step configs and 24/365 GitHub Actions workflow."""

    def __init__(self, config: CompanyConfig) -> None:
        self.config = config

    def generate_all(self, pack_dir: Path, workflow_path: Path | None = None) -> Dict[str, Any]:
        pack_dir.mkdir(parents=True, exist_ok=True)
        agents_dir = pack_dir / ".claude" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        created_files: List[Dict[str, Any]] = []

        # Step 1: Job Posting
        job_md = pack_dir / "job_posting.md"
        job_md.write_text(self._render_job_posting(), encoding="utf-8")
        created_files.append(self._record(job_md, "① 채용 공고 (3줄 핵심 + KPI/예산 SLA)"))

        # Step 3: CLAUDE.md Company Manual
        claude_md = pack_dir / "CLAUDE.md"
        claude_md.write_text(self._render_claude_md(), encoding="utf-8")
        created_files.append(self._record(claude_md, "③ 회사 업무 매뉴얼 (CLAUDE.md)"))

        # Step 5: ~/.claude/settings.json snippet
        settings_snippet = pack_dir / "settings.json.snippet"
        settings_payload = {
            "env": {
                "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
            }
        }
        settings_snippet.write_text(json.dumps(settings_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        created_files.append(self._record(settings_snippet, "⑤ 에이전트 팀 활성화 settings.json"))

        # Step 6: 6 Department Agent Definitions (.claude/agents/*.md)
        for dept_id, spec in DEPARTMENT_SPECS.items():
            agent_file = agents_dir / f"{dept_id}.md"
            agent_file.write_text(self._render_agent_md(dept_id), encoding="utf-8")
            created_files.append(self._record(agent_file, f"⑥ 부서 에이전트 정의 ({spec.name_ko})"))

        # Step 7: /schedule Command + Anti-Hallucination Prompt
        schedule_txt = pack_dir / "schedule_command.txt"
        schedule_txt.write_text(self._render_schedule_command(), encoding="utf-8")
        created_files.append(self._record(schedule_txt, "⑦ 매일 09:00 /schedule + 거짓말 방지 2줄 검수 규칙"))

        # Step 2/7 Cloud Upgrade: GitHub Actions Workflow (KST 09:00 = UTC 00:00)
        wf_content = self._render_github_actions_workflow()
        pack_wf = pack_dir / "daily_ai_company.yml"
        pack_wf.write_text(wf_content, encoding="utf-8")
        created_files.append(self._record(pack_wf, "②·⑦ PC 전원 OFF 대응 GitHub Actions 클라우드 스케줄러"))

        if workflow_path is not None:
            workflow_path.parent.mkdir(parents=True, exist_ok=True)
            workflow_path.write_text(wf_content, encoding="utf-8")

        return {
            "pack_dir": str(pack_dir),
            "file_count": len(created_files),
            "files": created_files,
            "snippets": {
                "job_posting": job_md.read_text(encoding="utf-8"),
                "claude_md": claude_md.read_text(encoding="utf-8"),
                "settings_json": settings_snippet.read_text(encoding="utf-8"),
                "schedule_command": schedule_txt.read_text(encoding="utf-8"),
            },
        }

    def _record(self, path: Path, label: str) -> Dict[str, Any]:
        return {
            "label": label,
            "file_path": str(path),
            "byte_size": path.stat().st_size,
            "sha256": _sha256(path),
        }

    def _render_job_posting(self) -> str:
        sites_str = ", ".join(str(p) for p in self.config.target_site_dirs)
        return f"""# ① AI 직원 채용 공고 ({self.config.company_name})

## 핵심 3줄 정의 (영상 1단계 표준)
- **목표**: 수익형 웹 사이트({self.config.site_domain}) 무인 운영 및 검색 노출·전환 수익 극대화
- **매일 업무**: 사이트 헬스체크·고장 수리, Google Search Console/SEO 색인 점검 및 개선 패치, 고객 CS 분류·초안, SNS 카드뉴스 5장 생성 및 홍보 패키지 발행
- **결과물**: 검색 상위 노출이 검증된 무장애 사이트 + 매일 발행되는 1080×1350 카드뉴스 + 증거 해시(SHA-256)가 첨부된 일일 감사 리포트

## 확장 운영 SLA & 가드레일
- **관리 대상 사이트 경로**: `{sites_str}`
- **매일 실행 시각**: KST {self.config.schedule_kst_hour:02d}:{self.config.schedule_kst_minute:02d} (로컬 `/schedule` + GitHub Actions 이중화)
- **월간 LLM 토큰 예산 상한**: `${self.config.monthly_token_budget_usd:.2f}` (초과 시 자동 Tier-0 Python 무인 엔진 폴백)
- **절대 금지**: 시크릿(`.env`) 열람/커밋, `rm -rf`·`git push --force`, 증거 없는 완료 보고, 인간 승인 없는 환불/법무 답변 발송
"""

    def _render_claude_md(self) -> str:
        rows = []
        for dept_id, spec in DEPARTMENT_SPECS.items():
            writes = ", ".join(spec.allowed_write_dirs)
            rows.append(f"| `{dept_id}` ({spec.name_ko}) | {spec.model_tier} | `{writes}` | {spec.daily_mission} |")
        dept_table = "\n".join(rows)

        return f"""# {self.config.company_name} — 회사 업무 매뉴얼 (CLAUDE.md)

> 본 매뉴얼은 모든 AI 직원(기획·개발·디자인·CS·마케팅)과 총괄 마스터가 반드시 준수해야 하는 최상위 운영 헌법입니다.

## 1. 회사 목표 및 수익화 원칙
- 대상 도메인: `{self.config.site_domain}`
- 모든 작업은 **검색 노출(GSC/SEO) → 트래픽 유입(SNS 카드뉴스) → 전환 수익(AdSense/CPA/제휴)** 파이프라인에 기여해야 합니다.
- 단순 반복 점검(HTML/링크/메타 감사, 카드뉴스 PNG 렌더링, CS 분류)은 토큰 비용 `$0`인 `company_engine`을 우선 사용합니다.

## 2. 부서별 조직도 및 파일 소유권 매트릭스
| 부서 | 권장 모델 | 쓰기 허용 경로 | 일일 핵심 미션 |
|---|---|---|---|
{dept_table}

## 3. 거짓말 방지 2줄 검증 규칙 (영상 7단계 필수 — 절대 예외 없음)
1. **다 됐다고 보고하기 전에 결과물을 직접 열어서 확인하고 증거(파일 경로, SHA-256, 테스트/해상도 로그)를 보여 줄 것.**
2. **확인 못 한 건 못했다고 그대로 말할 것. 추정·환각 완료 보고 시 마스터가 즉시 `UNVERIFIED_REJECTED` 처리한다.**

## 4. 보안 및 최소 권한 원칙 (영상 4단계 보완)
- 무제한 '항상 허용(Always Allow)' 금지 — 각 부서는 위 소유권 매트릭스의 `쓰기 허용 경로` 밖의 파일을 수정할 수 없습니다.
- `.env`, API 키, SSH 키, 개인정보가 포함된 파일은 읽기·출력·커밋을 원천 금지합니다.
- 라이브 사이트 코드 수정은 반드시 `output/dev/`에 Diff 패치를 생성하고 테스트 통과 후 반영합니다.
"""

    def _render_agent_md(self, dept_id: str) -> str:
        spec = DEPARTMENT_SPECS[dept_id]
        extra_rule = ""
        if dept_id == "master":
            extra_rule = """
## 총괄 마스터 전용 검수 규칙 (거짓말 방지 2줄)
- 다 됐다고 보고하기 전에 모든 부서의 결과물을 직접 열어서 확인하고 증거(파일 경로·SHA-256·실측 수치)를 보여 줄 것.
- 확인 못 한 건 못했다고 그대로 말할 것. 증거가 누락된 부서 보고는 절대 승인하지 말고 재작업 지시할 것.
"""
        return f"""---
name: {dept_id}
description: {spec.name_ko} ({spec.role_title}) — {spec.daily_mission}
model: {spec.model_tier}
---

# {spec.name_ko} ({spec.role_title})

- **소속**: `{self.config.company_name}` (프로젝트 전용 직원)
- **일일 미션**: {spec.daily_mission}
- **읽기 허용 범위**: `{", ".join(spec.allowed_read_globs)}`
- **쓰기 허용 경로**: `{", ".join(spec.allowed_write_dirs)}`
- **금지 행동**: `{", ".join(spec.forbidden_actions)}`
- **필수 완료 증거**: {spec.evidence_requirement}
{extra_rule}"""

    def _render_schedule_command(self) -> str:
        return f"""# ⑦ Claude Code /schedule 자동화 명령 (그대로 복사해 입력)

/schedule 매일 아침 {self.config.schedule_kst_hour}시 {self.config.schedule_kst_minute:02d}분에 마스터가 기획팀, 개발팀, 디자인팀, CS팀, 마케팅팀에게 오늘 할 일을 지시하도록 스케줄 걸어줘.
단, 마스터는 아래 검수 규칙 2줄을 반드시 지켜야 해:
1) 다 됐다고 보고하기 전에 결과물을 직접 열어서 확인하고 증거(파일 경로, SHA-256, 테스트/해상도 결과)를 보여 줄 것.
2) 확인 못 한 건 못했다고 그대로 말할 것.

# 권장: PC가 꺼져 있어도 100% 실행되는 완전 무인 실행 커맨드
.venv/bin/python -m company_engine run
"""

    def _render_github_actions_workflow(self) -> str:
        utc_hour = (self.config.schedule_kst_hour - 9) % 24
        return f"""name: Daily AI Company Autopilot (KST {self.config.schedule_kst_hour:02d}:{self.config.schedule_kst_minute:02d})

on:
  schedule:
    # 매일 KST {self.config.schedule_kst_hour:02d}:{self.config.schedule_kst_minute:02d} (UTC {utc_hour:02d}:{self.config.schedule_kst_minute:02d}) 무인 실행
    - cron: "{self.config.schedule_kst_minute} {utc_hour} * * *"
  workflow_dispatch:

jobs:
  run-ai-employees:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install pillow

      - name: Run 5 AI Departments + Master Evidence Verification Gate
        run: python -m company_engine run

      - name: Run Automated Test Suite
        run: python -m unittest discover -s tests -t . -v

      - name: Upload Daily HQ Report & SNS Card News Artifact
        uses: actions/upload-artifact@v4
        with:
          name: ai-company-daily-output
          path: output/
"""
