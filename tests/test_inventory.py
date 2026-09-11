"""Catalog rendering must retain every skill and usable documentation links."""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

from scripts.inventory import render_markdown


class MarkdownCatalogTests(unittest.TestCase):
    def test_catalog_links_cover_all_skills_and_preserve_table_structure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "README.md").write_text("# Library\n")
            (root / "docs/tooling.md").write_text("# Tools\n")
            paths = {"skills": "skills/example", "agents": "agents/example", "workflows": "workflows/example", "evals": "evals/example"}
            for folder in paths.values():
                (root / folder).mkdir(parents=True)
            for name in ("first", "second"):
                folder = root / paths["skills"] / name
                folder.mkdir()
                (folder / "SKILL.md").write_text(f"---\nname: {name}\ndescription: |\n  Проверка A | B\n  с <условием>.\n---\n", encoding="utf-8")
            catalog = {"repository": {"version": "1.2.0"}, "packs": {"example": paths}}
            result = render_markdown(root, catalog)
            self.assertIn("Навыков: 2", result)
            self.assertIn("Проверка A &#124; B с &lt;условием&gt;.", result)
            self.assertEqual(result.count("/SKILL.md)"), 2)
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", result):
                self.assertTrue((root / "docs" / unquote(target)).exists(), target)
            self.assertEqual(result, render_markdown(root, catalog))


if __name__ == "__main__":
    unittest.main()
