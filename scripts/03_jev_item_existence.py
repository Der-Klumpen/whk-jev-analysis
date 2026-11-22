#!/usr/bin/env python3
"""03 — Jev 1.14: Item-Existenz pro Bild (ja/nein), kachelbasiert.

Ablauf pro Bild: alle Kacheln als Assets in EIN Request, darin ein Block von
Ja/Nein-Fragen zu je einem Katalog-Item („Is the exact text `X` readable on the
tire?"). Bild wird so nur einmal je Request berechnet. Fragen werden in Blöcke
von --questions-per-request geteilt (Default 824 = ganzer Katalog).

Resume: outputs/runs/<run>.jsonl, Schlüssel image_id|item. Budget-Wache gegen
eine Ledger-Datei: bricht ab, wenn Kumul-Kosten --budget übersteigen.

Probe-Modus (--probe) misst erst die echten Grenzen: Fragen/Request,
Assets/Request, Token-Kosten je Kachel und je Frage — ohne die GT zu berühren.

  python3 scripts/03_jev_item_existence.py --probe
  python3 scripts/03_jev_item_existence.py --run pilot --limit-images 5
"""
from __future__ import annotations
import argparse, base64, io, json, random, sys, threading, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path("/home/iiot/data/jev-analysis")
KEY_PATH = Path.home() / "TypeSafe-Keys" / "Jev-Test-Key.txt"
API = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-1.14.0"
TILES = ROOT / "outputs/tiles"
RUNS = ROOT / "outputs/runs"
LEDGER = RUNS / "ledger.json"
COST_MTOK = 0.042          # USD je 1M Input-Tokens (Preisliste TypeSafe)
MAX_AR, MAX_SIDE, MIN_SIDE = 2.5, 1568, 280
INSTR = ("The images {refs} show consecutive, overlapping sections of one "
         "unwrapped tire wall, ordered left to right. Is the exact text `{item}` "
         "readable on the tire? Answer yes or no.")
# Kurzform: nur ein Bild im Request (dann genügt die Kachel-Referenz), Criteria minDestens
# so verschieden, dass Jev nicht dedupliziert.
INSTR_SHORT = "Image `{ref}` (a section of an unwrapped tire wall). Exact text `{item}` readable?"
STYLES = {
    "long": (INSTR, lambda item: {
        "yes": f'The exact text "{item}" is legible somewhere in the shown tire sections.',
        "no": f'The exact text "{item}" is not legible anywhere in the shown tire sections.'}),
    "short": (INSTR_SHORT, lambda item: {
        "yes": f'`{item}` is legible in the image.',
        "no": f'`{item}` is not legible in the image.'}),
}


def key() -> str:
    return KEY_PATH.read_text().strip()


def ledger_add(usd: float) -> float:
    RUNS.mkdir(parents=True, exist_ok=True)
    data = {"cum_usd": 0.0}
    if LEDGER.exists():
        data = json.loads(LEDGER.read_text())
    data["cum_usd"] = round(data.get("cum_usd", 0.0) + usd, 6)
    data["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    LEDGER.write_text(json.dumps(data, indent=1) + "\n")
    return data["cum_usd"]


def prep(im: Image.Image) -> str:
    """Notnetz: Jev-Limits erzwingen (Kacheln sollten sie schon erfüllen)."""
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
            msg = e.read().decode()[:300]
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** attempt); continue
            raise RuntimeError(f"HTTP {e.code}: {msg}") from None
    raise RuntimeError("unreachable")


def build_request(tile_files: list[Path], items: list[str], mnemonic: str,
                  style: str = "long") -> dict:
    assets = {}
    refs = []
    for i, f in enumerate(tile_files):
        ref = f"tile{i:02d}"
        with Image.open(f) as im:
            assets[ref] = {"type": "image", "format": "jpg", "data_base64": prep(im)}
        refs.append(ref)
    instr_t, crit = STYLES[style]
    questions = {}
    for i, item in enumerate(items):
        if style == "short":  # genau ein Bild im Request
            ref = refs[i % len(refs)]
            instr = instr_t.format(ref=ref, item=item)
        else:
            instr = instr_t.format(refs=", ".join(f"`{r}`" for r in refs), item=item)
        questions[f"q{i:03d}"] = {"type": "choice", "instructions": instr,
                                  "criteria": crit(item)}
    return {"model": MODEL, "state": {"case": f"item-existence-{mnemonic}"},
            "assets": assets, "questions": questions}


