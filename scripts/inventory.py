#!/usr/bin/env python3
"""Print inventory using the repository catalog's pack paths."""

from __future__ import annotations

import sys
import argparse
from pathlib import Path
from urllib.parse import quote

if __package__:
    from .validate_repo import ROOT, PACK_PATTERNS, ValidationError, iter_files, load_catalog, pack_files, parse_frontmatter, read_text
else:
    from validate_repo import ROOT, PACK_PATTERNS, ValidationError, iter_files, load_catalog, pack_files, parse_frontmatter, read_text


PACK_TITLES = {
    "core": "Работа с проектом и проверка результата",
    "agile-delivery": "Требования и управление поставкой",
    "xops-platform": "Платформа и эксплуатация",
    "software-engineering": "Разработка программного обеспечения",
    "data-platform": "Данные и аналитическая платформа",
    "ml-mlops": "ML, MLOps и RAG",
    "qa-aqa": "Качество и автоматизация тестирования",
    "security": "Безопасность",
    "office-work": "Офисная работа",
}


def table_text(value: str) -> str:
    return " ".join(value.split()).replace("|", "&#124;").replace("<", "&lt;").replace(">", "&gt;")


def render_markdown(root: Path, catalog: dict) -> str:
    """Render a browsable catalog whose links are relative to docs/catalog.md."""
    lines = [
        "# Каталог навыков",
        "",
        f"Версия {catalog['repository']['version']}. Состав и описания взяты из `codex-skills.yaml` и файлов `SKILL.md`.",
        "",
        "Обновление из корня репозитория: `python3 scripts/inventory.py --markdown > docs/catalog.md`.",
        "Для выбора набора и установки см. [README](../README.md) и [инструменты](tooling.md).",
        "",
    ]
    for pack, paths in catalog["packs"].items():
        files = pack_files(root, paths, "skills")
        lines.extend([
            f"## {PACK_TITLES.get(pack, pack)} (`{pack}`)",
            "",
            f"Навыков: {len(files)}. " + " · ".join(
                f"[{label}](../{quote(paths[kind], safe='/')}/)"
                for kind, label in (("agents", "Роли"), ("workflows", "Рабочие процессы"), ("evals", "Сценарии проверки"))
            ),
            "",
            "| Навык | Когда применять |",
            "| --- | --- |",
        ])
        for path in files:
            metadata = parse_frontmatter(read_text(path), str(path.relative_to(root)))
            name = table_text(metadata["name"])
            description = table_text(metadata["description"])
            link = quote(path.relative_to(root).as_posix(), safe="/")
            lines.append(f"| [{name}](../{link}) | {description} |")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Показать состав библиотеки по каталогу.")
    parser.add_argument("--markdown", action="store_true", help="вывести каталог для docs/catalog.md вместо сводки CSV")
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog(ROOT)
        if args.markdown:
            print(render_markdown(ROOT, catalog), end="")
            return 0
    except ValidationError as error:
        print(f"ERROR: {error}")
        return 1
    print(f"codex-skills version: {catalog['repository']['version']}")
    print()
    print("pack,skills,agents,workflows,evals")
    totals = dict.fromkeys(PACK_PATTERNS, 0)
    for pack, paths in catalog["packs"].items():
        counts = {kind: len(pack_files(ROOT, paths, kind)) for kind in PACK_PATTERNS}
        print(",".join([pack, *(str(count) for count in counts.values())]))
        for kind, count in counts.items():
            totals[kind] += count
    print()
    print(f"templates,{sum(1 for _ in iter_files(ROOT / 'templates'))}")
    for kind, count in totals.items():
        print(f"total_{kind},{count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
