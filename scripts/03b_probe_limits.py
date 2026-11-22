#!/usr/bin/env python3
"""03b — Grenzen des Jev-Requests ausmessen (Anzahl Fragen, Anzahl/Größe Kacheln).

Kein GT-Bezug, nur Limit-Erkundung. Ausgabe outputs/runs/probe2.json.

  python3 scripts/03b_probe_limits.py
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import importlib.util

spec = importlib.util.spec_from_file_location("runner", Path(__file__).parent / "03_jev_item_existence.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)

ROOT = R.ROOT


def main() -> int:
    row = json.loads((ROOT / "data/subset_resolved.jsonl").read_text().splitlines()[0])
    d = ROOT / "outputs/tiles" / row["image_id"]
    tmeta = json.loads((d / "tiles.json").read_text())
    files = [d / t["file"] for t in tmeta["tiles"]]
    catalog = [l for l in (ROOT / "outputs/catalog.txt").read_text().splitlines() if l.strip()]

    from PIL import Image
    small = ROOT / "outputs/tiles/_probe_small"
    small.mkdir(parents=True, exist_ok=True)
    # kleine Kachel 800x500 aus der ersten Kachel erzeugen
    with Image.open(files[0]) as im:
        im.convert("RGB").resize((800, 500), Image.LANCZOS).save(small / "s.jpg", "JPEG", quality=90)
    small_f = [small / "s.jpg"]

    plan = [
        ("1 Kachel 1568 + 20 Fragen", files[:1], catalog[:20]),
        ("1 Kachel 1568 + 35 Fragen", files[:1], catalog[:35]),
        ("1 Kachel 1568 + 50 Fragen", files[:1], catalog[:50]),
        ("2 Kacheln 1568 + 1 Frage", files[:2], catalog[:1]),
        ("4 Kacheln 1568 + 1 Frage", files[:4], catalog[:1]),
        ("1 Kachel 800x500 + 50 Fragen", small_f, catalog[:50]),
        ("1 Kachel 800x500 + 150 Fragen", small_f, catalog[:150]),
        ("1 Kachel 800x500 + 200 Fragen", small_f, catalog[:200]),
    ]
    res = []
    for label, fl, items in plan:
        req = R.build_request(fl, items, "limit")
        body_mb = len(json.dumps(req)) / 1e6
        try:
            resp = R.call_jev(req)
            tok = resp.get("usage", {}).get("input_tokens", 0)
            R.ledger_add(tok / 1e6 * R.COST_MTOK)
            res.append({"probe": label, "n_tiles": len(fl), "n_q": len(items),
                        "body_mb": round(body_mb, 2), "ok": True, "input_tokens": tok,
                        "tok_per_q": round(tok / len(items), 1),
                        "answered": sum(1 for a in resp.get("answers", {}).values() if a.get("choice"))})
        except Exception as e:  # noqa: BLE001
            res.append({"probe": label, "n_tiles": len(fl), "n_q": len(items),
                        "body_mb": round(body_mb, 2), "ok": False, "error": str(e)[:120]})
        print(json.dumps(res[-1]), flush=True)
    (ROOT / "outputs/runs").mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs/runs/probe2.json").write_text(json.dumps(res, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