def answers_to_rows(resp: dict, items: list[str], meta: dict) -> list[dict]:
    out = []
    ans = resp.get("answers", {})
    for i, item in enumerate(items):
        a = ans.get(f"q{i:03d}", {})
        probs = a.get("probabilities", {}) or {}
        out.append({**meta, "item": item, "choice": a.get("choice"),
                    "p_yes": probs.get("yes"), "p_no": probs.get("no"),
                    "confidence": a.get("confidence")})
    return out


def run_image(row: dict, items: list[str], meta: dict, qpr: int,
              style: str = "short", workers: int = 1) -> tuple[list[dict], float]:
    """Kacheln in Gruppen (≤6, unter Tokenbudget) und Fragen in Blöcken abarbeiten.

    Jedes Asset muss im Request referenziert werden, sonst 400 Invalid image
    request — deshalb fragt jede Frage ALLE Kacheln ihrer Gruppe ab (long style)
    bzw. die eine Kachel (short style, 1 Kachel/Gruppe).
    """
    d = TILES / row["image_id"]
    tmeta = json.loads((d / "tiles.json").read_text())
    files = [d / t["file"] for t in tmeta["tiles"]]
    per_tile_tokens = [t["w"] * t["h"] * 2743 / 1e6 for t in tmeta["tiles"]]
    max_tiles = 1 if style == "short" else 6
    budget = 24000.0

    # Kachelgruppen bilden: bis max_tiles und bis das Budget erschöpft ist
    groups, cur, cur_tok = [], [], 0.0
    for i, f in enumerate(files):
        if cur and (len(cur) >= max_tiles or cur_tok + per_tile_tokens[i] > budget * 0.5):
            groups.append((cur, cur_tok)); cur, cur_tok = [], 0.0
        cur.append(i); cur_tok += per_tile_tokens[i]
    if cur:
        groups.append((cur, cur_tok))

    jobs = []
    for gi, (idxs, tok) in enumerate(groups):
        q = qpr if qpr > 0 else max(4, int(budget / (tok + 25)))
        for start in range(0, len(items), q):
            jobs.append((gi, [files[i] for i in idxs], items[start:start + q]))

    rows, cost = [], 0.0
    lock = threading.Lock()

    def work(job):
        gi, fl, chunk = job
        resp = call_jev(build_request(fl, chunk, f"{row['image_id']}-{gi}-{chunk[0]}", style=style))
        tok = resp.get("usage", {}).get("input_tokens", 0)
        usd = tok / 1e6 * COST_MTOK
        with lock:
            ledger_add(usd)
        return answers_to_rows(resp, chunk, {**meta, "tile_group": gi, "n_tiles": len(fl),
                                            "input_tokens": tok}), usd

    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for out, usd in ex.map(work, jobs):
                rows += out; cost += usd
    else:
        for job in jobs:
            out, usd = work(job)
            rows += out; cost += usd
            time.sleep(0.05)
    return rows, cost


