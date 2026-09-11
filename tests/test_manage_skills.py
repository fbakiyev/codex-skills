"""Проверки каталога и установки в изолированные временные папки."""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from scripts import manage_skills as manager


class ManageSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name).resolve()
        self.root = self.workspace / "library"
        self.destination = self.workspace / "target" / "skills"
        self.catalog = {
            "repository": {"version": "1.2.0"},
            "release_target": {"version": "1.2.0", "required_packs": ["engineering", "office"]},
            "packs": {},
        }
        self.write("VERSION", "1.2.0\n")
        self.write("AGENTS.md", "Правила сопровождения всей библиотеки.\n")
        self.add_pack("engineering", "api-design", "Проектирование совместимого API.")
        self.add_pack("office", "prepare-document", "Подготовка рабочего документа.")
        self.write("skills/engineering/api-design/references/contracts.md", "Контракты и примеры.\n")
        asset = self.root / "skills/engineering/api-design/assets/example.bin"
        asset.parent.mkdir()
        asset.write_bytes(bytes(range(256)))
        self.write("skills/engineering/api-design/scripts/check.py", "print('ok')\n")
        (self.root / "skills/engineering/api-design/scripts/check.py").chmod(0o755)
        (self.root / "skills/engineering/api-design/assets/empty").mkdir()

    def write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def add_pack(self, pack: str, skill: str, description: str) -> None:
        paths = {
            "skills": f"skills/{pack}", "agents": f"agents/{pack}",
            "workflows": f"workflows/{pack}", "evals": f"evals/sample-tasks/{pack}",
        }
        self.catalog["packs"][pack] = paths
        self.write(f"{paths['skills']}/{skill}/SKILL.md", f"---\nname: {skill}\ndescription: {description}\n---\nПроверьте результат.\n")
        self.write(f"{paths['agents']}/owner.yaml", yaml.safe_dump({
            "id": f"{pack}-owner", "display_name": "Ответственный", "skills": [skill],
        }, allow_unicode=True))
        self.write(f"{paths['workflows']}/delivery.md", "# Рабочий процесс\n")
        self.write(f"{paths['evals']}/example.md", "# Сценарий\n")
        self.save_catalog()

    def save_catalog(self) -> None:
        self.write("codex-skills.yaml", yaml.safe_dump(self.catalog, allow_unicode=True))

    def run_command(self, *args: str) -> tuple[int, str, str]:
        output = io.StringIO()
        errors = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = manager.main(list(args), root=self.root)
        self.assertNotIn("Traceback", errors.getvalue())
        return code, output.getvalue(), errors.getvalue()

    def install_command(self, *args: str) -> tuple[int, str, str]:
        return self.run_command("install", *args, "--dest", str(self.destination))

    def test_list_filters_and_show_follow_catalog_mapping(self) -> None:
        code, output, errors = self.run_command("list", "--pack", "engineering", "--query", "СОВМЕСТИМОГО", "--json")
        self.assertEqual((code, errors), (0, ""))
        entries = json.loads(output)
        self.assertEqual([entry["name"] for entry in entries], ["api-design"])
        self.assertEqual(Path(entries[0]["path"]), self.root / "skills/engineering/api-design")
        # Связанная роль может принадлежать другому пакету.
        self.write("agents/office/reviewer.yaml", "id: document-reviewer\ndisplay_name: Рецензент\nskills: [api-design]\n")
        code, output, errors = self.run_command("show", "api-design")
        self.assertEqual((code, errors), (0, ""))
        self.assertIn("engineering-owner", output)
        self.assertIn("document-reviewer", output)
        self.assertNotIn("office-owner", output)
        self.assertIn(str(self.root / "workflows/engineering/delivery.md"), output)
        self.assertIn(str(self.root / "evals/sample-tasks/engineering/example.md"), output)
        self.assertNotIn(str(self.root / "workflows/office/delivery.md"), output)
        self.assertFalse(self.destination.exists())

    def test_list_no_matches_is_an_empty_json_array(self) -> None:
        code, output, errors = self.run_command("list", "--query", "нет-совпадений", "--json")
        self.assertEqual((code, json.loads(output), errors), (0, [], ""))

    def test_install_copies_full_skill_and_no_repository_policy_or_roles(self) -> None:
        code, _, errors = self.install_command("--skill", "api-design")
        self.assertEqual((code, errors), (0, ""))
        installed = self.destination / "api-design"
        self.assertEqual((installed / "references/contracts.md").read_text(), "Контракты и примеры.\n")
        self.assertEqual((installed / "assets/example.bin").read_bytes(), bytes(range(256)))
        self.assertTrue((installed / "assets/empty").is_dir())
        self.assertTrue(stat.S_IMODE((installed / "scripts/check.py").stat().st_mode) & stat.S_IXUSR)
        self.assertEqual({path.name for path in self.destination.iterdir()}, {"api-design"})
        self.assertFalse((installed / "AGENTS.md").exists())
        self.assertFalse((installed / "agents").exists())
        self.assertFalse((self.destination / "prepare-document").exists())

    def test_identical_repeat_skips_without_rewriting(self) -> None:
        self.assertEqual(self.install_command("--skill", "api-design")[0], 0)
        path = self.destination / "api-design/SKILL.md"
        original = path.stat()
        code, output, errors = self.install_command("--skill", "api-design", "--skill", "api-design")
        self.assertEqual((code, errors), (0, ""))
        self.assertIn("Пропуск", output)
        self.assertEqual(output.count("api-design →"), 1)
        self.assertEqual((path.stat().st_ino, path.stat().st_mtime_ns), (original.st_ino, original.st_mtime_ns))

    def test_repeated_packs_install_union_and_preserve_unrelated_files(self) -> None:
        self.destination.mkdir(parents=True)
        unrelated = self.destination / "personal.txt"
        unrelated.write_text("Личный файл.", encoding="utf-8")
        code, _, errors = self.install_command("--pack", "engineering", "--pack", "office", "--pack", "office")
        self.assertEqual((code, errors), (0, ""))
        self.assertEqual({path.name for path in self.destination.iterdir()}, {"api-design", "prepare-document", "personal.txt"})
        self.assertEqual(unrelated.read_text(), "Личный файл.")

    def test_dry_run_does_not_create_destination_or_parents(self) -> None:
        code, output, errors = self.install_command("--pack", "engineering", "--dry-run")
        self.assertEqual((code, errors), (0, ""))
        self.assertIn("Будет установлен", output)
        self.assertFalse(self.destination.parent.exists())

    def test_conflict_blocks_entire_selection_before_any_copy(self) -> None:
        installed = self.destination / "prepare-document"
        installed.mkdir(parents=True)
        (installed / "SKILL.md").write_text("Пользовательская версия.", encoding="utf-8")
        code, output, errors = self.install_command("--skill", "api-design", "--skill", "prepare-document")
        self.assertEqual(code, 2)
        self.assertEqual(output, "")
        self.assertIn("Конфликт", errors)
        self.assertFalse((self.destination / "api-design").exists())
        self.assertEqual((installed / "SKILL.md").read_text(), "Пользовательская версия.")
        self.assertEqual({path.name for path in self.destination.iterdir()}, {"prepare-document"})

    def test_extra_file_and_partial_install_are_conflicts(self) -> None:
        self.assertEqual(self.install_command("--skill", "api-design")[0], 0)
        installed = self.destination / "api-design"
        (installed / "personal.md").write_text("Изменения пользователя.", encoding="utf-8")
        self.assertEqual(self.install_command("--skill", "api-design")[0], 2)
        shutil.rmtree(installed)
        installed.mkdir()
        (installed / "references").mkdir()
        code, _, _ = self.install_command("--skill", "api-design")
        self.assertEqual(code, 2)
        self.assertFalse((installed / "SKILL.md").exists())

    def test_unknown_name_invalid_selector_and_missing_destination_are_safe(self) -> None:
        for args in (
            ("install", "--skill", "../outside", "--dest", str(self.destination)),
            ("install", "--pack", "unknown", "--dest", str(self.destination)),
            ("install", "--skill", "api-design"),
            ("install", "--skill", "api-design", "--pack", "office", "--dest", str(self.destination)),
            ("show", "missing"), ("list", "--pack", "missing"),
        ):
            with self.subTest(args=args):
                code, output, errors = self.run_command(*args)
                self.assertEqual(code, 2)
                self.assertEqual(output, "")
                self.assertIn("Ошибка:", errors)
                self.assertFalse(self.destination.parent.exists())

    def test_duplicate_names_and_traversing_catalog_fail_before_writes(self) -> None:
        self.add_pack("duplicate", "api-design", "Другая версия.")
        self.assertEqual(self.install_command("--skill", "api-design")[0], 2)
        self.assertFalse(self.destination.parent.exists())
        self.catalog["packs"]["engineering"]["skills"] = "../outside"
        self.save_catalog()
        self.assertEqual(self.install_command("--skill", "api-design")[0], 2)
        self.assertFalse(self.destination.parent.exists())

    def test_yaml_errors_do_not_echo_source_values(self) -> None:
        private_marker = "unrelated-private-source-value"
        self.write("codex-skills.yaml", f"repository: [\n{private_marker}\n")
        code, output, errors = self.run_command("list")
        self.assertEqual(code, 2)
        self.assertNotIn(private_marker, output + errors)

    def test_source_symlink_outside_skill_blocks_the_whole_set(self) -> None:
        outside = self.workspace / "private.txt"
        outside.write_text("Не копировать.", encoding="utf-8")
        (self.root / "skills/office/prepare-document/external.txt").symlink_to(outside)
        code, _, errors = self.install_command("--skill", "api-design", "--skill", "prepare-document")
        self.assertEqual(code, 2)
        self.assertIn("символическую ссылку", errors)
        self.assertFalse(self.destination.parent.exists())
        self.assertEqual(outside.read_text(), "Не копировать.")

    def test_destination_symlink_and_symlinked_ancestor_are_rejected(self) -> None:
        external = self.workspace / "external"
        external.mkdir()
        self.destination.mkdir(parents=True)
        (self.destination / "api-design").symlink_to(external, target_is_directory=True)
        self.assertEqual(self.install_command("--skill", "api-design")[0], 2)
        self.assertEqual(list(external.iterdir()), [])
        linked = self.workspace / "linked"
        linked.symlink_to(external, target_is_directory=True)
        code, _, _ = self.run_command("install", "--skill", "api-design", "--dest", str(linked / "skills"))
        self.assertEqual(code, 2)
        self.assertEqual(list(external.iterdir()), [])

    def test_copy_failure_leaves_no_partial_skill_or_new_destination(self) -> None:
        actual_copy = shutil.copytree

        def copy_then_fail(source, target, *args, **kwargs):
            if Path(source).name == "prepare-document":
                Path(target).mkdir()
                (Path(target) / "SKILL.md").write_text("Незавершённая копия.", encoding="utf-8")
                raise OSError("private-os-error-text")
            return actual_copy(source, target, *args, **kwargs)

        with mock.patch.object(manager.shutil, "copytree", side_effect=copy_then_fail):
            code, _, errors = self.install_command("--skill", "api-design", "--skill", "prepare-document")
        self.assertEqual(code, 2)
        self.assertNotIn("private-os-error-text", errors)
        self.assertFalse(self.destination.parent.exists())

    def test_publish_failure_rolls_back_only_newly_installed_skills(self) -> None:
        self.destination.mkdir(parents=True)
        marker = self.destination / "personal.md"
        marker.write_text("Сохранить.", encoding="utf-8")
        actual_link = os.link

        def fail_second(source, target, *args, **kwargs):
            if Path(source).parent.name == "prepare-document":
                raise OSError("Сбой файловой системы.")
            return actual_link(source, target, *args, **kwargs)

        with mock.patch.object(manager.os, "link", side_effect=fail_second):
            self.assertEqual(self.install_command("--skill", "api-design", "--skill", "prepare-document")[0], 2)
        self.assertEqual({path.name for path in self.destination.iterdir()}, {"personal.md"})
        self.assertEqual(marker.read_text(), "Сохранить.")

    def test_source_changes_during_copy_are_not_published(self) -> None:
        actual_copy = shutil.copytree

        def changed_copy(source, target, *args, **kwargs):
            result = actual_copy(source, target, *args, **kwargs)
            if Path(source).name == "api-design":
                (Path(target) / "SKILL.md").write_text("Изменившийся источник.", encoding="utf-8")
            return result

        with mock.patch.object(manager.shutil, "copytree", side_effect=changed_copy):
            code, _, errors = self.install_command("--skill", "api-design")
        self.assertEqual(code, 2)
        self.assertIn("изменился", errors)
        self.assertFalse(self.destination.parent.exists())

    def test_new_empty_destination_from_another_process_is_not_overwritten(self) -> None:
        actual_mkdir = Path.mkdir
        first = self.destination / "api-design"
        competitor = self.destination / "prepare-document"

        def make_competing_directory(path, *args, **kwargs):
            result = actual_mkdir(path, *args, **kwargs)
            if path == first:
                actual_mkdir(competitor)
            return result

        with mock.patch.object(Path, "mkdir", new=make_competing_directory):
            code, _, _ = self.install_command("--skill", "api-design", "--skill", "prepare-document")
        self.assertEqual(code, 2)
        self.assertTrue(competitor.is_dir())
        self.assertEqual(list(competitor.iterdir()), [])
        self.assertFalse(first.exists())

    def test_user_edit_to_skipped_skill_during_preparation_is_preserved(self) -> None:
        self.assertEqual(self.install_command("--skill", "api-design")[0], 0)
        installed = self.destination / "api-design/SKILL.md"
        actual_copy = shutil.copytree

        def edit_existing(source, target, *args, **kwargs):
            result = actual_copy(source, target, *args, **kwargs)
            if Path(source).name == "prepare-document":
                installed.write_text("Новая пользовательская правка.", encoding="utf-8")
            return result

        with mock.patch.object(manager.shutil, "copytree", side_effect=edit_existing):
            code, _, _ = self.install_command("--skill", "api-design", "--skill", "prepare-document")
        self.assertEqual(code, 2)
        self.assertEqual(installed.read_text(), "Новая пользовательская правка.")
        self.assertFalse((self.destination / "prepare-document").exists())

    def test_symlink_followed_by_parent_segment_is_rejected_before_normalizing(self) -> None:
        external = self.workspace / "external" / "nested"
        external.mkdir(parents=True)
        linked = self.workspace / "linked"
        linked.symlink_to(external, target_is_directory=True)
        candidate = linked / ".." / "chosen"
        code, _, errors = self.run_command("install", "--skill", "api-design", "--dest", str(candidate))
        self.assertEqual(code, 2)
        self.assertIn("'..'", errors)
        self.assertFalse((self.workspace / "chosen").exists())
        self.assertFalse((external.parent / "chosen").exists())

    def test_replaced_reservation_does_not_overwrite_competing_empty_directory(self) -> None:
        actual_link_contents = manager.link_contents
        target = self.destination / "api-design"
        competing_identity = []

        def replace_empty_reservation(source, directory_fd):
            if source.name == "api-design":
                target.rmdir()
                target.mkdir()
                competing_identity.append(target.stat().st_ino)
            return actual_link_contents(source, directory_fd)

        with mock.patch.object(manager, "link_contents", side_effect=replace_empty_reservation):
            code, _, _ = self.install_command("--skill", "api-design")
        self.assertEqual(code, 2)
        self.assertEqual(target.stat().st_ino, competing_identity[0])
        self.assertEqual(list(target.iterdir()), [])

    def test_new_file_from_another_process_is_never_overwritten(self) -> None:
        actual_link = os.link
        target = self.destination / "api-design/SKILL.md"

        def create_competing_file(source, name, *args, **kwargs):
            if Path(source).name == "SKILL.md":
                target.write_text("Версия другого процесса.", encoding="utf-8")
            return actual_link(source, name, *args, **kwargs)

        with mock.patch.object(manager.os, "link", side_effect=create_competing_file):
            code, output, errors = self.install_command("--skill", "api-design")
        self.assertEqual(code, 2)
        self.assertEqual(output, "")
        self.assertEqual(target.read_text(), "Версия другого процесса.")
        self.assertIn("требуют проверки", errors)

    def test_rollback_continues_when_one_published_skill_disappeared(self) -> None:
        self.add_pack("third", "third-skill", "Третий навык.")
        actual_link = os.link
        disappeared = self.destination / "prepare-document"

        def fail_after_removing_previous(source, name, *args, **kwargs):
            if Path(source).parent.name == "third-skill":
                shutil.rmtree(disappeared)
                raise OSError("private-publish-error")
            return actual_link(source, name, *args, **kwargs)

        with mock.patch.object(manager.os, "link", side_effect=fail_after_removing_previous):
            code, _, errors = self.install_command("--pack", "engineering", "--pack", "office", "--pack", "third")
        self.assertEqual(code, 2)
        self.assertNotIn("private-publish-error", errors)
        self.assertFalse(self.destination.parent.exists())

    def test_rollback_continues_when_one_published_skill_cannot_be_verified(self) -> None:
        self.add_pack("third", "third-skill", "Третий навык.")
        actual_link = os.link
        actual_snapshot = manager.tree_snapshot
        inaccessible = self.destination / "prepare-document"
        failed = []

        def fail_third(source, name, *args, **kwargs):
            if Path(source).parent.name == "third-skill":
                failed.append(True)
                raise OSError("private-publish-error")
            return actual_link(source, name, *args, **kwargs)

        def unavailable_snapshot(path):
            if failed and path == inaccessible:
                raise PermissionError("private-permission-error")
            return actual_snapshot(path)

        with mock.patch.object(manager.os, "link", side_effect=fail_third), mock.patch.object(manager, "tree_snapshot", side_effect=unavailable_snapshot):
            code, _, errors = self.install_command("--pack", "engineering", "--pack", "office", "--pack", "third")
        self.assertEqual(code, 2)
        self.assertNotIn("private-publish-error", errors)
        self.assertNotIn("private-permission-error", errors)
        self.assertIn("требуют проверки", errors)
        self.assertTrue((inaccessible / "SKILL.md").is_file())
        self.assertFalse((self.destination / "api-design").exists())
        self.assertFalse((self.destination / "third-skill").exists())

    def test_entrypoint_appears_after_all_supporting_resources(self) -> None:
        actual_link = os.link
        installed = self.destination / "api-design"

        def check_entrypoint_order(source, name, *args, **kwargs):
            if Path(source).name == "SKILL.md":
                self.assertTrue((installed / "references/contracts.md").is_file())
                self.assertTrue((installed / "assets/example.bin").is_file())
                self.assertTrue((installed / "scripts/check.py").is_file())
                self.assertTrue((installed / "assets/empty").is_dir())
            else:
                self.assertFalse((installed / "SKILL.md").exists())
            return actual_link(source, name, *args, **kwargs)

        with mock.patch.object(manager.os, "link", side_effect=check_entrypoint_order):
            self.assertEqual(self.install_command("--skill", "api-design")[0], 0)


if __name__ == "__main__":
    unittest.main()
