#!/usr/bin/env python3
"""02 — Auswertung des Brand-Vollaufs: Bild- und Kachelebene, Konfidenz, Verwirrungen.

Auswertungsregeln:
  - any-tile: Bild = Marke X, wenn irgendeine Kachelgruppe X waehlt (wie Pilot).
  - Mehrheit: haeufigste Entscheidung der Kachelgruppen, Konflikte als „uneins".
  - Mittel-p: hoechste durchschnittliche Wahrscheinlichkeit je Option.
Berichte je Ebene: Accuracy je Marke, Konfusionsmatrix, ECE der p_gt,
Kosten/Kacheln. Ausgabe outputs/eval/brand_voll_eval.json + docs/pilot.md Ergaenzung.
"""
from __future__ import annotations
import collections, json
from pathlib import Path

ROOT = Path("/home/iiot/data/jev-analysis/brand-experiment")
RUN = ROOT / "outputs/runs/brand_voll.jsonl"
OUT = ROOT / "outputs/eval/brand_voll_eval.json"


def ece(pairs, bins=10):
    if not pairs:
        return None
    tot = len(pairs); acc = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        sel = [(p, y) for p, y in pairs if lo <= p < hi or (b == bins - 1 and p == 1.0)]
        if not sel:
            continue
        acc += len(sel) / tot * abs(sum(p for p, _ in sel) / len(sel)
                                    - sum(y for _, y in sel) / len(sel))
    return acc


def main() -> int:
    gt = {json.loads(l)["image_id"]: json.loads(l)["marke_gt"]
          for l in (ROOT / "data/testset_100.jsonl").read_text().splitlines()}
    rows = [json.loads(l) for l in RUN.read_text().splitlines()]
    by_img: dict[str, list[dict]] = collections.defaultdict(list)
    for r in rows:
        by_img[r["image_id"]].append(r)

    bilder = []
    for iid, ents in by_img.items():
        gt_marke = gt[iid]
        stimmen = [e["choice"] for e in ents]
        z = collections.Counter(stimmen)
        any_choice = gt_marke if gt_marke in stimmen else stimmen[0]
        any_richtig = gt_marke in stimmen
        mehrheit, n = z.most_common(1)[0]
        p_sums: dict[str, float] = collections.defaultdict(float)
        for e in ents:
            for opt, p in (e.get("top3") or []):
                p_sums[opt] += p or 0.0
        mittel = {k: v / len(ents) for k, v in p_sums.items()}
        mittel_best = max(mittel, key=mittel.get) if mittel else None
        p_gt_liste = [e["p_gt"] for e in ents if e.get("p_gt") is not None]
        bilder.append({"image_id": iid, "gt": gt_marke, "n_gruppen": len(ents),
                       "stimmen": stimmen, "any_richtig": any_richtig,
                       "any_choice": any_choice, "mehrheit": mehrheit,
                       "mehrheit_richtig": mehrheit == gt_marke,
                       "uneins": len(z) > 1,
                       "mittel_p_best": mittel_best,
                       "mittel_p_richtig": mittel_best == gt_marke,
                       "p_gt_max": max(p_gt_liste) if p_gt_liste else None,
                       "p_gt_mean": sum(p_gt_liste) / len(p_gt_liste) if p_gt_liste else None,
                       "kosten": sum(e.get("input_tokens", 0) for e in ents) / 1e6 * 0.042})

    def acc_block(key):
        tp = sum(1 for b in bilder if b[key])
        return {"n": len(bilder), "richtig": tp, "acc": round(tp / len(bilder), 4) if bilder else None}

    je_marke = {}
    for m in sorted({b["gt"] for b in bilder}):
        sel = [b for b in bilder if b["gt"] == m]
        je_marke[m] = {"n": len(sel),
                       "any": round(sum(b["any_richtig"] for b in sel) / len(sel), 3),
                       "mehrheit": round(sum(b["mehrheit_richtig"] for b in sel) / len(sel), 3),
                       "mittel_p": round(sum(b["mittel_p_richtig"] for b in sel) / len(sel), 3),
                       "uneins": sum(b["uneins"] for b in sel)}
    verw = collections.Counter((b["gt"], b["any_choice"]) for b in bilder if not b["any_richtig"])
    pairs = [(b["p_gt_mean"], 1) for b in bilder if b["any_richtig"] and b["p_gt_mean"] is not None]
    pairs += [(b["p_gt_mean"], 0) for b in bilder if not b["any_richtig"] and b["p_gt_mean"] is not None]
    out = {"uebersicht": {"any_tile": acc_block("any_richtig"),
                          "mehrheit": acc_block("mehrheit_richtig"),
                          "mittel_p": acc_block("mittel_p_richtig"),
                          "uneins_anteil": round(sum(b["uneins"] for b in bilder) / len(bilder), 3),
                          "ece_p_gt_mean": round(ece(pairs), 4) if pairs else None,
                          "kachelgruppen": len(rows),
                          "kosten_usd": round(sum(b["kosten"] for b in bilder), 4)},
           "je_marke": je_marke,
           "verwechslungen_any": [{"gt": g, "stattdessen": s, "n": n} for (g, s), n in verw.most_common(15)],
           "einzeln": sorted(bilder, key=lambda b: b["image_id"])}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({"uebersicht": out["uebersicht"], "je_marke": je_marke,
                      "verwechslungen": out["verwechslungen_any"][:8]}, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
