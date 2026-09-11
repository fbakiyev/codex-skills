"""Regression cases for catalog validation and safe diagnostics."""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import validate_repo as validator


class RepositoryValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ("templates", "scripts", "evals"):
            (self.root / name).mkdir()
        self.write("README.md", "Example library\n")
        self.write("AGENTS.md", "Contributing rules\n")
        self.write("VERSION", "1.1.0\n")
        self.write("templates/output.md", "Expected result\n")
        self.catalog = {
            "repository": {"version": "1.1.0"},
            "release_target": {"version": "1.1.0", "required_packs": ["core"]},
            "packs": {},
        }
        self.add_pack("core", "example-skill", "example-role")

    def write(self, path: str, text: str) -> None:
        destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")

    def save_catalog(self) -> None:
        self.write("codex-skills.yaml", yaml.safe_dump(self.catalog, sort_keys=False))

    def add_pack(self, pack: str, skill: str, role: str) -> None:
        paths = {"skills": f"skills/{pack}", "agents": f"agents/{pack}", "workflows": f"workflows/{pack}", "evals": f"evals/sample-tasks/{pack}"}
        self.catalog["packs"][pack] = paths
        self.write(f"{paths['skills']}/{skill}/SKILL.md", f"---\nname: {skill}\ndescription: |\n  Use for a specific example.\n---\nComplete the example.\n")
        self.write_agent(f"{paths['agents']}/role.yaml", role, pack, skill)
        self.write(f"{paths['workflows']}/workflow.md", "Example workflow\n")
        self.write(f"{paths['evals']}/example.md", "Example evaluation\n")
        self.save_catalog()

    def write_agent(self, path: str, role: str = "example-role", pack: str = "core", skill: str = "example-skill", **changes) -> None:
        data = {
            "id": role, "pack": pack, "display_name": "Example Role", "mission": "Prepare a useful result.",
            "responsibilities": ["Check the input."], "artifacts": ["templates/output.md"],
            "skills": [skill], "handoff": {"required": False, "template": "templates/output.md"},
        }
        data.update(changes)
        self.write(path, yaml.safe_dump(data))

    def assert_invalid(self, message: str) -> None:
        with self.assertRaisesRegex(validator.ValidationError, message):
            validator.validate(self.root)

    def test_valid_catalog_and_multiline_frontmatter(self) -> None:
        validator.validate(self.root)

    def test_invalid_yaml_is_rejected_without_source_echo(self) -> None:
        marker = "private-input-must-stay-out-of-errors"
        self.write("codex-skills.yaml", f"repository: [\n{marker}\n")
        with self.assertRaises(validator.ValidationError) as caught:
            validator.load_catalog(self.root)
        self.assertIn("invalid YAML", str(caught.exception))
        self.assertNotIn(marker, str(caught.exception))

    def test_duplicate_yaml_keys_are_rejected(self) -> None:
        self.write("agents/core/role.yaml", "id: first\nid: second\n")
        self.assert_invalid("invalid YAML")

    def test_version_mismatch(self) -> None:
        self.catalog["repository"]["version"] = "1.0.0"
        self.save_catalog()
        self.assert_invalid("must match")

    def test_missing_required_pack(self) -> None:
        self.catalog["release_target"]["required_packs"].append("missing")
        self.save_catalog()
        self.assert_invalid("required pack is missing")

    def test_missing_pack_content(self) -> None:
        (self.root / "evals/sample-tasks/core/example.md").unlink()
        self.assert_invalid("has no evals")

    def test_unregistered_skill_directory(self) -> None:
        self.write("skills/other/orphan/SKILL.md", "---\nname: orphan\ndescription: Unregistered skill.\n---\n")
        self.assert_invalid("not assigned to a catalog pack")

    def test_catalog_paths_cannot_escape_repository(self) -> None:
        self.catalog["packs"]["core"]["skills"] = "../external-skills"
        self.save_catalog()
        self.assert_invalid("must stay inside")

    def test_duplicate_skill_names(self) -> None:
        self.add_pack("other", "example-skill", "other-role")
        self.assert_invalid("duplicate skill name")

    def test_skill_name_must_match_folder(self) -> None:
        self.write("skills/core/example-skill/SKILL.md", "---\nname: different\ndescription: Example.\n---\n")
        self.assert_invalid("must match its folder")

    def test_duplicate_agent_ids(self) -> None:
        self.write_agent("agents/core/duplicate.yaml")
        self.assert_invalid("duplicate agent id")

    def test_agent_pack_must_match_directory(self) -> None:
        self.write_agent("agents/core/role.yaml", pack="other")
        self.assert_invalid("pack must match")

    def test_agent_required_fields_are_nonempty(self) -> None:
        self.write_agent("agents/core/role.yaml", mission="   ")
        self.assert_invalid("nonempty agent field mission")

    def test_unknown_skill_reference(self) -> None:
        self.write_agent("agents/core/role.yaml", skill="missing-skill")
        self.assert_invalid("unknown skill")

    def test_missing_artifact_template(self) -> None:
        self.write_agent("agents/core/role.yaml", artifacts=["templates/missing.md"])
        self.assert_invalid("existing file under templates")

    def test_missing_handoff_template(self) -> None:
        self.write_agent("agents/core/role.yaml", handoff={"template": "templates/missing.md"})
        self.assert_invalid("handoff.template")

    def test_runbook_warning_accepts_russian_and_english(self) -> None:
        self.add_pack("xops-platform", "example-xops", "example-operator")
        self.write("templates/access-map.yaml", "never_store_value: true\n")
        for warning in (
            "Ссылайтесь на `access-map.yaml`. Не дублируйте здесь значения секретов.",
            "Reference `access-map.yaml`. Do not duplicate secret values here.",
        ):
            with self.subTest(warning=warning):
                self.write("templates/runbook.md", warning + "\n")
                validator.validate(self.root)

    def test_runbook_still_requires_secret_warning(self) -> None:
        self.add_pack("xops-platform", "example-xops", "example-operator")
        self.write("templates/access-map.yaml", "never_store_value: true\n")
        self.write("templates/runbook.md", "# Инструкция эксплуатации\n\nСсылайтесь на `access-map.yaml`.\n")
        self.assert_invalid("must warn against duplicating secret values")

    def test_secret_diagnostic_never_prints_value(self) -> None:
        secret = "gh" + "p_" + "A" * 35
        self.write("example.txt", "Example\n" + secret + "\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = validator.main(self.root)
        self.assertEqual(result, 1)
        self.assertIn("example.txt:2", output.getvalue())
        self.assertIn("rule: github-token", output.getvalue())
        self.assertNotIn(secret, output.getvalue())

    def test_private_runtime_directories_are_pruned(self) -> None:
        secret = "gh" + "p_" + "B" * 35
        for directory in (".git", ".venv", "venv", "__pycache__"):
            self.write(f"{directory}/nested/example.txt", secret)
        validator.validate(self.root)


if __name__ == "__main__":
    unittest.main()