def probe() -> int:
    row = json.loads((ROOT / "data/subset_resolved.jsonl").read_text().splitlines()[0])
    d = TILES / row["image_id"]
    if not (d / "tiles.json").exists():
        print("erst scripts/02_make_tiles.py laufen lassen", file=sys.stderr); return 1
    tmeta = json.loads((d / "tiles.json").read_text())
    files = [d / t["file"] for t in tmeta["tiles"]]
    catalog = [l for l in (ROOT / "outputs/catalog.txt").read_text().splitlines() if l.strip()]
    probe_rows = []
    plan = [("1 Kachel / 1 Frage", files[:1], catalog[:1]),
            ("1 Kachel / 50 Fragen", files[:1], catalog[:50]),
            ("1 Kachel / voller Katalog", files[:1], catalog),
            (f"{len(files)} Kacheln / 10 Fragen", files, catalog[:10]),
            (f"{len(files)} Kacheln / voller Katalog", files, catalog)]
    results = []
    for label, fl, items in plan:
        t0 = time.time()
        try:
            resp = call_jev(build_request(fl, items, "probe"))
        except Exception as e:  # noqa: BLE001
            results.append({"probe": label, "n_tiles": len(fl), "n_questions": len(items),
                            "error": str(e)[:200]}); print(json.dumps(results[-1]), flush=True)
            continue
        tok = resp.get("usage", {}).get("input_tokens", 0)
        usd = tok / 1e6 * COST_MTOK
        ledger_add(usd)
        probs = [(resp.get("answers", {}).get(f"q{i:03d}", {}) or {}).get("probabilities", {}) or {}
                 for i in range(len(items))]
        p_yes = [p.get("yes") for p in probs]
        results.append({"probe": label, "n_tiles": len(fl), "n_questions": len(items),
                        "input_tokens": tok, "usd": round(usd, 6),
                        "sec": round(time.time() - t0, 1),
                        "tok_per_tile": round(tok / len(fl), 1) if fl else None,
                        "tok_per_question": round(max(0, tok - (tok / len(fl)) * 0) / len(items), 1),
                        "n_answered": sum(1 for p in probs if p),
                        "p_yes_first10": [round(x, 3) if x is not None else None for x in p_yes[:10]]})
        print(json.dumps(results[-1]), flush=True)
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "probe.json").write_text(json.dumps({"image_id": row["image_id"],
                                                 "n_catalog": len(catalog),
                                                 "results": results}, indent=2) + "\n")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="pilot", help="Namenssuffix der Ausgabedatei")
    ap.add_argument("--limit-images", type=int, default=5)
    ap.add_argument("--questions-per-request", type=int, default=824,
                    help="0 = automatisch aus der Kachelgröße")
    ap.add_argument("--only-images", nargs="*", default=None, help="explizite image_ids statt der ersten N")
    ap.add_argument("--budget", type=float, default=4.40, help="Kumul-Obergrenze USD")
    ap.add_argument("--items", default=str(ROOT / "outputs/catalog.txt"))
    ap.add_argument("--style", choices=["long", "short"], default="long")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--probe", action="store_true")
    args = ap.parse_args()
    if args.probe:
        return probe()

    items = [l for l in Path(args.items).read_text().splitlines() if l.strip()]
    rows = [json.loads(l) for l in (ROOT / "data/subset_resolved.jsonl").read_text().splitlines()]
    if args.only_images:
        want = set(args.only_images)
        rows = [r for r in rows if r["image_id"] in want]
    else:
        rows = rows[:args.limit_images]
    RUNS.mkdir(parents=True, exist_ok=True)
    out = RUNS / f"{args.run}.jsonl"
    done = {json.loads(l)["image_id"] for l in out.read_text().splitlines()} if out.exists() else set()
    cum = json.loads(LEDGER.read_text())["cum_usd"] if LEDGER.exists() else 0.0
    t0, n_img, n_ans, run_cost = time.time(), 0, 0, 0.0
    with out.open("a") as f:
        for row in rows:
            if row["image_id"] in done:
                continue
            if cum > args.budget:
                print(f"Budget-Stop bei {cum:.4f} USD", file=sys.stderr); break
            if not (TILES / row["image_id"] / "tiles.json").exists():
                print(f"Kacheln fehlen: {row['image_id']}", file=sys.stderr); continue
            meta = {"image_id": row["image_id"], "group": row["group"],
                    "ts": datetime.now(timezone.utc).isoformat(timespec="seconds")}
            answered, cost = run_image(row, items, meta, args.questions_per_request, args.style, args.workers)
            for r in answered:
                f.write(json.dumps(r) + "\n")
            f.flush()
            n_img += 1; n_ans += len(answered); run_cost += cost; cum += cost
            print(f"{row['image_id']} +{len(answered)} Antworten {cost:.4f} USD (kumul {cum:.4f})", flush=True)
    summary = {"run": args.run, "images": n_img, "answers": n_ans,
               "cost_usd": round(run_cost, 4), "cum_usd": round(cum, 4),
               "sec": round(time.time() - t0, 1), "out": str(out)}
    (RUNS / f"{args.run}_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
