#!/usr/bin/env python3
"""04 — Auswertung eines Laufs gegen den Ground-Truth.

Metriken (Konvention wie im Referenz-Evaluator: unbeantwortet/unparsbar = falsch):
Accuracy, Precision, Recall, F1, TN/FP/FN/TP, ECE (10 Bins über p_yes), plus
Zerlegungen nach Bildgruppe (VW/4W), Item-Häufigkeit, Item-Länge,
Ein-Zeichen-Items, Randfragmente und Boxbreite. Zusätzlich Rangliste der
häufigsten FP/FN-Items.

  python3 scripts/04_evaluate.py outputs/runs/pilot.jsonl
"""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path

ROOT = Path("/home/iiot/data/jev-analysis/katalog-experiment")


def ece(pairs: list[tuple[float, int]], bins: int = 10) -> float:
    if not pairs:
        return float("nan")
    total, acc = len(pairs), 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        sel = [(p, y) for p, y in pairs if (lo <= p < hi) or (b == bins - 1 and p == 1.0)]
        if not sel:
            continue
        conf = sum(p for p, _ in sel) / len(sel)
        hit = sum(y for _, y in sel) / len(sel)
        acc += len(sel) / total * abs(conf - hit)
    return acc


def block(rows: list[dict], label: str) -> dict:
    return _block(rows, label, "gt")


def _block(rows: list[dict], label: str, key: str) -> dict:
    tp = sum(1 for r in rows if r[key] and r["pred"])
    fp = sum(1 for r in rows if not r[key] and r["pred"])
    fn = sum(1 for r in rows if r[key] and not r["pred"])
    tn = sum(1 for r in rows if not r[key] and not r["pred"])
    n = len(rows)
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if prec == prec and rec == rec and (prec + rec) else float("nan")
    pairs = [(r["p_yes"], int(r[key])) for r in rows if r.get("p_yes") is not None]
    return {"slice": label, "n": n, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "acc": round((tp + tn) / n, 4) if n else None,
            "precision": round(prec, 4) if prec == prec else None,
            "recall": round(rec, 4) if rec == rec else None,
            "f1": round(f1, 4) if f1 == f1 else None,
            "ece": round(ece(pairs), 4) if pairs else None,
            "unanswered": sum(1 for r in rows if r["pred"] is None)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    gt = {json.loads(l)["image_id"]: json.loads(l)
          for l in (ROOT / "outputs/ground_truth.jsonl").read_text().splitlines()}
    catalog = [l for l in (ROOT / "outputs/catalog.txt").read_text().splitlines() if l.strip()]
    cat = json.loads((ROOT / "outputs/catalog.json").read_text())
    count = {c["item"]: c["count"] for c in cat["items"]}

    rows = []
    pooled: dict[tuple[str, str], dict] = {}
    for line in Path(args.run).read_text().splitlines():
        r = json.loads(line)
        if r["image_id"] not in gt:
            continue
        key = (r["image_id"], r["item"])
        pred = r.get("choice")
        pred = None if pred not in ("yes", "no") else (pred == "yes")
        p = r.get("p_yes")
        cur = pooled.get(key)
        if cur is None:
            pooled[key] = {"pred": pred, "p": p, "group": r["group"], "n": 1}
            continue
        cur["n"] += 1
        if pred is True:
            cur["pred"] = True
        elif cur["pred"] is None and pred is False:
            cur["pred"] = False
        if p is not None and (cur["p"] is None or p > cur["p"]):
            cur["p"] = p   # Max-Pooling über Kachelgruppen

    for (image_id, item), v in pooled.items():
        gt_items = gt[image_id]["items"]
        items = {i["item"]: i for i in gt_items}
        g = items.get(item)
        # loose GT: Item steckt in einem GT-String, ein GT-String steckt im Item,
        # oder (casefold-gleich) — bildet Fragment-Items (z.B. "ELIN" in "MICHELIN") fair ab
        low = item.casefold()
        loose = g is not None or any(
            (low in i["norm"] and len(low) >= 2) or (i["norm"] in low and len(i["norm"]) >= 2)
            for i in gt_items)
        rows.append({"image_id": image_id, "group": v["group"], "item": item,
                     "gt": g is not None, "gt_loose": loose, "pred": v["pred"], "p_yes": v["p"],
                     "n_requests": v["n"], "box_w": (g or {}).get("box_w"),
                     "edge": (g or {}).get("edge_fragment", False)})

    results = {"run": str(args.run), "overall": block(rows, "alle"),
               "overall_loose": _block(rows, "alle (containment-tolerantes GT)", "gt_loose"),
               "by_group": [block([r for r in rows if r["group"] == g], g) for g in ("VW", "4W")],
               "by_group_loose": [_block([r for r in rows if r["group"] == g], g, "gt_loose") for g in ("VW", "4W")],
               "by_item_len": [block([r for r in rows if (len(r["item"]) == 1) == (k == "1 Zeichen")],
                                     f"Länge {k}") for k in ("1 Zeichen", "mehr")],
               "by_freq": [], "by_edge": [block([r for r in rows if r["edge"]], "Randfragment (pos)"),
                                          block([r for r in rows if not r["edge"]], "kein Rand")]}
    for lo, hi, lab in ((1, 10, "1-10 Bilder"), (11, 50, "11-50"), (51, 10**9, ">50 Bilder (item präsent)")):
        results["by_freq"].append(block([r for r in rows if lo <= count.get(r["item"], 0) <= hi], lab))

    fp = collections.Counter(r["item"] for r in rows if r["pred"] and not r["gt"])
    fn = collections.Counter(r["item"] for r in rows if r["gt"] and r["pred"] is False)
    per_item = []
    for item in catalog:
        sel = [r for r in rows if r["item"] == item]
        if not sel:
            continue
        b = block(sel, item)
        b["gt_count"] = count.get(item, 0)
        per_item.append(b)
    per_item.sort(key=lambda b: (b["acc"] if b["acc"] is not None else 1.0))

    out = {"meta": {"run": args.run, "questions_answerable": len(rows),
                    "catalog": len(catalog), "images": len({r['image_id'] for r in rows})},
           "results": results,
           "top_fp": fp.most_common(25), "top_fn": fn.most_common(25),
           "worst_items": per_item[:25], "best_items": per_item[-10:][::-1],
           "rows": len(rows)}
    dst = Path(args.out) if args.out else ROOT / "outputs/eval" / (Path(args.run).stem + "_eval.json")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    o = results["overall"]
    print(json.dumps({"n": o["n"], "acc": o["acc"], "precision": o["precision"],
                      "recall": o["recall"], "f1": o["f1"], "ece": o["ece"],
                      "by_group": results["by_group"], "out": str(dst)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
