#!/usr/bin/env python3
"""Validate catalog metadata, references, and repository structure."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    raise SystemExit("Install validation dependencies: python3 -m pip install -r requirements-dev.txt")

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_TOP_LEVEL = ("README.md", "AGENTS.md", "VERSION", "codex-skills.yaml", "templates", "scripts", "evals")
PACK_PATTERNS = {"skills": "SKILL.md", "agents": "*.yaml", "workflows": "*.md", "evals": "*.md"}
CONTENT_ROOTS = {"skills": "skills", "agents": "agents", "workflows": "workflows", "evals": "evals/sample-tasks"}
IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__"}
TEXT_EXTENSIONS = {".md", ".yaml", ".yml", ".json", ".txt", ".py"}
SECRET_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "credential-assignment": re.compile(r"(?i)(?:password|passwd|token|api_key|apikey|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{24,}['\"]?"),
    "aws-secret": re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{32,}['\"]?"),
    "github-token": re.compile(r"(?i)ghp_[A-Za-z0-9_]{30,}"),
    "slack-token": re.compile(r"(?i)xox[baprs]-[A-Za-z0-9-]{20,}"),
}


class ValidationError(ValueError):
    """A diagnostic safe to display without source values."""


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate keys instead of silently discarding earlier values."""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict:
        self.flatten_mapping(node)
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in mapping
            except TypeError:
                raise yaml.constructor.ConstructorError(None, None, "invalid mapping key", key_node.start_mark)
            if duplicate:
                raise yaml.constructor.ConstructorError(None, None, "duplicate mapping key", key_node.start_mark)
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


def fail(message: str) -> None:
    raise ValidationError(message)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        fail(f"cannot read UTF-8 file: {path.name}")


def parse_yaml(text: str, label: str) -> dict[str, Any]:
    try:
        result = yaml.load(text, Loader=UniqueKeyLoader)
    except yaml.YAMLError as error:
        mark = getattr(error, "problem_mark", None)
        location = f":{mark.line + 1}:{mark.column + 1}" if mark else ""
        # PyYAML's normal exception includes source text, which may contain secrets.
        fail(f"invalid YAML in {label}{location}")
    if not isinstance(result, dict):
        fail(f"{label} must contain a YAML mapping")
    return result


