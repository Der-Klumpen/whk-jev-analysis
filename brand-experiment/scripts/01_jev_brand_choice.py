#!/usr/bin/env python3
"""01 — Brand-Pilot: Jev 1.14 wählt die Marke aus der Klassenliste (Choice).

Frageform: Multiple-Choice über alle 15 Optionen (14 Marken + „keine Marke
lesbar"), Optionen alphabetisch, Item-String = Klassenname. Ein Request je
Bild mit allen Kacheln des Bildes (Kachelgruppen ≤ 6, adaptive Blockgröße).
Ergebnis je Bild: gewählte Option, Wahrscheinlichkeiten, p der GT-Klasse.

  python3 scripts/01_jev_brand_choice.py --limit 5
"""
from __future__ import annotations
import argparse, base64, io, json, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path("/home/iiot/data/jev-analysis/brand-experiment")
KEY_PATH = Path.home() / "TypeSafe-Keys" / "Jev-Test-Key.txt"
API = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-1.14.0"
TILES = ROOT / "outputs/tiles"
RUNS = ROOT / "outputs/runs"
LEDGER = RUNS / "ledger.json"
COST_MTOK = 0.042
MAX_AR, MAX_SIDE, MIN_SIDE = 2.5, 1568, 280
# Klassenliste = 14 Marken + Abwesenheitsoption (alphabetisch)
MARKEN = ["Bridgestone", "Continental", "Dunlop", "Falken", "Firestone", "Fulda",
          "Goodyear", "Hankook", "Kleber", "Kumho", "Michelin", "Nokian", "Pirelli",
          "Semperit", "Vredestein"]
OPTIONEN = sorted(MARKEN + ["KEINE MARKE LESBAR"])
# Optionen, die nur ein Bild im Subset haben (keine belastbare Aussage je Marke)
SELTEN = {"Falken", "Firestone", "Kleber", "Kumho", "Nokian", "Semperit", "Vredestein", "Fulda"}


def key() -> str:
    return KEY_PATH.read_text().strip()


