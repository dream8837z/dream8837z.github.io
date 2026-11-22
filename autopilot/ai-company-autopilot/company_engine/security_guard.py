"""Step 4 Security Guard — Replaces unsafe blanket 'Always Allow' with Least-Privilege RBAC."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from company_engine.config import DEPARTMENT_SPECS

DANGEROUS_COMMAND_PATTERNS = [
    re.compile(r"\brm\s+-rf\s+(/|~|\$HOME|\*|\.\.)", re.IGNORECASE),
    re.compile(r"\bgit\s+push\s+.*(--force|-f)\b", re.IGNORECASE),
    re.compile(r"\bcurl\b.*\|\s*(bash|sh)\b", re.IGNORECASE),
    re.compile(r"\bchmod\s+-R\s+777\b", re.IGNORECASE),
    re.compile(r"\b(cat|head|tail|printenv)\b.*\.env\b", re.IGNORECASE),
]

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"),
]


class SecurityGuard:
    """Enforces department file ownership, least-privilege scopes, and secret/command hygiene."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir.resolve()

    def build_permissions_policy(self) -> Dict[str, Any]:
        departments_policy: Dict[str, Any] = {}
        for dept_id, spec in DEPARTMENT_SPECS.items():
            departments_policy[dept_id] = {
                "name_ko": spec.name_ko,
                "model_tier": spec.model_tier,
                "allowed_read_globs": spec.allowed_read_globs,
                "allowed_write_dirs": spec.allowed_write_dirs,
                "forbidden_actions": spec.forbidden_actions,
                "blanket_always_allow": False,
            }
        return {
            "policy_version": "1.0.0",
            "principle": "Least Privilege + Department Ownership Matrix (Replaces Unsafe Blanket Always-Allow)",
            "blocked_command_patterns": [p.pattern for p in DANGEROUS_COMMAND_PATTERNS],
            "protected_secret_files": [".env", "*.pem", "*.key", "*credentials*.json", "~/.ssh/*"],
            "departments": departments_policy,
        }

    def check_write_permission(self, dept_id: str, target_path: Path) -> Dict[str, Any]:
        spec = DEPARTMENT_SPECS.get(dept_id)
        if spec is None:
            return {"allowed": False, "reason": f"Unknown department: {dept_id}"}

        resolved = target_path.resolve()
        try:
            rel = resolved.relative_to(self.base_dir).as_posix()
        except ValueError:
            return {
                "allowed": False,
                "reason": f"Write outside project sandbox blocked: {resolved}",
            }

        if rel.endswith(".env") or "/.env" in rel or ".git/" in rel:
            return {"allowed": False, "reason": f"Protected system/secret path blocked: {rel}"}

        for allowed_dir in spec.allowed_write_dirs:
            norm = allowed_dir.rstrip("/")
            if rel == norm or rel.startswith(norm + "/"):
                return {"allowed": True, "relative_path": rel}

        return {
            "allowed": False,
            "reason": f"Department '{dept_id}' cannot write to '{rel}'. Allowed: {spec.allowed_write_dirs}",
        }

    def inspect_command(self, command: str) -> Dict[str, Any]:
        for pattern in DANGEROUS_COMMAND_PATTERNS:
            if pattern.search(command):
                return {
                    "safe": False,
                    "blocked_by": pattern.pattern,
                    "command": command,
                }
        return {"safe": True, "command": command}

    def scan_text_for_secrets(self, text: str) -> List[str]:
        hits: List[str] = []
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                hits.append(pattern.pattern)
        return hits

    def export_policy(self, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        policy = self.build_permissions_policy()
        output_path.write_text(json.dumps(policy, ensure_ascii=False, indent=2), encoding="utf-8")
        return output_path
