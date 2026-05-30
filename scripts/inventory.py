#!/usr/bin/env python3
"""Print a compact inventory of packs, skills, agents, workflows, templates, and evals."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PACKS = {
    "core": ("skills/core", "agents/core", "workflows/core", "evals/sample-tasks/core"),
    "agile-delivery": ("skills/agile-delivery", "agents/delivery", "workflows/agile", "evals/sample-tasks/agile"),
    "xops-platform": ("skills/xops-platform", "agents/xops", "workflows/xops", "evals/sample-tasks/xops"),
    "software-engineering": ("skills/software-engineering", "agents/engineering", "workflows/engineering", "evals/sample-tasks/engineering"),
    "data-platform": ("skills/data-platform", "agents/data", "workflows/data", "evals/sample-tasks/data"),
    "ml-mlops": ("skills/ml-mlops", "agents/ml", "workflows/ml", "evals/sample-tasks/ml"),
    "qa-aqa": ("skills/qa-aqa", "agents/qa", "workflows/qa", "evals/sample-tasks/qa"),
    "security": ("skills/security", "agents/security", "workflows/security", "evals/sample-tasks/security"),
}


def count(pattern: str) -> int:
    return len(list(ROOT.glob(pattern)))


def main() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    print(f"codex-skills version: {version}")
    print()
    print("pack,skills,agents,workflows,evals")
    for pack, (skills, agents, workflows, evals) in PACKS.items():
        print(
            f"{pack},"
            f"{len(list((ROOT / skills).rglob('SKILL.md')))},"
            f"{len(list((ROOT / agents).glob('*.yaml')))},"
            f"{len(list((ROOT / workflows).glob('*.md')))},"
            f"{len(list((ROOT / evals).glob('*.md')))}"
        )
    print()
    print(f"templates,{count('templates/*')}")
    print(f"total_skills,{count('skills/**/SKILL.md')}")
    print(f"total_agents,{count('agents/**/*.yaml')}")
    print(f"total_workflows,{count('workflows/**/*.md')}")
    print(f"total_evals,{count('evals/**/*.md')}")


if __name__ == "__main__":
    main()