def nonempty(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else bool(value)


def string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        fail(f"{label} must be a nonempty list of strings")
    return value


def required_fields(catalog: dict, section: str, defaults: tuple[str, ...]) -> list[str]:
    standards = catalog.get("standards", {})
    if not isinstance(standards, dict):
        fail("catalog standards must be a mapping")
    schema = standards.get(section, {})
    if not isinstance(schema, dict):
        fail(f"catalog standards.{section} must be a mapping")
    extra = string_list(schema.get("required", list(defaults)), f"standards.{section}.required")
    return list(dict.fromkeys([*defaults, *extra]))


def local_path(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a nonempty relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not (root / path).resolve().is_relative_to(root.resolve()):
        fail(f"{label} must stay inside the repository")
    return root / path


def load_catalog(root: Path = ROOT) -> dict[str, Any]:
    catalog = parse_yaml(read_text(root / "codex-skills.yaml"), "codex-skills.yaml")
    repository = catalog.get("repository")
    release = catalog.get("release_target")
    packs = catalog.get("packs")
    if not isinstance(repository, dict) or not isinstance(release, dict):
        fail("catalog requires repository and release_target mappings")
    version = read_text(root / "VERSION").strip()
    if not version or repository.get("version") != version or release.get("version") != version:
        fail("VERSION, repository.version, and release_target.version must match")
    if not isinstance(packs, dict) or not packs:
        fail("catalog packs must be a nonempty mapping")
    required = string_list(release.get("required_packs"), "release_target.required_packs")
    if len(required) != len(set(required)):
        fail("release_target.required_packs contains duplicate entries")
    if any(pack not in packs for pack in required):
        fail("a required pack is missing from the catalog")
    seen_paths: set[Path] = set()
    for pack, paths in packs.items():
        if not isinstance(pack, str) or not pack.strip() or not isinstance(paths, dict):
            fail("each catalog pack must have a name and path mapping")
        for kind in PACK_PATTERNS:
            path = local_path(root, paths.get(kind), f"pack {pack}.{kind}")
            if not path.resolve().is_relative_to((root / CONTENT_ROOTS[kind]).resolve()):
                fail(f"pack {pack}.{kind} must be under {CONTENT_ROOTS[kind]}")
            if path.resolve() in seen_paths:
                fail(f"pack {pack}.{kind} repeats another catalog path")
            seen_paths.add(path.resolve())
    required_fields(catalog, "skill_frontmatter", ("name", "description"))
    required_fields(catalog, "agent_fields", ("id", "display_name", "mission", "responsibilities", "artifacts"))
    return catalog


def iter_files(directory: Path):
    """Prune environments and Git metadata before visiting their contents."""
    for current, directories, files in os.walk(directory, followlinks=False):
        directories[:] = sorted(name for name in directories if name not in IGNORED_DIRS and not (Path(current) / name).is_symlink())
        for name in sorted(files):
            path = Path(current) / name
            if not path.is_symlink():
                yield path


def pack_files(root: Path, paths: dict[str, str], kind: str) -> list[Path]:
    return [path for path in iter_files(root / paths[kind]) if path.match(PACK_PATTERNS[kind])]


def check_required_paths(root: Path) -> None:
    for item in REQUIRED_TOP_LEVEL:
        if not (root / item).exists():
            fail(f"missing required path: {item}")


def check_required_packs(root: Path, catalog: dict) -> None:
    for kind, pattern in PACK_PATTERNS.items():
        registered: set[Path] = set()
        for pack, paths in catalog["packs"].items():
            files = pack_files(root, paths, kind)
            if not files:
                fail(f"pack {pack} has no {kind} under {paths[kind]}")
            if registered.intersection(files):
                fail(f"catalog {kind} directories overlap")
            registered.update(files)
        actual = {path for path in iter_files(root / CONTENT_ROOTS[kind]) if path.match(pattern)}
        if actual != registered:
            fail(f"some {kind} files are not assigned to a catalog pack")


def parse_frontmatter(text: str, label: str = "SKILL.md") -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        fail(f"{label} missing YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(f"{label} missing closing frontmatter delimiter")
    return parse_yaml("\n".join(lines[1:end]), f"{label} frontmatter")


def check_skills(root: Path, catalog: dict) -> set[str]:
    names: set[str] = set()
    required = required_fields(catalog, "skill_frontmatter", ("name", "description"))
    for paths in catalog["packs"].values():
        for skill_file in pack_files(root, paths, "skills"):
            text = read_text(skill_file)
            rel = str(skill_file.relative_to(root))
            metadata = parse_frontmatter(text, rel)
            for key in required:
                if not nonempty(metadata.get(key)):
                    fail(f"{rel} missing nonempty frontmatter field {key}")
            if not isinstance(metadata["name"], str) or not isinstance(metadata["description"], str):
                fail(f"{rel} name and description must be strings")
            name = metadata["name"]
            if name != skill_file.parent.name:
                fail(f"{rel} frontmatter name must match its folder name")
            if name in names:
                fail(f"duplicate skill name in {rel}")
            names.add(name)
            if len(text.splitlines()) > 500:
                fail(f"{rel} exceeds 500 lines; move details to references/")
    for path in iter_files(root / "skills"):
        if path.name == "README.md":
            fail(f"extra README inside skills is not allowed: {path.relative_to(root)}")
    return names


def check_template_reference(root: Path, value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a nonempty template path")
    path = local_path(root, value, label)
    if not path.resolve().is_relative_to((root / "templates").resolve()) or not path.is_file():
        fail(f"{label} must refer to an existing file under templates/")


def check_agents(root: Path, catalog: dict, skill_names: set[str]) -> None:
    ids: set[str] = set()
    required = required_fields(catalog, "agent_fields", ("id", "display_name", "mission", "responsibilities", "artifacts"))
    for pack, paths in catalog["packs"].items():
        for agent_file in pack_files(root, paths, "agents"):
            rel = str(agent_file.relative_to(root))
            data = parse_yaml(read_text(agent_file), rel)
            for key in required:
                if not nonempty(data.get(key)):
                    fail(f"{rel} missing nonempty agent field {key}")
            for key in ("id", "display_name", "mission"):
                if not isinstance(data[key], str):
                    fail(f"{rel} field {key} must be a string")
            if data["id"] in ids:
                fail(f"duplicate agent id in {rel}")
            ids.add(data["id"])
            if data.get("pack") != pack:
                fail(f"{rel} pack must match its catalog directory")
            string_list(data["responsibilities"], f"{rel} responsibilities")
            artifacts = string_list(data["artifacts"], f"{rel} artifacts")
            for artifact in artifacts:
                if artifact.startswith("templates/"):
                    check_template_reference(root, artifact, f"{rel} artifact reference")
            if "skills" in data:
                skills = string_list(data["skills"], f"{rel} skills")
                if any(skill not in skill_names for skill in skills):
                    fail(f"{rel} references an unknown skill")
            if "handoff" in data:
                handoff = data["handoff"]
                if not isinstance(handoff, dict):
                    fail(f"{rel} handoff must be a mapping")
                if "template" in handoff:
                    check_template_reference(root, handoff["template"], f"{rel} handoff.template")


def check_secret_leaks(root: Path) -> None:
    for path in iter_files(root):
        if path.suffix not in TEXT_EXTENSIONS:
            continue
        text = read_text(path)
        for rule, pattern in SECRET_PATTERNS.items():
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                fail(f"possible secret leak in {path.relative_to(root)}:{line} (rule: {rule})")


def check_xops_templates(root: Path, catalog: dict) -> None:
    if "xops-platform" not in catalog["packs"]:
        return
    if "never_store_value: true" not in read_text(root / "templates" / "access-map.yaml"):
        fail("templates/access-map.yaml must include never_store_value: true")
    runbook = read_text(root / "templates" / "runbook.md")
    warnings = ("Не дублируйте здесь значения секретов", "Do not duplicate secret values")
    if not any(warning in runbook for warning in warnings):
        fail("templates/runbook.md must warn against duplicating secret values")


def validate(root: Path = ROOT) -> None:
    check_required_paths(root)
    check_secret_leaks(root)
    catalog = load_catalog(root)
    check_required_packs(root, catalog)
    skill_names = check_skills(root, catalog)
    check_agents(root, catalog, skill_names)
    check_xops_templates(root, catalog)


def main(root: Path = ROOT) -> int:
    try:
        validate(root)
    except ValidationError as error:
        print(f"ERROR: {error}")
        return 1
    print("OK: repository structure is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
