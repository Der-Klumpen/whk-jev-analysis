#!/usr/bin/env python3
"""03e — Minimal-Prompt-Kosten (Frage-Overhead) + Bestätigung des Bildlimits.

Ausgabe outputs/runs/probe5.json.
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


def tiny(n: int) -> list[Path]:
    d = CACHE / "tiny280"
    d.mkdir(parents=True, exist_ok=True)
    row = json.loads((ROOT / "data/subset_resolved.jsonl").read_text().splitlines()[0])
    src = ROOT / "outputs/tiles" / row["image_id"]
    tiles = json.loads((src / "tiles.json").read_text())["tiles"]
    return [d / f"t{i}.jpg" for i in range(n)]


def minimal_req(files: list[Path], items: list[str], mnem: str) -> dict:
    """Kürzest möglich: instructions = Item, criteria = y/n."""
    assets = {}
    for i, f in enumerate(files):
        with Image.open(f) as im:
            assets[f"t{i}"] = {"type": "image", "format": "jpg", "data_base64": R.prep(im)}
    qs = {f"q{i}": {"type": "choice", "instructions": item, "criteria": {"y": "y", "n": "n"}}
          for i, item in enumerate(items)}
    return {"model": R.MODEL, "state": {"case": f"min-{mnem}"}, "assets": assets, "questions": qs}


def main() -> int:
    catalog = [l for l in (ROOT / "outputs/catalog.txt").read_text().splitlines() if l.strip()]
    res = []

    def attempt(label: str, files: list[Path], n_q: int, builder) -> None:
        req = builder(files, catalog[:n_q], label[:6])
        try:
            resp = R.call_jev(req)
            tok = resp.get("usage", {}).get("input_tokens", 0)
            R.ledger_add(tok / 1e6 * R.COST_MTOK)
            ans = resp.get("answers", {})
            res.append({"probe": label, "tiles": len(files), "q": n_q, "ok": True,
                        "tokens": tok, "tok_per_q": round(tok / n_q, 1),
                        "n_answered": len(ans),
                        "distinct_p": len({round((a.get("probabilities") or {}).get("y") or 0, 3)
                                           for a in ans.values()})})
        except Exception as e:  # noqa: BLE001
            res.append({"probe": label, "tiles": len(files), "q": n_q, "ok": False,
                        "err": str(e)[:90]})
        print(json.dumps(res[-1]), flush=True)

    attempt("minimal tiny + 30 Fragen", tiny(1), 30, minimal_req)
    attempt("minimal tiny + 100 Fragen", tiny(1), 100, minimal_req)
    attempt("minimal 6 tiny + 1 Frage", tiny(6), 1, minimal_req)
    rv = sorted((ROOT / "outputs/tiles").glob("*/tiles.json"))
    row = next(json.loads(l) for l in (ROOT / "data/subset_resolved.jsonl").read_text().splitlines()
               if '"VW"' in l)
    d = ROOT / "outputs/tiles" / row["image_id"]
    tf = d / json.loads((d / "tiles.json").read_text())["tiles"][5]["file"]
    attempt("minimal 1 echte VW-Kachel + 100 Fragen", [tf], 100, minimal_req)
    (ROOT / "outputs/runs/probe5.json").write_text(json.dumps(res, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
