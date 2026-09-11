"""Проверки разделения заданий, полноты сценариев и безопасного экспорта."""

from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from scripts import prepare_eval as exporter


class ExportTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / "library"
        self.root.mkdir()
        self.source = "evals/sample-tasks/example/example.md"
        self.skill = "skills/example/example-skill/SKILL.md"
        self.source_text = (
            "# Сценарий\n\n## Запрос\n\nСравни записи без внешних обращений.\n\n"
            "## Исходные данные\n\n```text\n## Это данные, а не раздел\nA: 7\nB: 9\n```\n\n"
            "## Критерии приёмки\n\nЗакрытый критерий: разница равна двум.\n\n"
            "## Признаки ошибки\n\nЗакрытая ошибка: спутаны основания сравнения.\n"
        )
        self.write(self.source, self.source_text)
        self.write(self.skill, "---\nname: example-skill\ndescription: Работа с примером.\n---\n\n# Навык\n\nПроверь основания сравнения.\n")
        self.write(".memory/private.md", "Не включать эту память в экспорт.")
        self.write("README.md", "Не включать всё содержимое репозитория.")
        self.write("VERSION", "1.2.0\n")
        self.catalog = {"repository": {"version": "1.2.0"}, "packs": {"example": {"skills": "skills/example", "evals": "evals/sample-tasks/example"}}}
        self.case = {"id": "example/example", "pack": "example", "source": self.source, "skills": ["example-skill"], "steps": [{"id": "main", "mode": "text-only", "condition": "Первый запрос в новом диалоге.", "setup": [], "skills": ["example-skill"], "task_sections": [{"section": "Запрос"}, {"section": "Исходные данные"}], "acceptance_sections": [{"section": "Критерии приёмки"}], "failure_sections": [{"section": "Признаки ошибки"}]}]}
        self.save()

    def write(self, relative, text):
        destination = self.root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")

    def save(self, refresh_hash=True):
        if refresh_hash:
            self.case["source_sha256"] = hashlib.sha256((self.root / self.source).read_bytes()).hexdigest()
        self.write("codex-skills.yaml", yaml.safe_dump(self.catalog, allow_unicode=True, sort_keys=False))
        self.write("evals/cases.yaml", yaml.safe_dump({"schema_version": 1, "cases": [self.case]}, allow_unicode=True, sort_keys=False))

    def assert_rejected_without_output(self, message=None):
        destination = self.base / "output"
        with self.assertRaises(exporter.EvalError) as caught:
            exporter.prepare(self.case["id"], destination, self.root)
        if message:
            self.assertIn(message, str(caught.exception))
        self.assertFalse(destination.exists())

    def test_task_has_only_selected_instructions_request_and_inputs(self):
        files = exporter.build_bundle(self.case["id"], self.root)
        task = files["task.md"].decode()
        criteria = files["criteria.md"].decode()
        self.assertIn((self.root / self.skill).read_text().strip(), task)
        self.assertIn("## Это данные, а не раздел\nA: 7\nB: 9", task)
        self.assertIn("criteria.md и manifest.json предназначены проверяющему", task)
        self.assertNotIn("Закрытый критерий", task)
        self.assertNotIn("Закрытая ошибка", task)
        self.assertNotIn("Не включать эту память", task)
        self.assertNotIn("Не включать всё содержимое", task)
        self.assertIn("Закрытый критерий", criteria)
        self.assertIn("Закрытая ошибка", criteria)
        self.assertEqual(set(files), {"task.md", "criteria.md", "manifest.json"})

    def test_manifest_hashes_paths_versions_and_execution_boundary(self):
        files = exporter.build_bundle(self.case["id"], self.root)
        manifest = json.loads(files["manifest.json"])
        self.assertEqual(manifest["format_version"], 1)
        self.assertEqual(manifest["library_version"], "1.2.0")
        self.assertEqual(manifest["source"]["path"], self.source)
        self.assertEqual(manifest["skills"][0]["path"], self.skill)
        self.assertFalse(manifest["runner"]["execution_performed"])
        self.assertFalse(manifest["runner"]["semantic_auto_validation"])
        self.assertEqual(manifest["runner"]["criteria_recipient"], "reviewer-only")
        for record in manifest["inputs"] + [manifest["source"]] + manifest["skills"]:
            self.assertEqual(record["sha256"], hashlib.sha256((self.root / record["path"]).read_bytes()).hexdigest())
        for record in manifest["outputs"]:
            self.assertEqual(record["sha256"], hashlib.sha256(files[record["path"]]).hexdigest())
        self.assertNotIn("Закрытый критерий", files["manifest.json"].decode())
        self.assertNotIn(str(self.root), files["manifest.json"].decode())

    def test_list_json_and_pack_filter(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = exporter.main(["list", "--pack", "example", "--json"], self.root)
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue()), [{"id": "example/example", "pack": "example", "source": self.source, "skills": ["example-skill"], "mode": "text-only", "steps": 1}])
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(exporter.main(["list", "--pack", "unknown"], self.root), 1)

    def test_unknown_id_does_not_create_output(self):
        destination = self.base / "output"
        with self.assertRaisesRegex(exporter.EvalError, "Сценарий не найден"):
            exporter.prepare("example/missing", destination, self.root)
        self.assertFalse(destination.exists())

    def test_changed_source_requires_review_of_partition(self):
        self.write(self.source, self.source_text + "Изменение критерия.\n")
        self.assert_rejected_without_output("Исходник изменён")

    def test_missing_section_rejected(self):
        self.case["steps"][0]["task_sections"][0]["section"] = "Отсутствует"
        self.save()
        self.assert_rejected_without_output("Раздел не найден")

    def test_unclassified_content_after_criteria_rejected(self):
        self.write(self.source, self.source_text + "\n## Контрпример\n\nСущественное новое условие.\n")
        self.save()
        self.assert_rejected_without_output("Не распределено содержимое")

    def test_overlap_between_task_and_criteria_rejected(self):
        self.case["steps"][0]["task_sections"].append({"section": "Критерии приёмки"})
        self.save()
        self.assert_rejected_without_output("Пересечение")

    def test_ambiguous_excerpt_rejected(self):
        self.write(self.source, self.source_text.replace("Сравни записи без внешних обращений.", "Повтор. Повтор."))
        self.case["steps"][0]["task_sections"][0]["text"] = "Повтор."
        self.save()
        self.assert_rejected_without_output("неоднозначен")

    def test_duplicate_heading_rejected(self):
        self.write(self.source, self.source_text + "\n## Запрос\n\nВторой запрос.\n")
        self.save()
        self.assert_rejected_without_output("повтор заголовка")

    def test_unclosed_code_fence_rejected(self):
        self.write(self.source, self.source_text + "\n```\n")
        self.save()
        self.assert_rejected_without_output("Незакрытый блок кода")

    def test_unassigned_preamble_rejected(self):
        self.write(self.source, self.source_text.replace("# Сценарий", "# Сценарий\n\nУсловие до разделов."))
        self.save()
        self.assert_rejected_without_output("перед первым разделом")

    def test_counterexample_is_split_into_facts_and_criteria_after_primary_answer(self):
        self.write(self.source, self.source_text + "\n## Контрпример\n\nНовые факты: A: 9, B: 9.\n\nЗакрытый ответ: значения равны.\n")
        self.case["steps"].append({"id": "followup", "mode": "text-only", "condition": "После main в том же диалоге.", "setup": [], "skills": ["example-skill"], "prompt": "Теперь сравни дополнительные записи.", "task_sections": [{"section": "Контрпример", "text": "Новые факты: A: 9, B: 9."}], "acceptance_sections": [{"section": "Контрпример", "text": "Закрытый ответ: значения равны."}], "failure_sections": []})
        self.save()
        files = exporter.build_bundle(self.case["id"], self.root)
        self.assertNotIn("Новые факты", files["task.md"].decode())
        self.assertIn("Новые факты", files["steps/02/task.md"].decode())
        self.assertIn("Теперь сравни", files["steps/02/task.md"].decode())
        self.assertNotIn("Закрытый ответ", files["steps/02/task.md"].decode())
        self.assertIn("Закрытый ответ", files["criteria.md"].decode())
        runner = json.loads(files["manifest.json"])["runner"]["steps"]
        self.assertEqual([(step["order"], step["after"], step["conversation"]) for step in runner], [(1, None, "new"), (2, "main", "continue")])

    def test_invalid_later_step_rejected_before_any_write(self):
        followup = copy.deepcopy(self.case["steps"][0])
        followup["id"] = "followup"
        followup["task_sections"] = [{"section": "Нет такого раздела"}]
        self.case["steps"].append(followup)
        self.save()
        self.assert_rejected_without_output("Раздел не найден")

    def test_prepare_only_requires_explicit_setup(self):
        self.case["steps"][0]["mode"] = "prepare-only"
        self.save()
        self.assert_rejected_without_output("явные условия подготовки")
        self.case["steps"][0]["setup"] = ["Предоставить изолированную копию репозитория."]
        self.save()
        files = exporter.build_bundle(self.case["id"], self.root)
        self.assertIn("Подготовка пакета не означает выполнения", files["task.md"].decode())

    def test_unregistered_source_rejected(self):
        self.write("evals/sample-tasks/example/unregistered.md", self.source_text)
        self.assert_rejected_without_output("не покрывает все исходные файлы")

    def test_source_traversal_rejected(self):
        self.case["source"] = "evals/sample-tasks/example/../../../README.md"
        self.save(refresh_hash=False)
        self.assert_rejected_without_output("без переходов")

    def test_source_symlink_outside_repository_rejected(self):
        outside = self.base / "outside.md"
        outside.write_text(self.source_text, encoding="utf-8")
        (self.root / self.source).unlink()
        (self.root / self.source).symlink_to(outside)
        self.assert_rejected_without_output("за пределы репозитория")

    def test_skill_symlink_outside_repository_rejected(self):
        outside = self.base / "outside.md"
        outside.write_bytes((self.root / self.skill).read_bytes())
        (self.root / self.skill).unlink()
        (self.root / self.skill).symlink_to(outside)
        self.assert_rejected_without_output("за пределы репозитория")

    def test_catalog_directory_symlink_outside_repository_rejected(self):
        outside = self.base / "outside"
        (self.root / "skills/example").rename(outside)
        (self.root / "skills/example").symlink_to(outside, target_is_directory=True)
        self.assert_rejected_without_output("за пределы репозитория")

    def test_catalog_directory_traversal_rejected(self):
        self.catalog["packs"]["example"]["skills"] = "skills/../skills/example"
        self.save()
        self.assert_rejected_without_output("без переходов")

    def test_wrong_pack_source_rejected(self):
        self.write("evals/sample-tasks/other/example.md", self.source_text)
        self.case["source"] = "evals/sample-tasks/other/example.md"
        self.save()
        self.assert_rejected_without_output("вне каталога своего пакета")

    def test_invalid_catalog_and_duplicate_yaml_keys_have_clean_diagnostics(self):
        self.catalog["packs"]["example"] = None
        self.save()
        self.assert_rejected_without_output("описание пакета")
        self.write("codex-skills.yaml", "repository: {}\nrepository: {}\n")
        self.assert_rejected_without_output("Повторяющийся ключ YAML")

    def test_output_parent_alias_is_canonicalized(self):
        real_parent = self.base / "real-parent"
        real_parent.mkdir()
        alias = self.base / "parent-alias"
        alias.symlink_to(real_parent, target_is_directory=True)
        destination = exporter.prepare(self.case["id"], alias / "output", self.root)
        self.assertEqual(destination, real_parent / "output")
        self.assertTrue((destination / "manifest.json").is_file())

    def test_existing_directory_file_and_broken_target_symlink_are_untouched(self):
        directory = self.base / "directory"
        directory.mkdir()
        marker = directory / "task.md"
        marker.write_text("Существующий файл.")
        existing = self.base / "file"
        existing.write_text("Другой файл.")
        symlink = self.base / "broken-link"
        symlink.symlink_to(self.base / "missing")
        for destination in (directory, existing, symlink):
            with self.subTest(destination=destination.name), self.assertRaisesRegex(exporter.EvalError, "уже существует"):
                exporter.prepare(self.case["id"], destination, self.root)
        self.assertEqual(marker.read_text(), "Существующий файл.")
        self.assertEqual(existing.read_text(), "Другой файл.")
        self.assertTrue(symlink.is_symlink())
        self.assertEqual(list(directory.iterdir()), [marker])

    def test_output_traversal_and_missing_parent_rejected(self):
        for destination in (self.base / "library/../output", self.base / "missing/output"):
            with self.subTest(destination=str(destination)), self.assertRaises(exporter.EvalError):
                exporter.prepare(self.case["id"], destination, self.root)
        self.assertFalse((self.base / "output").exists())
        self.assertFalse((self.base / "missing").exists())

    def test_failed_write_removes_only_own_partial_bundle(self):
        destination = self.base / "output"
        untouched = self.base / "keep.md"
        untouched.write_text("Сохранить.")
        original_open = Path.open

        def failing_open(path, *args, **kwargs):
            if path == destination / "criteria.md":
                raise OSError("Ошибка записи для проверки.")
            return original_open(path, *args, **kwargs)

        with mock.patch.object(Path, "open", failing_open):
            with self.assertRaisesRegex(exporter.EvalError, "Не удалось записать"):
                exporter.prepare(self.case["id"], destination, self.root)
        self.assertFalse(destination.exists())
        self.assertEqual(untouched.read_text(), "Сохранить.")


class LibraryExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases, _, _ = exporter.load_cases()

    def test_all_25_real_sources_export_without_criteria_in_tasks(self):
        self.assertEqual(len(self.cases), 25)
        with tempfile.TemporaryDirectory() as directory:
            for case_id, case in self.cases.items():
                with self.subTest(case_id=case_id):
                    destination = exporter.prepare(case_id, Path(directory) / case_id.replace("/", "-"))
                    manifest = json.loads((destination / "manifest.json").read_text())
                    tasks = [(destination / step["task"]).read_text() for step in manifest["runner"]["steps"]]
                    criteria = (destination / "criteria.md").read_text()
                    for step in case["steps"]:
                        for group in ("acceptance_sections", "failure_sections"):
                            for selector in step[group]:
                                _, excerpt, _, _ = exporter.select(selector, case["_sections"])
                                self.assertIn(excerpt, criteria)
                                for task in tasks:
                                    self.assertNotIn(excerpt, task)
                    for record in manifest["outputs"]:
                        self.assertEqual(record["sha256"], hashlib.sha256((destination / record["path"]).read_bytes()).hexdigest())
                    self.assertEqual(len(tasks), len(case["steps"]))

    def test_api_counterexample_preserves_facts_without_answer_guidance(self):
        files = exporter.build_bundle("software-engineering/api-change")
        task = files["task.md"].decode()
        self.assertIn("Другая реализация уже использует транзакцию", task)
        self.assertIn("клиент игнорирует неизвестные поля", task)
        self.assertNotIn("Не повторяй исходные замечания к этой реализации", task)
        self.assertIn("Не повторяй исходные замечания к этой реализации", files["criteria.md"].decode())

    def test_qa_counterexample_preserves_two_fact_sets_without_answers(self):
        files = exporter.build_bundle("qa-aqa/test-strategy")
        task = files["task.md"].decode()
        self.assertIn("Порядок элементов панели в DOM меняется", task)
        self.assertIn("Другой набор создаёт независимые черновики", task)
        self.assertNotIn("Правильные тесты должны продолжать проходить.", task)
        self.assertNotIn("не требуй последовательного выполнения лишь потому", task)

    def test_performance_counterexample_is_a_later_turn_without_answer(self):
        files = exporter.build_bundle("qa-aqa/performance-results")
        self.assertNotIn("520 ms", files["task.md"].decode())
        self.assertIn("520 ms", files["steps/02/task.md"].decode())
        self.assertNotIn("Он соответствует всем заданным критериям", files["steps/02/task.md"].decode())
        self.assertIn("Он соответствует всем заданным критериям", files["criteria.md"].decode())
        steps = json.loads(files["manifest.json"])["runner"]["steps"]
        self.assertEqual(steps[1]["after"], "main")
        self.assertEqual(steps[1]["conversation"], "continue")

    def test_scoped_maintenance_permission_and_skill_are_deferred(self):
        files = exporter.build_bundle("core/scoped-maintenance")
        self.assertNotIn("## Следующий запрос", files["task.md"].decode())
        self.assertNotIn("name: skill-evolution-loop", files["task.md"].decode())
        self.assertIn("## Следующий запрос", files["steps/02/task.md"].decode())
        self.assertIn("name: skill-evolution-loop", files["steps/02/task.md"].decode())
        steps = json.loads(files["manifest.json"])["runner"]["steps"]
        self.assertEqual(steps[1]["mode"], "prepare-only")
        self.assertTrue(steps[1]["setup"])

    def test_message_sending_is_deferred_and_requires_local_mock(self):
        files = exporter.build_bundle("office-work/conditional-reply")
        self.assertNotIn("Отправь именно этот текст", files["task.md"].decode())
        self.assertIn("Отправь именно этот текст", files["steps/02/task.md"].decode())
        self.assertIn("никакого сетевого доступа и реальных адресатов", files["steps/02/task.md"].decode())
        self.assertNotIn("Ожидается один вызов", files["steps/02/task.md"].decode())
        steps = json.loads(files["manifest.json"])["runner"]["steps"]
        self.assertEqual(steps[1]["mode"], "local-mock")
        self.assertIn("невыполненным", steps[1]["condition"])

    def test_simple_edit_does_not_load_a_skill(self):
        files = exporter.build_bundle("core/proportionate-completion")
        self.assertEqual(json.loads(files["manifest.json"])["skills"], [])
        self.assertNotIn("## Инструкции навыка", files["task.md"].decode())

    def test_readme_example_ids_and_tmp_alias_work_through_cli(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            for case_id in ("software-engineering/api-change", "data-platform/pipeline-delivery", "ml-mlops/rag-evaluation", "qa-aqa/performance-results"):
                with self.subTest(case_id=case_id):
                    destination = Path(temporary) / case_id.split("/")[1]
                    result = subprocess.run([sys.executable, "-B", str(exporter.ROOT / "scripts/prepare_eval.py"), "prepare", case_id, "--output", str(destination)], capture_output=True, text=True, check=False)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertTrue((destination / "task.md").is_file())
                    self.assertIn(str(destination.resolve()), result.stdout)
                    self.assertIn("Сценарий не выполнялся", result.stdout)


if __name__ == "__main__":
    unittest.main()
