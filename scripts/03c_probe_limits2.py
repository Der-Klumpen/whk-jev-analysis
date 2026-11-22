#!/usr/bin/env python3
"""03c — Limits getrennt ausmessen: Fragenzahl (A), Kachelzahl/Größe (B), Kombination (C).

Ausgabe outputs/runs/probe3.json. Kleine Kachel = 300x280 (Jev-Untergrenze).
"""
from __future__ import annotations
import json
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("runner", Path(__file__).parent / "03_jev_item_existence.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
ROOT = R.ROOT
from PIL import Image

CACHE = ROOT / "outputs/tiles/_probe_cache"


def shrink(n: int, size: tuple[int, int]) -> list[Path]:
    d = CACHE / f"{size[0]}x{size[1]}"
    d.mkdir(parents=True, exist_ok=True)
    out = []
    row = json.loads((ROOT / "data/subset_resolved.jsonl").read_text().splitlines()[0])
    src = ROOT / "outputs/tiles" / row["image_id"]
    tiles = json.loads((src / "tiles.json").read_text())["tiles"]
    for i in range(n):
        f = d / f"t{i}.jpg"
        if not f.exists():
            with Image.open(src / tiles[i]["file"]) as im:
                im.convert("RGB").resize(size, Image.LANCZOS).save(f, "JPEG", quality=90)
        out.append(f)
    return out


def main() -> int:
    catalog = [l for l in (ROOT / "outputs/catalog.txt").read_text().splitlines() if l.strip()]
    res = []

    def attempt(label: str, files: list[Path], n_q: int) -> None:
        req = R.build_request(files, catalog[:n_q], "lim3")
        mb = len(json.dumps(req)) / 1e6
        try:
            resp = R.call_jev(req)
            tok = resp.get("usage", {}).get("input_tokens", 0)
            R.ledger_add(tok / 1e6 * R.COST_MTOK)
            res.append({"probe": label, "tiles": len(files), "q": n_q, "mb": round(mb, 2),
                        "ok": True, "tokens": tok})
        except Exception as e:  # noqa: BLE001
            res.append({"probe": label, "tiles": len(files), "q": n_q, "mb": round(mb, 2),
                        "ok": False, "err": str(e)[:80]})
        print(json.dumps(res[-1]), flush=True)

    # A: Fragenzahl bei minimaler Kachelgröße
    tiny = shrink(1, (300, 280))
    for q in (5, 10, 15, 20, 30):
        attempt(f"A tiny 1 Kachel + {q} Fragen", tiny, q)
    # B: Kachelzahl bei 1 Frage (1568er Kacheln)
    for n in (6, 10, 14, 18):
        attempt(f"B {n} Kacheln + 1 Frage", shrink(n, (1568, 1000)), 1)
    # C: Kombination mittlere Kacheln
    mid = shrink(12, (800, 500))
    for q in (5, 10):
        attempt(f"C 12 Kacheln 800x500 + {q} Fragen", mid, q)
    (ROOT / "outputs/runs/probe3.json").write_text(json.dumps(res, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
