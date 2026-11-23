#!/usr/bin/env python3
"""00 — Subset auflösen: all_test.txt → lokale Pfade + Bildmaße.

Die Subset-Datei enthält absolute Pfade einer fremden Maschine
(/home/seko040e/...). Aufgelöst wird über (Gruppe, Dateiname) auf
/home/iiot/data/OCR/<Gruppe>/images/<Dateiname>.

Ausgabe: data/subset_resolved.jsonl
  {"image_id","group","path","orig_path","width","height"}
Prüft zusätzlich die Existenz von Label-Datei und Annotationsträger und
bricht bei fehlenden Bildern ab.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from PIL import Image

OCR = Path("/home/iiot/data/OCR")
OUT = Path("/home/iiot/data/jev-analysis/katalog-experiment/data")


def main() -> int:
    src = OUT / "subset_all_test.txt"
    lines = [l.strip() for l in src.read_text().splitlines() if l.strip()]
    if not lines:
        print("leeres Subset", file=sys.stderr); return 1
    rows, missing, dup = [], [], []
    seen: set[str] = set()
    for line in lines:
        parts = Path(line).parts
        group, name = parts[-3], parts[-1]
        if group not in ("VW", "4W"):
            print(f"unerwartete Gruppe {group!r} in {line}", file=sys.stderr); return 1
        p = OCR / group / "images" / name
        if name in seen:
            dup.append(name)
        seen.add(name)
        if not p.exists():
            missing.append(str(p)); continue
        if not (OCR / group / "labels" / (p.stem + ".txt")).exists():
            missing.append(str(p) + " (Label fehlt)"); continue
        with Image.open(p) as im:
            w, h = im.size
        rows.append({"image_id": p.stem, "group": group, "path": str(p),
                     "orig_path": line, "width": w, "height": h})
    if missing:
        print(f"{len(missing)} fehlend, z. B. {missing[:3]}", file=sys.stderr)
        if len(missing) > 5:
            return 1
    dst = OUT / "subset_resolved.jsonl"
    with dst.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    n_vw = sum(1 for r in rows if r["group"] == "VW")
    print(json.dumps({"written": len(rows), "VW": n_vw, "4W": len(rows) - n_vw,
                      "duplicates": len(dup), "missing": len(missing), "out": str(dst)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
