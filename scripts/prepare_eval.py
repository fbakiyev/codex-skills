#!/usr/bin/env python3
"""Подготовить локальный сценарий, отделив задание от критериев проверки."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("Установите зависимости: python3 -m pip install -r requirements-dev.txt")

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "evals/cases.yaml"
FORMAT_VERSION = 1
MODES = {"text-only", "prepare-only", "local-mock"}
GROUPS = ("task_sections", "acceptance_sections", "failure_sections")


class EvalError(ValueError):
    """Ошибка, которую можно показать без раскрытия содержимого исходников."""


class UniqueLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in result
            except TypeError:
                raise EvalError("Недопустимый ключ YAML")
            if duplicate:
                raise EvalError("Повторяющийся ключ YAML")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def digest(data):
    return hashlib.sha256(data).hexdigest()


def string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise EvalError(f"{label}: нужна непустая строка")
    return value


def strings(value, label, empty=False):
    if not isinstance(value, list) or (not empty and not value):
        raise EvalError(f"{label}: нужен список строк")
    for item in value:
        string(item, label)
    if len(value) != len(set(value)):
        raise EvalError(f"{label}: повторяющиеся значения")
    return value


def relative_path(value):
    value = string(value, "Путь источника")
    if "\\" in value or Path(value).is_absolute() or any(p in {"", ".", ".."} for p in value.split("/")):
        raise EvalError("Путь источника должен быть относительным, без переходов по каталогам")
    return value


def source_path(root, value, prefix=None):
    """Разрешать только явные относительные пути внутри данной копии библиотеки."""
    value = relative_path(value)
    path = root / value
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError):
        raise EvalError(f"Источник недоступен: {value}")
    if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
        raise EvalError(f"Источник выходит за пределы репозитория или не является файлом: {value}")
    if prefix is not None:
        base = root / prefix
        if not path.is_relative_to(base) or not resolved.is_relative_to(base.resolve()):
            raise EvalError(f"Источник находится вне каталога своего пакета: {value}")
    return resolved


def read_source(root, value, prefix=None):
    path = source_path(root, value, prefix)
    try:
        data = path.read_bytes()
        text = data.decode("utf-8")
    except (OSError, UnicodeError):
        raise EvalError(f"Нельзя прочитать источник как UTF-8: {value}")
    return text, {"path": value, "sha256": digest(data)}


def load_yaml(text, label):
    try:
        data = yaml.load(text, Loader=UniqueLoader)
    except yaml.YAMLError:
        raise EvalError(f"Некорректный YAML: {label}")
    if not isinstance(data, dict):
        raise EvalError(f"В {label} ожидается отображение YAML")
    return data


def sections(text):
    """Разбирать явные заголовки второго уровня, игнорируя заголовки внутри кода."""
    result = {}
    current = None
    fence = None
    preamble = []
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if marker:
            run = marker.group(1)
            if fence is None:
                fence = (run[0], len(run))
            elif run[0] == fence[0] and len(run) >= fence[1] and not marker.group(2).strip():
                fence = None
        elif fence is None:
            heading = re.fullmatch(r"## ([^\r\n]+)\r?\n?", line)
            if heading:
                current = heading.group(1).strip()
                if current in result:
                    raise EvalError("Неоднозначный повтор заголовка раздела")
                result[current] = []
                continue
        if current is None:
            preamble.append(line)
        else:
            result[current].append(line)
    if fence is not None:
        raise EvalError("Незакрытый блок кода в сценарии")
    visible = [line for line in preamble if line.strip()]
    if len(visible) != 1 or not visible[0].startswith("# "):
        raise EvalError("Условия перед первым разделом должны быть явно включены в manifest")
    if not result:
        raise EvalError("В сценарии нет явных разделов")
    return {heading: "".join(body).strip() for heading, body in result.items()}


def select(selector, available):
    if not isinstance(selector, dict) or set(selector) - {"section", "text"}:
        raise EvalError("Некорректный указатель раздела")
    heading = string(selector.get("section"), "Заголовок раздела")
    if heading not in available:
        raise EvalError(f"Раздел не найден: {heading}")
    body = available[heading]
    excerpt = string(selector.get("text", body), "Содержимое раздела")
    if body.count(excerpt) != 1:
        raise EvalError(f"Фрагмент раздела отсутствует или неоднозначен: {heading}")
    start = body.index(excerpt)
    return heading, excerpt, start, start + len(excerpt)


def resolve_skill(root, catalog, name):
    string(name, "Имя навыка")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise EvalError("Недопустимое имя навыка")
    candidates = []
    for pack in catalog["packs"].values():
        parent = string(pack.get("skills"), "Каталог навыков")
        relative = parent + "/" + name + "/SKILL.md"
        if (root / relative).exists() or (root / relative).is_symlink():
            candidates.append((relative, parent))
    if len(candidates) != 1:
        raise EvalError(f"Навык не найден или неоднозначен: {name}")
    relative, parent = candidates[0]
    text, record = read_source(root, relative, parent)
    frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    if not frontmatter or load_yaml(frontmatter.group(1), relative).get("name") != name:
        raise EvalError(f"Имя навыка не соответствует его файлу: {name}")
    return text, dict(record, name=name)


def load_cases(root=ROOT):
    root = root.resolve()
    raw, manifest_record = read_source(root, MANIFEST)
    manifest = load_yaml(raw, MANIFEST)
    raw_catalog, catalog_record = read_source(root, "codex-skills.yaml")
    catalog = load_yaml(raw_catalog, "codex-skills.yaml")
    version, version_record = read_source(root, "VERSION")
    version = version.strip()
    repository = catalog.get("repository")
    if not isinstance(repository, dict) or not version or repository.get("version") != version:
        raise EvalError("Версия библиотеки не согласована с каталогом")
    packs = catalog.get("packs")
    if not isinstance(packs, dict) or not packs:
        raise EvalError("В каталоге отсутствуют пакеты")
    for pack_name, pack_paths in packs.items():
        if not isinstance(pack_name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", pack_name) or not isinstance(pack_paths, dict):
            raise EvalError("Некорректное описание пакета в каталоге")
        for field in ("skills", "evals"):
            relative = relative_path(pack_paths.get(field))
            try:
                directory = (root / relative).resolve(strict=True)
            except (OSError, RuntimeError):
                raise EvalError(f"Каталог пакета недоступен: {relative}")
            if not directory.is_dir() or not directory.is_relative_to(root):
                raise EvalError(f"Каталог пакета выходит за пределы репозитория: {relative}")
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("cases"), list):
        raise EvalError("Неподдерживаемая схема evals/cases.yaml")
    cases = {}
    sources = set()
    skill_cache = {}
    for case in manifest["cases"]:
        if not isinstance(case, dict):
            raise EvalError("Некорректная запись сценария")
        identity = string(case.get("id"), "ID сценария")
        pack = string(case.get("pack"), "Пакет сценария")
        if pack not in packs or not re.fullmatch(re.escape(pack) + r"/[a-z0-9]+(?:-[a-z0-9]+)*", identity):
            raise EvalError(f"Неверный пакет или ID: {identity}")
        if identity in cases:
            raise EvalError(f"Повторяющийся ID: {identity}")
        names = strings(case.get("skills"), "Навыки сценария", empty=True)
        source = string(case.get("source"), "Источник сценария")
        if source in sources:
            raise EvalError("Один исходный файл зарегистрирован несколько раз")
        source_text, source_record = read_source(root, source, packs[pack]["evals"])
        if case.get("source_sha256") != source_record["sha256"]:
            raise EvalError(f"Исходник изменён; пересмотрите разделение задания и критериев: {identity}")
        available = sections(source_text)
        coverage = {key: [False] * len(value) for key, value in available.items()}
        steps = case.get("steps")
        if not isinstance(steps, list) or not steps:
            raise EvalError(f"Не заданы шаги: {identity}")
        step_ids = set()
        used_skills = set()
        for step in steps:
            if not isinstance(step, dict):
                raise EvalError("Некорректное описание шага")
            sid = string(step.get("id"), "ID шага")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", sid) or sid in step_ids:
                raise EvalError("Повторяющийся или недопустимый ID шага")
            step_ids.add(sid)
            if step.get("mode") not in MODES:
                raise EvalError("Неизвестный режим шага")
            string(step.get("condition"), "Условие запуска")
            strings(step.get("setup"), "Подготовка среды", empty=True)
            if step["mode"] != "text-only" and not step["setup"]:
                raise EvalError("Для этого режима нужны явные условия подготовки")
            step_skills = strings(step.get("skills"), "Навыки шага", empty=True)
            if not set(step_skills).issubset(names):
                raise EvalError("Навык шага отсутствует в списке сценария")
            used_skills.update(step_skills)
            if "prompt" in step:
                string(step["prompt"], "Дополнительный запрос")
            for group in GROUPS:
                selectors = step.get(group)
                if not isinstance(selectors, list) or (group == "task_sections" and not selectors):
                    raise EvalError(f"Не задано явное разделение: {group}")
                for selector in selectors:
                    heading, excerpt, start, end = select(selector, available)
                    if any(coverage[heading][start:end]):
                        raise EvalError(f"Пересечение задания и критериев либо повтор фрагмента: {identity}")
                    coverage[heading][start:end] = [True] * (end - start)
        if used_skills != set(names):
            raise EvalError("Список навыков сценария не совпадает со списками шагов")
        for heading, body in available.items():
            if any(not covered and not char.isspace() for char, covered in zip(body, coverage[heading])):
                raise EvalError(f"Не распределено содержимое раздела: {identity}, {heading}")
        for name in names:
            if name not in skill_cache:
                skill_cache[name] = resolve_skill(root, catalog, name)
        cases[identity] = dict(case, _sections=available, _source_record=source_record)
        sources.add(source)
    actual = {path.relative_to(root).as_posix() for path in (root / "evals/sample-tasks").rglob("*.md")}
    if actual != sources:
        raise EvalError("Manifest не покрывает все исходные файлы сценариев или содержит лишние")
    return cases, skill_cache, {"library_version": version, "inputs": [manifest_record, catalog_record, version_record]}


def render_selectors(selectors, available):
    chunks = []
    previous = None
    for selector in selectors:
        heading, excerpt, _, _ = select(selector, available)
        if heading != previous:
            chunks.append(f"## {heading}")
        chunks.append(excerpt)
        previous = heading
    return "\n\n".join(chunks)


def build_bundle(case_id, root=ROOT):
    cases, skills, provenance = load_cases(root)
    if case_id not in cases:
        raise EvalError(f"Сценарий не найден: {case_id}. Посмотрите команду list.")
    case = cases[case_id]
    files = {}
    runs = []
    criteria = ["# Критерии проверки", "Только для проверяющего после получения ответа. Не передавайте этот файл проверяемой модели. Автоматической оценки смысла ответов нет."]
    for index, step in enumerate(case["steps"], 1):
        path = "task.md" if index == 1 else f"steps/{index:02d}/task.md"
        task = ["# Задание", "Организатору: передайте проверяемому исполнителю только этот task.md. criteria.md и manifest.json предназначены проверяющему. Последующие шаги выдавайте отдельно по порядку и условиям прогона.", f"## Условия прогона\n\nРежим: {step['mode']}.\n\n{step['condition']}"]
        if step["mode"] == "prepare-only":
            task.append("Пока перечисленные исходные данные и изолированная среда не предоставлены, готовьте план или обозначайте недостающие условия. Подготовка пакета не означает выполнения исходного запроса.")
        if step["setup"]:
            task.append("\n".join("- " + item for item in step["setup"]))
        for name in step["skills"]:
            task.extend([f"## Инструкции навыка {name}", skills[name][0].strip()])
        if step.get("prompt"):
            task.extend(["## Запрос следующего шага", step["prompt"]])
        task.append(render_selectors(step["task_sections"], case["_sections"]))
        files[path] = ("\n\n".join(task).strip() + "\n").encode("utf-8")
        criteria.append(f"# Шаг {index}: {step['id']}")
        for group in ("acceptance_sections", "failure_sections"):
            rendered = render_selectors(step[group], case["_sections"])
            if rendered:
                criteria.append(rendered)
        runs.append({"order": index, "id": step["id"], "task": path, "after": None if index == 1 else case["steps"][index - 2]["id"], "conversation": "new" if index == 1 else "continue", "mode": step["mode"], "condition": step["condition"], "setup": step["setup"], "skills": step["skills"]})
    files["criteria.md"] = ("\n\n".join(criteria).strip() + "\n").encode("utf-8")
    output = {"format_version": FORMAT_VERSION, "case_id": case["id"], "pack": case["pack"], **provenance, "source": case["_source_record"], "skills": [skills[name][1] for name in case["skills"]], "runner": {"execution_performed": False, "semantic_auto_validation": False, "criteria_recipient": "reviewer-only", "instructions": "Подавайте модели только task текущего шага. Не передавайте criteria.md или manifest.json. Проверяйте смысл результата отдельно. Без требуемой среды или локальной имитации шаг считается невыполненным, а не успешным.", "steps": runs}, "outputs": [{"path": path, "sha256": digest(data)} for path, data in files.items()]}
    files["manifest.json"] = (json.dumps(output, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return files


def prepare(case_id, destination, root=ROOT):
    files = build_bundle(case_id, root)  # Все входы и всё содержимое проверяются до записи.
    destination = Path(destination).expanduser()
    if ".." in destination.parts:
        raise EvalError("Выходной путь не должен содержать ..")
    destination = destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise EvalError("Выходной каталог уже существует; выберите новый каталог")
    try:
        parent = destination.parent.resolve(strict=True)
    except (OSError, RuntimeError):
        raise EvalError("Родительский каталог должен уже существовать")
    if not parent.is_dir():
        raise EvalError("Родительский каталог должен уже существовать")
    # Явно выбранный родитель может иметь системный псевдоним, например /tmp.
    destination = parent / destination.name
    if destination.exists() or destination.is_symlink():
        raise EvalError("Выходной каталог уже существует; выберите новый каталог")
    created_files = []
    created_dirs = []
    try:
        destination.mkdir(mode=0o700)
        created_dirs.append(destination)
        for relative, data in files.items():
            target = destination / relative
            missing = []
            parent = target.parent
            while parent != destination and not parent.exists():
                missing.append(parent)
                parent = parent.parent
            for directory in reversed(missing):
                directory.mkdir(mode=0o700)
                created_dirs.append(directory)
            with target.open("xb") as stream:
                created_files.append(target)
                stream.write(data)
        return destination
    except OSError:
        # Удаляются только файлы и пустые каталоги, созданные данным вызовом.
        for path in reversed(created_files):
            try:
                path.unlink()
            except OSError:
                pass
        for path in reversed(created_dirs):
            try:
                path.rmdir()
            except OSError:
                pass
        raise EvalError("Не удалось записать пакет; проверьте доступ и свободное место")


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description="Локальная подготовка сценариев без вызова моделей, API и сервисов.")
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="Показать доступные сценарии")
    listing.add_argument("--pack", help="Фильтр по ID пакета")
    listing.add_argument("--json", action="store_true", help="Вывести список как JSON")
    export = commands.add_parser("prepare", help="Подготовить задание и отдельные критерии")
    export.add_argument("case_id", help="ID из команды list, например qa-aqa/performance-results")
    export.add_argument("--output", required=True, help="Новый каталог в существующем родительском каталоге; существующие файлы не перезаписываются")
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            destination = prepare(args.case_id, args.output, root)
            print(f"Пакет подготовлен: {destination}")
            print("Исполнителю передавайте только task.md текущего шага. criteria.md и manifest.json оставьте проверяющему. Сценарий не выполнялся.")
        else:
            cases, _, _ = load_cases(root)
            if args.pack and args.pack not in {case["pack"] for case in cases.values()}:
                raise EvalError(f"Пакет не найден: {args.pack}")
            rows = [{"id": case["id"], "pack": case["pack"], "source": case["source"], "skills": case["skills"], "mode": case["steps"][0]["mode"], "steps": len(case["steps"])} for case in cases.values() if not args.pack or case["pack"] == args.pack]
            if args.json:
                print(json.dumps(rows, ensure_ascii=False, indent=2))
            else:
                for row in rows:
                    print(f"{row['id']}  [{row['mode']}; шагов: {row['steps']}]")
        return 0
    except (EvalError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
