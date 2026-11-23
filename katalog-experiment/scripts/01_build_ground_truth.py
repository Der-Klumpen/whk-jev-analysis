#!/usr/bin/env python3
"""01 — Ground-Truth pro Bild + Item-Katalog aus den Labels.

Quellen (nur lesend):
  VW: labels/<stem>.txt Zeile i  ↔  OCR_images/<stem>_bbox_i.jpg  ↔
      Transkription in VW/OCR_annotations-cleaned_v01.json
 4W: labels/<stem>.txt Zeile i  ↔  4W_annotations.xml Box i; GT-Text =
      Content-Attribut (nur Text_Area-Boxen mit nicht-leerem Content)

Zeilen ohne Transkription/Content tragen kein Item (VW: von der Bereinigung
entfernte leere Boxen; 4W: Pfeil-Symbole Alpine/Rotation/OEM_Q).

GT-Definition: Ein Item gilt für ein Bild als vorhanden, wenn mindestens eine
Box des Bildes exakt diesen Text trägt. Vergleich casefold + Whitespace-normiert.
Das ist bewusst ANNOTATIONS-basiert: nicht annotierter Text auf dem Reifen kann
zusätzlich sichtbar sein (FP-Quelle, siehe docs/design.md).

Ausgabe:
  outputs/ground_truth.jsonl   {"image_id","group","width","height","items":[...]}
  outputs/catalog.json         {"items":[{item,norm,count,n_images,aliases}],...}
  outputs/catalog.txt          Item-Liste, eins pro Zeile (für Fragen-Generierung)
"""
from __future__ import annotations
import collections, json, re, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path("/home/iiot/data/jev-analysis/katalog-experiment")
OCR = Path("/home/iiot/data/OCR")
GT_OUT = ROOT / "outputs/ground_truth.jsonl"
CAT_JSON = ROOT / "outputs/catalog.json"
CAT_TXT = ROOT / "outputs/catalog.txt"

WS = re.compile(r"\s+")


def norm(s: str) -> str:
    return WS.sub(" ", s.strip()).casefold()


def box_from_poly(vals: list[float], w: int, h: int) -> list[int]:
    xs, ys = vals[0::2], vals[1::2]
    return [int(round(min(xs) * w)), int(round(min(ys) * h)),
            int(round(max(xs) * w)), int(round(max(ys) * h))]


def vw_texts() -> dict[str, dict[int, str]]:
    data = json.loads((OCR / "VW/OCR_annotations-cleaned_v01.json").read_text())
    out: dict[str, dict[int, str]] = collections.defaultdict(dict)
    for it in data:
        name = Path(it["file_path"]).name
        if "_bbox_" not in name:
            continue
        stem, idx = name.rsplit("_bbox_", 1)
        idx = int(idx.split(".")[0])
        text = WS.sub(" ", (it["transcription"] or "").strip())
        if text:
            out[stem][idx] = text
    return out


def w4_texts() -> dict[str, dict[int, str]]:
    root = ET.parse(OCR / "4W/4W_annotations.xml").getroot()
    out: dict[str, dict[int, str]] = collections.defaultdict(dict)
    for im in root.findall("image"):
        for i, box in enumerate(im.findall("box")):
            content = None
            for attr in box.findall("attribute"):
                if attr.get("name") == "Content":
                    content = WS.sub(" ", (attr.text or "").strip())
            if content:
                out[Path(im.get("name")).stem][i] = content  # Key = image_id (ohne Endung)
    return out


def main() -> int:
    rows = [json.loads(l) for l in (ROOT / "data/subset_resolved.jsonl").read_text().splitlines()]
    texts = {"VW": vw_texts(), "4W": w4_texts()}

    gt_rows, edge_flags = [], 0
    for r in rows:
        stem, group, w, h = r["image_id"], r["group"], r["width"], r["height"]
        by_idx = texts[group].get(stem, {})
        label_file = OCR / group / "labels" / (stem + ".txt")
        polys = [list(map(float, l.split())) for l in label_file.read_text().splitlines() if l.strip()]
        items = []
        for i, text in sorted(by_idx.items()):
            if i >= len(polys):
                continue
            box = box_from_poly(polys[i][1:], w, h)
            # Fragment am Bildrand: Text berührt den linken/rechten Rand
            edge = box[0] <= 2 or box[2] >= w - 2
            edge_flags += edge
            items.append({"item": text, "norm": norm(text), "row": i,
                          "box": box, "box_w": box[2] - box[0], "box_h": box[3] - box[1],
                          "edge_fragment": edge})
        gt_rows.append({"image_id": stem, "group": group, "width": w, "height": h,
                        "n_items": len(items), "items": items})

    # Katalog: casefold-dedupliziert, häufigste Schreibweise als Item, Rest Aliase
    spellings: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    img_count: dict[str, set] = collections.defaultdict(set)
    for row in gt_rows:
        for it in row["items"]:
            spellings[it["norm"]][it["item"]] += 1
            img_count[it["norm"]].add(row["image_id"])
    catalog = []
    for n, cnt in spellings.items():
        main_spelling = cnt.most_common(1)[0][0]
        catalog.append({"item": main_spelling, "norm": n, "count": sum(cnt.values()),
                        "n_images": len(img_count[n]),
                        "aliases": sorted(a for a in cnt if a != main_spelling)})
    catalog.sort(key=lambda c: (-c["count"], c["norm"]))

    GT_OUT.parent.mkdir(parents=True, exist_ok=True)
    with GT_OUT.open("w") as f:
        for row in gt_rows:
            f.write(json.dumps(row) + "\n")
    CAT_JSON.write_text(json.dumps({
        "source": "union of ground-truth items over data/subset_all_test.txt",
        "n_items": len(catalog),
        "n_images_without_items": sum(1 for r in gt_rows if r["n_items"] == 0),
        "casefold_alias_groups": sum(1 for c in catalog if c["aliases"]),
        "items": catalog}, indent=1, ensure_ascii=False) + "\n")
    CAT_TXT.write_text("\n".join(c["item"] for c in catalog) + "\n")

    inst = sum(r["n_items"] for r in gt_rows)
    single = sum(1 for r in gt_rows for it in r["items"] if len(it["item"]) == 1)
    print(json.dumps({
        "images": len(gt_rows), "gt_instances": inst, "catalog_items": len(catalog),
        "images_without_items": sum(1 for r in gt_rows if r["n_items"] == 0),
        "single_char_instances": single, "edge_fragment_instances": edge_flags,
        "questions_full_run": len(gt_rows) * len(catalog),
        "top10": [c["item"] for c in catalog[:10]]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
