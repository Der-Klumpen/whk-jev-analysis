#!/usr/bin/env python3
"""06 — Reproduzierbare Auswahl: Item-Teilkatalog + Bild-Stichprobe für Messläufe.

  --items-top N     schreibt outputs/catalog_top<N>.txt (Items mit Häufigkeit >= 3,
                    absteigend; N ist nur die Obergrenze)
  --images-per-group K  schreibt data/run_set_<2K>.txt (K Bilder je Gruppe,
                    äquidistant über die sortierte image_id-Liste)

Standardaufruf erzeugt genau die Dateien des 24er-Messlaufs.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT = Path("/home/iiot/data/jev-analysis/katalog-experiment")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items-top", type=int, default=250)
    ap.add_argument("--items-min-count", type=int, default=3)
    ap.add_argument("--images-per-group", type=int, default=12)
    args = ap.parse_args()

    cat = json.loads((ROOT / "outputs/catalog.json").read_text())["items"]
    items = [c["item"] for c in cat if c["count"] >= args.items_min_count][:args.items_top]
    ip = ROOT / "outputs" / f"catalog_top{len(items)}.txt"
    ip.write_text("\n".join(items) + "\n")

    rows = [json.loads(l) for l in (ROOT / "data/subset_resolved.jsonl").read_text().splitlines()]
    sel = []
    for g in ("VW", "4W"):
        sub = sorted((r for r in rows if r["group"] == g), key=lambda r: r["image_id"])
        step = max(1, len(sub) // args.images_per_group)
        sel += [sub[i * step] for i in range(args.images_per_group)]
    sp = ROOT / "data" / f"run_set_{len(sel)}.txt"
    sp.write_text("\n".join(r["image_id"] for r in sel) + "\n")
    print(json.dumps({"items": len(items), "items_file": str(ip),
                      "images": len(sel), "image_file": str(sp)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
