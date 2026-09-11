#!/usr/bin/env python3
"""Локальный каталог и установка самостоятельных навыков."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    if __package__:
        from . import validate_repo as validator
    else:
        import validate_repo as validator
except (ImportError, SystemExit):
    raise SystemExit("Установите зависимости: python3 -m pip install -r requirements-dev.txt")

ROOT = validator.ROOT
IDENTIFIER = re.compile(r"[a-z0-9][a-z0-9-]{0,63}\Z")


class CommandError(ValueError):
    """Сообщение без содержимого исходных файлов и системных исключений."""


@dataclass(frozen=True)
class Skill:
    name: str
    pack: str
    path: Path
    description: str

    def as_dict(self) -> dict:
        return {"name": self.name, "pack": self.pack, "path": str(self.path), "description": self.description}


def reject_links(path: Path) -> None:
    for part in [*reversed(path.parents), path]:
        if part.is_symlink():
            raise CommandError("Символические ссылки в пути не поддерживаются, включая системные псевдонимы. Укажите прямой путь к каталогу.")


def read_catalog(root: Path) -> tuple[dict, list[Skill]]:
    root = root.resolve()
    try:
        catalog = validator.load_catalog(root)
        validator.check_required_packs(root, catalog)
        validator.check_skills(root, catalog)
        result = []
        for pack, paths in catalog["packs"].items():
            if not IDENTIFIER.fullmatch(pack):
                raise CommandError("Каталог содержит недопустимый идентификатор пакета.")
            reject_links(root / paths["skills"])
            for path in validator.pack_files(root, paths, "skills"):
                reject_links(path)
                metadata = validator.parse_frontmatter(validator.read_text(path))
                if not IDENTIFIER.fullmatch(metadata["name"]):
                    raise CommandError("Каталог содержит недопустимое имя навыка.")
                result.append(Skill(metadata["name"], pack, path.parent, metadata["description"].strip()))
    except validator.ValidationError:
        raise CommandError("Каталог навыков некорректен. Проверьте его командой scripts/validate_repo.py.") from None
    return catalog, sorted(result, key=lambda item: (item.pack, item.name))


def select_skills(catalog: dict, skills: list[Skill], names: list[str], packs: list[str]) -> list[Skill]:
    known = {skill.name for skill in skills}
    if set(names) - known:
        raise CommandError("Неизвестный навык. Доступные имена показывает команда list.")
    if set(packs) - set(catalog["packs"]):
        raise CommandError("Неизвестный пакет. Доступные пакеты показывает команда list.")
    return [skill for skill in skills if skill.name in names or skill.pack in packs]


def related_content(root: Path, catalog: dict, skill: Skill) -> dict:
    roles = []
    try:
        for paths in catalog["packs"].values():
            for path in validator.pack_files(root, paths, "agents"):
                data = validator.parse_yaml(validator.read_text(path), path.name)
                if skill.name in data.get("skills", []):
                    if not all(isinstance(data.get(key), str) for key in ("id", "display_name")):
                        raise CommandError("Описание связанной роли некорректно.")
                    roles.append({"id": data["id"], "display_name": data["display_name"], "path": str(path)})
    except (validator.ValidationError, TypeError):
        raise CommandError("Не удалось прочитать описания связанных ролей. Проверьте каталог.") from None
    paths = catalog["packs"][skill.pack]
    return {
        "roles": sorted(roles, key=lambda role: role["id"]),
        "workflows": [str(path) for path in validator.pack_files(root, paths, "workflows")],
        "evals": [str(path) for path in validator.pack_files(root, paths, "evals")],
    }


def tree_snapshot(directory: Path) -> dict:
    """Сравнивает содержимое, пустые папки и права; время изменения несущественно."""
    reject_links(directory)
    if not directory.is_dir():
        raise CommandError("Вместо папки навыка обнаружен файл или недоступный путь.")
    result = {}
    for current, directories, files in os.walk(directory, followlinks=False, onerror=_raise_walk_error):
        current_path = Path(current)
        for path in [current_path, *(current_path / name for name in sorted(directories + files))]:
            info = path.lstat()
            relative = path.relative_to(directory).as_posix()
            mode = stat.S_IMODE(info.st_mode)
            if stat.S_ISLNK(info.st_mode):
                raise CommandError("Папка навыка содержит символическую ссылку; установка остановлена.")
            if stat.S_ISDIR(info.st_mode):
                result[relative] = ("directory", mode)
            elif stat.S_ISREG(info.st_mode):
                digest = hashlib.sha256()
                descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
                with os.fdopen(descriptor, "rb") as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(block)
                result[relative] = ("file", mode, digest.hexdigest())
            else:
                raise CommandError("Папка навыка содержит неподдерживаемый тип файла; установка остановлена.")
    return result


def _raise_walk_error(error: OSError) -> None:
    raise CommandError("Не удалось прочитать все файлы навыка. Проверьте права доступа.")


@dataclass
class InstallItem:
    skill: Skill
    target: Path
    snapshot: dict
    skip: bool


def plan_install(skills: list[Skill], destination: Path) -> list[InstallItem]:
    reject_links(destination)
    if destination.exists() and not destination.is_dir():
        raise CommandError("Место установки должно быть каталогом.")
    plan = []
    for skill in skills:
        if destination == skill.path or skill.path in destination.parents:
            raise CommandError("Нельзя устанавливать набор внутрь исходной папки навыка.")
        snapshot = tree_snapshot(skill.path)
        target = destination / skill.name
        if target.is_symlink():
            raise CommandError(f"Конфликт: {skill.name} в месте установки является символической ссылкой.")
        skip = target.exists()
        if skip and tree_snapshot(target) != snapshot:
            raise CommandError(f"Конфликт: установленный {skill.name} отличается от исходника. Файлы не изменены.")
        plan.append(InstallItem(skill, target, snapshot, skip))
    return plan


def make_destination(destination: Path) -> list[Path]:
    missing = []
    path = destination
    while not path.exists():
        missing.append(path)
        path = path.parent
    created = []
    try:
        for path in reversed(missing):
            path.mkdir()
            created.append(path)
    except BaseException:
        for path in reversed(created):
            path.rmdir()
        raise
    return created


def link_contents(source: Path, directory_fd: int) -> None:
    """Добавляет целые подготовленные файлы, не заменяя существующих имён."""
    for entry in sorted(source.iterdir(), key=lambda path: (path.name == "SKILL.md", path.name)):
        if entry.is_dir():
            os.mkdir(entry.name, mode=0o700, dir_fd=directory_fd)
            child_fd = os.open(entry.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory_fd)
            try:
                link_contents(entry, child_fd)
            finally:
                os.close(child_fd)
        else:
            os.link(entry, entry.name, dst_dir_fd=directory_fd, follow_symlinks=False)
    os.fchmod(directory_fd, stat.S_IMODE(source.stat().st_mode))


def rollback(published: list[tuple[InstallItem, int, int]]) -> None:
    incomplete = False
    for item, device, inode in reversed(published):
        try:
            info = item.target.lstat()
            if (info.st_dev, info.st_ino) != (device, inode):
                continue
            current = tree_snapshot(item.target)
            # Незавершённая копия содержит только целые файлы и свои папки.
            owned = all(
                key in item.snapshot and (
                    value == item.snapshot[key]
                    or value[0] == item.snapshot[key][0] == "directory"
                )
                for key, value in current.items()
            )
            if owned:
                shutil.rmtree(item.target)
            else:
                incomplete = True
        except FileNotFoundError:
            continue
        except (OSError, CommandError):
            incomplete = True
    if incomplete:
        print("Некоторые созданные папки требуют проверки: изменённые или недоступные файлы сохранены. Используйте install с --dry-run перед повтором.", file=sys.stderr)


def install(plan: list[InstallItem], destination: Path) -> None:
    pending = [item for item in plan if not item.skip]
    if not pending:
        return
    if os.name != "posix" or not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW"):
        raise CommandError("Локальная установка поддерживается в macOS и Linux; поиск и просмотр доступны отдельно.")
    created = make_destination(destination)
    published = []
    try:
        # Все папки готовы и сверены до появления первого установленного навыка.
        with tempfile.TemporaryDirectory(prefix=".skills-install-", dir=destination) as staging:
            staged = Path(staging)
            for item in pending:
                shutil.copytree(item.skill.path, staged / item.skill.name, symlinks=True)
                if tree_snapshot(staged / item.skill.name) != item.snapshot:
                    raise CommandError("Исходный навык изменился во время копирования. Повторите установку после завершения правок.")
            for item in plan:
                reject_links(item.target)
                if item.skip:
                    if tree_snapshot(item.target) != item.snapshot:
                        raise CommandError("Существующий навык изменился во время подготовки; установка остановлена.")
                elif item.target.exists():
                    raise CommandError(f"Конфликт: {item.skill.name} появился во время подготовки. Повторите проверку.")
            for item in pending:
                reject_links(destination)
                item.target.mkdir(mode=0o700)
                reservation = item.target.lstat()
                identity = (reservation.st_dev, reservation.st_ino)
                published.append((item, *identity))
                directory_fd = os.open(item.target, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                try:
                    opened = os.fstat(directory_fd)
                    if (opened.st_dev, opened.st_ino) != identity:
                        raise CommandError("Каталог назначения изменился во время установки; запись остановлена.")
                    # Дескриптор закрепляет каталог, а link отказывает при совпадении имени.
                    # SKILL.md добавляется последним, после всех вспомогательных файлов.
                    link_contents(staged / item.skill.name, directory_fd)
                    current = item.target.lstat()
                    if (current.st_dev, current.st_ino) != identity:
                        raise CommandError("Каталог назначения изменился во время установки; проверьте результат перед повтором.")
                finally:
                    os.close(directory_fd)
    except BaseException:
        rollback(published)
        for path in reversed(created):
            try:
                path.rmdir()
            except OSError:
                pass
        raise


class RussianParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs["add_help"] = False
        super().__init__(*args, **kwargs)
        self._positionals.title = "Аргументы"
        self._optionals.title = "Параметры"
        self.add_argument("-h", "--help", action="help", help="Показать справку и завершить работу")

    def format_help(self) -> str:
        return super().format_help().replace("usage: ", "Использование: ", 1)

    def error(self, message: str) -> None:
        raise CommandError("Неверные аргументы. Используйте --help у команды для просмотра параметров.")


def make_parser() -> argparse.ArgumentParser:
    parser = RussianParser(description="Поиск, просмотр и локальная установка навыков из каталога репозитория.")
    commands = parser.add_subparsers(dest="command", required=True, title="Команды", metavar="COMMAND")
    listing = commands.add_parser("list", help="Найти навыки")
    listing.add_argument("--pack", action="append", default=[], metavar="PACK", help="Фильтр по пакету; можно повторять")
    listing.add_argument("--query", default="", metavar="TEXT", help="Поиск по имени, пакету и описанию без учёта регистра")
    listing.add_argument("--json", action="store_true", help="Вывести JSON-массив записей name, pack, path, description")
    showing = commands.add_parser("show", help="Показать описание и связи навыка")
    showing.add_argument("name", metavar="SKILL_NAME", help="Имя навыка из команды list")
    installing = commands.add_parser(
        "install", help="Установить выбранный набор в указанную локальную папку",
        description="Установка для macOS/Linux без перезаписи файлов. SKILL.md появляется последним. Весь набор не является общей транзакцией при аварии ОС; незавершённую папку нужно проверить перед повтором.",
    )
    selection = installing.add_mutually_exclusive_group(required=True)
    selection.add_argument("--skill", action="append", default=[], metavar="NAME", help="Навык для установки; можно повторять")
    selection.add_argument("--pack", action="append", default=[], metavar="PACK", help="Пакет для установки; можно повторять")
    installing.add_argument("--dest", required=True, type=Path, metavar="DIR", help="Прямой путь без символических ссылок и '..'; навыки появятся в DIR/<name>")
    installing.add_argument("--dry-run", action="store_true", help="Проверить весь набор и показать план без записи")
    return parser


def main(argv: Optional[list[str]] = None, root: Path = ROOT) -> int:
    try:
        args = make_parser().parse_args(argv)
        root = root.resolve()
        catalog, skills = read_catalog(root)
        if args.command == "list":
            chosen = select_skills(catalog, skills, [], args.pack) if args.pack else skills
            query = args.query.casefold()
            chosen = [skill for skill in chosen if query in " ".join((skill.name, skill.pack, skill.description)).casefold()]
            if args.json:
                print(json.dumps([skill.as_dict() for skill in chosen], ensure_ascii=False, indent=2))
            else:
                for skill in chosen:
                    print(f"{skill.name} [{skill.pack}]\n  {skill.description}")
                if not chosen:
                    print("Подходящих навыков не найдено.")
        elif args.command == "show":
            skill = select_skills(catalog, skills, [args.name], [])[0]
            related = related_content(root, catalog, skill)
            print(f"Навык: {skill.name}\nПакет: {skill.pack}\nПуть: {skill.path}\nОписание: {skill.description}")
            print("\nРоли с явной ссылкой на навык:")
            for role in related["roles"]:
                print(f"- {role['display_name']} ({role['id']}): {role['path']}")
            if not related["roles"]:
                print("- Не указаны.")
            for key, label in (("workflows", "Процессы пакета"), ("evals", "Сценарии проверки пакета")):
                print(f"\n{label}:")
                for path in related[key]:
                    print(f"- {path}")
                if not related[key]:
                    print("- Не указаны.")
        else:
            chosen = select_skills(catalog, skills, args.skill, args.pack)
            candidate = args.dest.expanduser()
            if ".." in candidate.parts:
                raise CommandError("Путь назначения не должен содержать '..'. Укажите прямой путь без перехода к родительскому каталогу.")
            destination = Path(os.path.abspath(candidate))
            plan = plan_install(chosen, destination)
            if not args.dry_run:
                install(plan, destination)
            for item in plan:
                action = "Пропуск: копия совпадает" if item.skip else ("Будет установлен" if args.dry_run else "Установлен")
                print(f"{action}: {item.skill.name} → {item.target}")
            if args.dry_run:
                print("Проверка завершена. Файлы не записаны.")
        return 0
    except CommandError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
    except (OSError, UnicodeError, shutil.Error):
        print("Ошибка: файловая операция не завершена. Проверьте права, свободное место и неизменность исходников и назначения.", file=sys.stderr)
    except KeyboardInterrupt:
        print("Установка прервана. Проверьте состояние командой install с --dry-run перед повтором.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
