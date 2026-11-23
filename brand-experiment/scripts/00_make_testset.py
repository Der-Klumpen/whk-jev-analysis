#!/usr/bin/env python3
"""00 — Test-Set: 100 Bilder, gleichmäßig über alle 14 Marken + „ohne Marke".

Eingabe: Ground Truth und Subset-Auflösung des Katalog-Experiments (nur lesend).
Regeln:
  - Klasse je Bild = Marke, wenn GENAU EIN exakter Marken-String annotiert ist;
    sonst „Ohne erkennbare Marke" (46 Bilder, darunter Goodyear-Produktnamen).
  - Quoten proportional zum Bestand (Largest-Remainder auf 100), danach jede
    Marke auf mindestens 1 Bild angehoben (Zugabe von den größten Klassen).
  - Auswahl deterministisch (random.Random mit festem Seed).
Ausgabe: data/testset_100.jsonl  {image_id, group, path, width, height, marke_gt}
"""
from __future__ import annotations
import collections, json, random
from pathlib import Path

KAT = Path("/home/iiot/data/jev-analysis/katalog-experiment")
OUT = Path(__file__).resolve().parent.parent / "data/testset_100.jsonl"
N = 100
SEED = 42
MINDEST = 1

marken = {"bridgestone": "Bridgestone", "michelin": "Michelin", "continental": "Continental",
          "pirelli": "Pirelli", "dunlop": "Dunlop", "hankook": "Hankook", "fulda": "Fulda",
          "kleber": "Kleber", "semperit": "Semperit", "nokian": "Nokian", "kumho": "Kumho",
          "falken": "Falken", "firestone": "Firestone", "vredestein": "Vredestein"}
OHNE = "Ohne erkennbare Marke"


def klassen_einteilen():
    gt = [json.loads(l) for l in (KAT / "outputs/ground_truth.jsonl").read_text().splitlines()]
    rows = {json.loads(l)["image_id"]: json.loads(l)
            for l in (KAT / "data/subset_resolved.jsonl").read_text().splitlines()}
    inv: dict[str, list[str]] = collections.defaultdict(list)
    for r in gt:
        s = {marken[it["norm"]] for it in r["items"] if it["norm"] in marken}
        if len(s) == 1:
            inv[next(iter(s))].append(r["image_id"])
        elif not s:
            inv[OHNE].append(r["image_id"])
        # len(s) > 1 gibt es im Subset nicht (geprüft)
    return inv, rows


def main() -> int:
    inv, rows = klassen_einteilen()
    klassen = sorted(inv, key=lambda k: -len(inv[k]))
    quote = {k: N * len(inv[k]) / sum(len(v) for v in inv.values()) for k in klassen}
    basis = {k: int(quote[k]) for k in klassen}
    for k in sorted(klassen, key=lambda k: quote[k] - basis[k], reverse=True)[:N - sum(basis.values())]:
        if len(inv[k]) > basis[k]:
            basis[k] += 1
    # Mindestbesetzung je Marke (kleine Marken hätten sonst 0)
    for k in klassen:
        if basis[k] < MINDEST:
            ueber = MINDEST - basis[k]
            basis[k] = MINDEST
            for k2 in sorted(klassen, key=lambda k2: -basis[k2]):
                frei = basis[k2] - MINDEST if basis[k2] > MINDEST else 0
                if frei:
                    ent = min(frei, ueber)
                    basis[k2] -= ent; ueber -= ent
                    if not ueber:
                        break
            if ueber:
                raise SystemExit(f"Bestand reicht nicht fuer Mindestbesetzung: {k}")
    rng = random.Random(SEED)
    zeilen = []
    for k in klassen:
        ids = sorted(inv[k])
        for iid in rng.sample(ids, min(basis[k], len(ids))):
            r = rows[iid]
            zeilen.append({"image_id": iid, "group": r["group"], "path": r["path"],
                           "width": r["width"], "height": r["height"], "marke_gt": k})
    zeilen.sort(key=lambda r: r["image_id"])
    OUT.write_text("".join(json.dumps(r) + "\n" for r in zeilen))
    ist = collections.Counter(r["marke_gt"] for r in zeilen)
    grp = collections.Counter(r["group"] for r in zeilen)
    print(json.dumps({"summe": len(zeilen), "verteilung": dict(ist),
                      "gruppen": dict(grp), "out": str(OUT)}, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
