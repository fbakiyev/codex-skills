#!/usr/bin/env python3
"""Print inventory using the repository catalog's pack paths."""

from __future__ import annotations

import sys

if __package__:
    from .validate_repo import ROOT, PACK_PATTERNS, ValidationError, iter_files, load_catalog, pack_files
else:
    from validate_repo import ROOT, PACK_PATTERNS, ValidationError, iter_files, load_catalog, pack_files


def main() -> int:
    try:
        catalog = load_catalog(ROOT)
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
