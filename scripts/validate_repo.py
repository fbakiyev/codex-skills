#!/usr/bin/env python3
"""Validate codex-skills repository structure."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_TOP_LEVEL = [
    "README.md",
    "AGENTS.md",
    "VERSION",
    "codex-skills.yaml",
    "templates",
    "scripts",
    "evals",
]

REQUIRED_TEMPLATES = [
    "access-map.yaml",
    "adr.md",
    "api-contract.md",
    "backlog-item.yaml",
    "backup-restore.md",
    "data-analysis.md",
    "data-contract.yaml",
    "deployment-map.yaml",
    "eval-report.md",
    "handoff.md",
    "incident-report.md",
    "linear-export.yaml",
    "model-card.md",
    "observability.md",
    "performance-report.md",
    "requirements-brief.md",
    "retro.md",
    "runbook.md",
    "security-notes.md",
    "service-catalog.yaml",
    "skill-evolution-record.md",
    "sprint-brief.md",
    "sprint-review.md",
    "standup-update.md",
    "system-analysis.md",
    "system-design.md",
    "test-plan.md",
    "threat-model.md",
    "vulnerability-triage.md",
]

REQUIRED_PACKS = {
    "core": {
        "skills": "skills/core",
        "agents": "agents/core",
        "workflows": "workflows/core",
        "evals": "evals/sample-tasks/core",
    },
    "agile-delivery": {
        "skills": "skills/agile-delivery",
        "agents": "agents/delivery",
        "workflows": "workflows/agile",
        "evals": "evals/sample-tasks/agile",
    },
    "xops-platform": {
        "skills": "skills/xops-platform",
        "agents": "agents/xops",
        "workflows": "workflows/xops",
        "evals": "evals/sample-tasks/xops",
    },
    "software-engineering": {
        "skills": "skills/software-engineering",
        "agents": "agents/engineering",
        "workflows": "workflows/engineering",
        "evals": "evals/sample-tasks/engineering",
    },
    "data-platform": {
        "skills": "skills/data-platform",
        "agents": "agents/data",
        "workflows": "workflows/data",
        "evals": "evals/sample-tasks/data",
    },
    "ml-mlops": {
        "skills": "skills/ml-mlops",
        "agents": "agents/ml",
        "workflows": "workflows/ml",
        "evals": "evals/sample-tasks/ml",
    },
    "qa-aqa": {
        "skills": "skills/qa-aqa",
        "agents": "agents/qa",
        "workflows": "workflows/qa",
        "evals": "evals/sample-tasks/qa",
    },
    "security": {
        "skills": "skills/security",
        "agents": "agents/security",
        "workflows": "workflows/security",
        "evals": "evals/sample-tasks/security",
    },
}

TEXT_EXTENSIONS = {
    ".md",
    ".yaml",
    ".yml",
    ".json",
    ".txt",
    ".py",
}

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:password|passwd|token|api_key|apikey|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{24,}['\"]?"),
    re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{32,}['\"]?"),
    re.compile(r"(?i)ghp_[A-Za-z0-9_]{30,}"),
    re.compile(r"(?i)xox[baprs]-[A-Za-z0-9-]{20,}"),
]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_required_paths() -> None:
    for item in REQUIRED_TOP_LEVEL:
        if not (ROOT / item).exists():
            fail(f"missing required path: {item}")
    for item in REQUIRED_TEMPLATES:
        if not (ROOT / "templates" / item).exists():
            fail(f"missing required template: templates/{item}")


def check_required_packs() -> None:
    for pack, paths in REQUIRED_PACKS.items():
        skills_dir = ROOT / paths["skills"]
        agents_dir = ROOT / paths["agents"]
        workflows_dir = ROOT / paths["workflows"]
        evals_dir = ROOT / paths["evals"]

        if not any(skills_dir.rglob("SKILL.md")):
            fail(f"pack {pack} has no skills under {paths['skills']}")
        if not any(agents_dir.glob("*.yaml")):
            fail(f"pack {pack} has no agents under {paths['agents']}")
        if not any(workflows_dir.glob("*.md")):
            fail(f"pack {pack} has no workflows under {paths['workflows']}")
        if not any(evals_dir.glob("*.md")):
            fail(f"pack {pack} has no eval samples under {paths['evals']}")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    frontmatter = text[4:end].strip().splitlines()
    result: dict[str, str] = {}
    for line in frontmatter:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def check_skills() -> None:
    skills_root = ROOT / "skills"
    if not skills_root.exists():
        return
    for skill_file in skills_root.rglob("SKILL.md"):
        text = read_text(skill_file)
        fm = parse_frontmatter(text)
        rel = skill_file.relative_to(ROOT)
        if not fm.get("name"):
            fail(f"{rel} missing frontmatter name")
        if not fm.get("description"):
            fail(f"{rel} missing frontmatter description")
        if len(text.splitlines()) > 500:
            fail(f"{rel} exceeds 500 lines; move details to references/")
    for readme in skills_root.rglob("README.md"):
        fail(f"extra README inside skills is not allowed: {readme.relative_to(ROOT)}")


def check_agents() -> None:
    agents_root = ROOT / "agents"
    if not agents_root.exists():
        return
    required = ["id:", "display_name:", "mission:", "responsibilities:", "artifacts:"]
    for agent_file in agents_root.rglob("*.yaml"):
        text = read_text(agent_file)
        rel = agent_file.relative_to(ROOT)
        for marker in required:
            if marker not in text:
                fail(f"{rel} missing required agent marker {marker}")


def check_secret_leaks() -> None:
    ignored_dirs = {".git", "__pycache__"}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_dirs for part in path.parts):
            continue
        if path.suffix not in TEXT_EXTENSIONS:
            continue
        text = read_text(path)
        for pattern in SECRET_PATTERNS:
            match = pattern.search(text)
            if match:
                rel = path.relative_to(ROOT)
                fail(f"possible secret leak in {rel}: {match.group(0)[:80]}")


def check_xops_templates() -> None:
    access_map = read_text(ROOT / "templates" / "access-map.yaml")
    if "never_store_value: true" not in access_map:
        fail("templates/access-map.yaml must include never_store_value: true")
    runbook = read_text(ROOT / "templates" / "runbook.md")
    if "Do not duplicate secret values" not in runbook:
        fail("templates/runbook.md must warn against duplicating secret values")


def main() -> None:
    check_required_paths()
    check_required_packs()
    check_skills()
    check_agents()
    check_secret_leaks()
    check_xops_templates()
    print("OK: repository structure is valid")


if __name__ == "__main__":
    main()
