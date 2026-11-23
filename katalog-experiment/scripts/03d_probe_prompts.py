#!/usr/bin/env python3
"""03d — Kurz-Prompt-Kosten + harte Limits (Bildanzahl, Fragenzahl).

Ausgabe outputs/runs/probe4.json.
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
    out = []
    for i in range(n):
        f = d / f"t{i}.jpg"
        if not f.exists():
            with Image.open(src / tiles[i]["file"]) as im:
                im.convert("RGB").resize((300, 280), Image.LANCZOS).save(f, "JPEG", quality=90)
        out.append(f)
    return out


def real_vw_tile() -> Path:
    """Echte VW-Kachel (flacher Streifen) erzeugen — realistischer Token-Fall."""
    row = next(json.loads(l) for l in (ROOT / "data/subset_resolved.jsonl").read_text().splitlines()
               if '"VW"' in l)
    d = ROOT / "outputs/tiles" / row["image_id"]
    if not (d / "tiles.json").exists():
        spec2 = importlib.util.spec_from_file_location("mk", Path(__file__).parent / "02_make_tiles.py")
        mk = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(mk)
        mk.make_tiles(Path(row["path"]), d)
    meta = json.loads((d / "tiles.json").read_text())
    return d / meta["tiles"][5]["file"]


def main() -> int:
    catalog = [l for l in (ROOT / "outputs/catalog.txt").read_text().splitlines() if l.strip()]
    res = []

    def attempt(label: str, files: list[Path], n_q: int) -> None:
        req = R.build_request(files, catalog[:n_q], "lim4", style="short")
        mb = len(json.dumps(req)) / 1e6
        try:
            resp = R.call_jev(req)
            tok = resp.get("usage", {}).get("input_tokens", 0)
            R.ledger_add(tok / 1e6 * R.COST_MTOK)
            res.append({"probe": label, "tiles": len(files), "q": n_q, "mb": round(mb, 2),
                        "ok": True, "tokens": tok, "tok_per_q": round(tok / n_q, 1)})
        except Exception as e:  # noqa: BLE001
            res.append({"probe": label, "tiles": len(files), "q": n_q, "mb": round(mb, 2),
                        "ok": False, "err": str(e)[:80]})
        print(json.dumps(res[-1]), flush=True)

    attempt("A short tiny + 30 Fragen", tiny(1), 30)
    for n in (7, 8, 9):
        attempt(f"B short {n} tiny + 1 Frage", tiny(n), 1)
    rv = real_vw_tile()
    with Image.open(rv) as im:
        print("VW-Kachel:", im.size, flush=True)
    attempt("C short 1 echte VW-Kachel + 100 Fragen", [rv], 100)
    attempt("D short 1 echte VW-Kachel + voller Katalog", [rv], len(catalog))
    (ROOT / "outputs/runs/probe4.json").write_text(json.dumps(res, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
