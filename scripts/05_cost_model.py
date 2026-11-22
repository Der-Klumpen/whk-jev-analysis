#!/usr/bin/env python3
"""05 — Kostenmodell (aus gemessenen Raten, keine Schätzung der Raten selbst).

Messgrundlage (outputs/runs/probe*.json, 03er-Sonden):
  - Jev rechnet das Bild PRO FRAGE, nicht pro Request: 1 Kachel + 1 Frage =
    6.665 Input-Token, 1 Kachel + 5 Fragen = 32.086 (≈ 5 × 6.665).
  - Folge: Kosten ≈ Fragen × Kachelfläche, unabhängig von der Bündelung.
  - Raten: 2.743 Token/Mpx Bildfläche (1568×1551-Fall), 0,042 USD/Mtok.
  - Grenzen: ~32k Input-Token/Request (darüber 400 max_tokens_exceeded),
    max. 6 Bilder/Request (ab 7: 400 Invalid image request).

Projektion für den Vollauf: 557 Bilder, Kataloggröße und Überlappung variabel.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT = Path("/home/iiot/data/jev-analysis")
TOK_PER_MPX = 2743.0
USD_PER_MTOK = 0.042
MIN_SIDE, MAX_SIDE, MAX_AR = 280, 1568, 2.5
TARGET_MAX_H = 627


def plan(w: int, h: int, overlap: float) -> tuple[float, int, int]:
    th = min(TARGET_MAX_H, max(MIN_SIDE, h))
    scale = th / h if th / h <= 1.0 else MIN_SIDE / h
    tw = min(MAX_SIDE, int(round(th * MAX_AR)))
    return scale, tw, max(1, int(round(tw * (1 - overlap))))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", type=int, nargs="+", default=[824, 384, 250, 170, 111])
    ap.add_argument("--overlap", type=float, nargs="+", default=[0.5, 0.25])
    args = ap.parse_args()
    rows = [json.loads(l) for l in (ROOT / "data/subset_resolved.jsonl").read_text().splitlines()]
    out = []
    for ov in args.overlap:
        tiles = 0
        area = 0.0
        for r in rows:
            s, tw, stride = plan(r["width"], r["height"], ov)
            w = r["width"] * s
            n = max(1, int((w - tw) // stride) + 1) if w > tw else 1
            tiles += n
            area += n * tw * r["height"] * s
        tokens_per_item_pass = area * TOK_PER_MPX / 1e6
        for items in args.items:
            tok = tokens_per_item_pass * items
            out.append({"overlap": ov, "items": items, "tiles": tiles,
                        "area_mpx": round(area / 1e6, 1),
                        "mio_tokens": round(tok / 1e6, 1),
                        "usd": round(tok / 1e6 * USD_PER_MTOK, 2),
                        "usd_per_image": round(tok / 1e6 * USD_PER_MTOK / len(rows), 4)})
    print(json.dumps({"questions_full": len(rows) * max(args.items),
                      "projection": out}, indent=1))
    (ROOT / "outputs/eval").mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs/eval/cost_projection.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