def ledger_add(usd: float) -> None:
    RUNS.mkdir(parents=True, exist_ok=True)
    d = {"cum_usd": 0.0}
    if LEDGER.exists():
        d = json.loads(LEDGER.read_text())
    d["cum_usd"] = round(d.get("cum_usd", 0.0) + usd, 6)
    d["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    LEDGER.write_text(json.dumps(d, indent=1) + "\n")


def prep(im: Image.Image) -> str:
    w, h = im.size
    if min(w, h) < MIN_SIDE:
        s = MIN_SIDE / min(w, h); im = im.resize((int(w * s), int(h * s)), Image.LANCZOS); w, h = im.size
    if max(w, h) > MAX_SIDE:
        im.thumbnail((MAX_SIDE, MAX_SIDE)); w, h = im.size
    if max(w, h) / min(w, h) > MAX_AR:
        if w > h:
            nh = int(w / MAX_AR); c = Image.new("RGB", (w, nh), (0, 0, 0)); c.paste(im, (0, (nh - h) // 2))
        else:
            nw = int(h * MAX_AR); c = Image.new("RGB", (nw, h), (0, 0, 0)); c.paste(im, ((nw - w) // 2, 0))
        im = c
    buf = io.BytesIO(); im.convert("RGB").save(buf, "JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode()


def call_jev(req: dict, timeout: int = 300, retries: int = 4) -> dict:
    body = json.dumps(req).encode()
    for attempt in range(retries):
        r = urllib.request.Request(API, data=body, method="POST")
        r.add_header("Authorization", f"Bearer {key()}")
        r.add_header("Content-Type", "application/json")
        r.add_header("TypeSafe-Danger-Zone-Images", "true")
        try:
            with urllib.request.urlopen(r, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:200]
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** attempt); continue
            raise RuntimeError(f"HTTP {e.code}: {msg}") from None
    raise RuntimeError("unreachable")


def build_request(files: list[Path]) -> dict:
    assets = {}
    refs = []
    for i, f in enumerate(files):
        ref = f"tile{i:02d}"
        with Image.open(f) as im:
            assets[ref] = {"type": "image", "format": "jpg", "data_base64": prep(im)}
        refs.append(ref)
    refliste = ", ".join(f"`{r}`" for r in refs)
    crit = {o: f"The tire is from brand {o}." if o != "KEINE MARKE LESBAR"
            else "No tire brand name is legible anywhere in the images."
            for o in OPTIONEN}
    q = {"type": "choice",
         "instructions": (f"The images {refliste} show consecutive, overlapping sections "
                          f"of one unwrapped tire wall, ordered left to right. Which brand "
                          f"does this tire belong to? Choose exactly one option."),
         "criteria": crit}
    return {"model": MODEL, "state": {"case": "brand-choice"},
            "assets": assets, "questions": {"brand": q}}


def kachelgruppen(image_id: str) -> list[list[Path]]:
    d = TILES / image_id
    meta = json.loads((d / "tiles.json").read_text())
    files = [d / t["file"] for t in meta["tiles"]]
    tok = [t["w"] * t["h"] * 2743 / 1e6 for t in meta["tiles"]]
    gruppen, cur, cur_tok = [], [], 0.0
    for i, f in enumerate(files):
        if cur and (len(cur) >= 6 or cur_tok + tok[i] > 12000):
            gruppen.append(cur); cur, cur_tok = [], 0.0
        cur.append(i); cur_tok += tok[i]
    if cur:
        gruppen.append(cur)
    return [[files[i] for i in g] for g in gruppen]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--testset", default=str(ROOT / "data/testset_100.jsonl"),
                    help="JSONL des Test-Sets oder TXT mit image_ids (je Zeile eine)")
    ap.add_argument("--ids", nargs="*", default=None,
                    help="explizite image_ids; überschreibt --testset/--limit")
    ap.add_argument("--limit", type=int, default=0, help="0 = alle Bilder des Test-Sets")
    ap.add_argument("--budget", type=float, default=4.50)
    ap.add_argument("--run", default="brand_pilot")
    args = ap.parse_args()
    alle = [json.loads(l) for l in Path(args.testset).read_text().splitlines()]
    if args.ids:  # Klartext-Liste von image_ids (z. B. data/pilot5.txt)
        want = set(args.ids)
        rows = [r for r in alle if r["image_id"] in want]
    elif args.limit > 0:
        rows = alle[:args.limit]
    else:
        rows = alle  # Vollauf: alle Bilder (Resume überspringt Fertige)
    RUNS.mkdir(parents=True, exist_ok=True)
    out = RUNS / f"{args.run}.jsonl"
    done = {json.loads(l)["image_id"] for l in out.read_text().splitlines()} if out.exists() else set()
    cum = json.loads(LEDGER.read_text())["cum_usd"] if LEDGER.exists() else 0.0
    start_kumul = cum
    t0, cost, n = time.time(), 0.0, 0
    with out.open("a") as f:
        for r in rows:
            if r["image_id"] in done or cum - start_kumul > args.budget:
                continue
            antworten = []
            for gi, gruppe in enumerate(kachelgruppen(r["image_id"])):
                resp = call_jev(build_request(gruppe))
                tok = resp.get("usage", {}).get("input_tokens", 0)
                usd = tok / 1e6 * COST_MTOK
                ledger_add(usd); cum += usd; cost += usd
                a = resp.get("answers", {}).get("brand", {})
                probs = a.get("probabilities", {}) or {}
                antworten.append({"tile_group": gi, "n_tiles": len(gruppe),
                                  "choice": a.get("choice"), "confidence": a.get("confidence"),
                                  "p_gt": probs.get(r["marke_gt"]),
                                  "top3": sorted(probs.items(), key=lambda x: -(x[1] or 0))[:3],
                                  "input_tokens": tok})
                f.write(json.dumps({"image_id": r["image_id"], "group": r["group"],
                                    "marke_gt": r["marke_gt"], **antworten[-1]}) + "\n")
                f.flush()
            n += 1
            wc = [a["choice"] for a in antworten]
            richtig = any(c == r["marke_gt"] for c in wc)
            print(f"{r['image_id'][:24]} gt={r['marke_gt']:22s} "
                  f"any-tile-richtig={richtig} entscheidungen={wc} kosten={cost:.4f} USD", flush=True)
    print(json.dumps({"lauf": args.run, "bilder": n, "kosten_usd": round(cost, 4),
                      "kumul_usd": round(cum, 4), "sec": round(time.time() - t0, 1)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
