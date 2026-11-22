"""Department 2: 개발팀 (Dev) — Site Healthcheck, Broken Link Audit & Safe SEO Patch Builder."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from company_engine.config import CompanyConfig
from company_engine.master_verifier import compute_sha256

HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)


class DevDepartment:
    """Audits site reliability, broken internal links, and generates safe reviewable SEO patches."""

    dept_id = "dev"
    dept_name_ko = "개발팀"

    def __init__(self, config: CompanyConfig) -> None:
        self.config = config

    def run(self, run_date: str, planner_result: Dict[str, Any]) -> Dict[str, Any]:
        out_dir = self.config.output_dir / "dev"
        out_dir.mkdir(parents=True, exist_ok=True)

        broken_links: List[Dict[str, str]] = []
        pages_checked = 0

        for site_dir in self.config.target_site_dirs:
            if not site_dir.exists():
                continue
            for html_file in sorted(site_dir.rglob("*.html"))[:60]:
                pages_checked += 1
                raw = html_file.read_text(encoding="utf-8", errors="ignore")
                for href in HREF_RE.findall(raw):
                    if href.startswith(("http://", "https://", "mailto:", "tel:", "#", "javascript:", "data:")):
                        continue
                    clean_href = href.split("#")[0].split("?")[0].strip()
                    if not clean_href:
                        continue
                    target = (
                        site_dir / clean_href.lstrip("/")
                        if clean_href.startswith("/")
                        else html_file.parent / clean_href
                    )
                    if not target.exists() and not (target / "index.html").exists():
                        if len(broken_links) < 30:
                            broken_links.append(
                                {
                                    "site": site_dir.name,
                                    "source_page": html_file.relative_to(site_dir).as_posix(),
                                    "broken_href": href,
                                }
                            )

        # Build safe, reviewable SEO patch proposals from planner's real detected gaps
        patch_proposals: List[Dict[str, Any]] = []
        for audit in planner_result.get("site_audits", []):
            for gap in audit.get("seo_gaps", [])[:10]:
                patch_proposals.append(self._build_patch_snippet(audit["site_name"], gap))

        patch_md_path = out_dir / f"{run_date}_seo_patch_proposals.md"
        patch_md_path.write_text(self._render_patch_markdown(run_date, patch_proposals, broken_links), encoding="utf-8")

        health_payload = {
            "dept_id": self.dept_id,
            "dept_name_ko": self.dept_name_ko,
            "run_date": run_date,
            "summary": {
                "pages_healthchecked": pages_checked,
                "broken_internal_links_found": len(broken_links),
                "safe_seo_patches_generated": len(patch_proposals),
                "auto_applied_to_prod": False,
                "safety_policy": "라이브 사이트 무단 덮어쓰기 금지 — 리뷰 가능한 패치 번들 생성 후 승인 반영",
            },
            "broken_links": broken_links,
            "patch_proposals": patch_proposals,
        }

        health_path = out_dir / f"{run_date}_site_health_report.json"
        health_path.write_text(json.dumps(health_payload, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "dept_id": self.dept_id,
            "dept_name_ko": self.dept_name_ko,
            "status": "COMPLETED",
            "summary": health_payload["summary"],
            "broken_links": broken_links,
            "patch_proposals": patch_proposals,
            "report_path": str(health_path),
            "patch_md_path": str(patch_md_path),
            "evidence": [
                {
                    "label": "개발팀 사이트 헬스체크 리포트 JSON",
                    "type": "json",
                    "file_path": str(health_path),
                    "sha256": compute_sha256(health_path),
                },
                {
                    "label": "개발팀 SEO 안전 패치 제안서 MD",
                    "type": "file",
                    "file_path": str(patch_md_path),
                    "sha256": compute_sha256(patch_md_path),
                },
            ],
        }

    def _build_patch_snippet(self, site_name: str, gap: Dict[str, Any]) -> Dict[str, Any]:
        issues = gap.get("issues", [])
        snippets: List[str] = []
        if "missing_viewport" in issues:
            snippets.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        if "missing_meta_description" in issues:
            snippets.append(f'<meta name="description" content="{site_name} 핵심 가이드 및 최신 비교 데이터 정리">')
        if "missing_canonical" in issues:
            page_slug = gap["page"].replace("index.html", "")
            snippets.append(f'<link rel="canonical" href="{self.config.site_domain.rstrip("/")}/{page_slug}">')
        if "incomplete_opengraph" in issues:
            snippets.append(f'<meta property="og:title" content="{site_name} | 공식 가이드">')
            snippets.append(f'<meta property="og:image" content="{self.config.site_domain.rstrip("/")}/og-cover.png">')
        if "missing_json_ld" in issues or "invalid_json_ld" in issues:
            snippets.append(
                '<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebPage","name":"'
                + site_name
                + '"}</script>'
            )
        if not snippets:
            snippets.append(f"<!-- Review issues: {', '.join(issues)} -->")

        return {
            "site": site_name,
            "page": gap["page"],
            "issues": issues,
            "recommended_head_patch": "\n".join(snippets),
        }

    def _render_patch_markdown(
        self,
        run_date: str,
        patches: List[Dict[str, Any]],
        broken_links: List[Dict[str, str]],
    ) -> str:
        lines = [
            f"# 개발팀 일일 SEO & 사이트 헬스 패치 제안서 ({run_date})",
            "",
            f"- 검출된 내부 깨진 링크: **{len(broken_links)}건**",
            f"- 생성된 안전 SEO 패치: **{len(patches)}건**",
            "",
        ]
        if broken_links:
            lines.append("## 1. 내부 깨진 링크 목록")
            for item in broken_links[:15]:
                lines.append(f"- `{item['site']}/{item['source_page']}` → `{item['broken_href']}`")
            lines.append("")

        lines.append("## 2. 권장 `<head>` SEO 보강 패치")
        if not patches:
            lines.append("- 현재 스캔된 페이지에서 추가 `<head>` 패치가 필요한 항목이 없습니다.")
        for p in patches:
            lines.append(f"### `{p['site']}/{p['page']}` ({', '.join(p['issues'])})")
            lines.append("```html")
            lines.append(p["recommended_head_patch"])
            lines.append("```")
            lines.append("")
        return "\n".join(lines)
