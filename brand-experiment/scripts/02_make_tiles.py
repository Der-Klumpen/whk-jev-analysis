#!/usr/bin/env python3
"""02 — Jev-konforme Kacheln aus den Panoramastreifen.

Regeln (aus references/sordi_datasets.md, hier für Ganzbild-Item-Existenz
angepasst):
 - Jev erzwingt 280–1568 px je Seite und AR ≤ 2,5 → Streifen (AR bis 45)
   werden gekachelt, nie gepolstert.
 - Höhe wird BEHALTEN (kein Höhenverlust), nur auf HEIGHT_CAP skaliert, wenn
   `--height-cap` gesetzt ist (Standard: aus).
 - Kachelbreite = min(1568, Höhe×2,5); Schrittweite = Breite×(1-OVERLAP) →
   Text an Kachelnähten liegt vollständig in der Nachbarkachel.
 - Mindesthöhe 280 px wird per Upscale nur dann erzwungen, wenn die Höhe sonst
   unter dem Jev-Limit läge (bei VW-Streifen 278–300 px möglich).
 - Keine Markierungen in den Kacheln.

Ausgabe: outputs/tiles/<image_id>/tile_000.jpg ... + outputs/tiles/<image_id>/tiles.json
Metadaten je Kachel: Offset im Original (für Box-/Item-Zuordnung in der Analyse).
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from PIL import Image

ROOT = Path("/home/iiot/data/jev-analysis/brand-experiment")
TILE_DIR = ROOT / "outputs/tiles"
MIN_SIDE, MAX_SIDE, MAX_AR = 280, 1568, 2.5
TARGET_MAX_H = 627          # 1568/2.5 — höchste Höhe, bei der die Kachel volle Breite hat
OVERLAP = 0.5
QUALITY = 90


def tile_plan(w: int, h: int, overlap: float) -> tuple[int, int, int]:
    """(scale, kachelbreite, schrittweite) für ein Bild.

    Zielhöhe: so nah an TARGET_MAX_H wie möglich, aber nie unter MIN_SIDE
    (Jev-Untergrenze) — Höhe wird also tendenziell reduziert, nie gepolstert.
    """
    th = min(TARGET_MAX_H, max(MIN_SIDE, h))
    scale = th / h
    if scale > 1.0:  # sehr flache Streifen (< 280 px) müssen hochskaliert werden
        scale = MIN_SIDE / h
        th = MIN_SIDE
    tw = min(MAX_SIDE, int(round(th * MAX_AR)))
    stride = max(1, int(round(tw * (1 - overlap))))
    return scale, tw, stride


def make_tiles(path: Path, out_dir: Path, overlap: float = OVERLAP) -> dict:
    with Image.open(path) as im:
        im = im.convert("RGB")
        w, h = im.size
        scale, tw, stride = tile_plan(w, h, overlap)
        if scale != 1.0:
            nw, nh = int(round(w * scale)), int(round(h * scale))
            im = im.resize((nw, nh), Image.LANCZOS)
            w, h = im.size
        out_dir.mkdir(parents=True, exist_ok=True)
        tiles, left = [], 0
        while True:
            right = min(w, left + tw)
            left = max(0, right - tw)  # letzte Kachel bündig
            fn = out_dir / f"tile_{len(tiles):03d}.jpg"
            im.crop((left, 0, right, h)).save(fn, "JPEG", quality=QUALITY)
            tiles.append({"idx": len(tiles), "file": fn.name,
                          "x0": left, "x1": right, "y0": 0, "y1": h,
                          "w": right - left, "h": h})
            if right >= w:
                break
            left += stride
        meta = {"image_id": path.stem, "src": str(path), "src_w": im.size[0],
                "src_h": h, "scale": round(scale, 4), "n_tiles": len(tiles),
                "overlap": overlap, "tiles": tiles}
        (out_dir / "tiles.json").write_text(json.dumps(meta, indent=1) + "\n")
        return meta


def preview(image_ids: list[str], out: Path, max_w: int = 1400) -> None:
    """Montage: Original oben, darunter die Kacheln mit Versatz-Markierung."""
    parts = []
    for iid in image_ids:
        d = TILE_DIR / iid
        if not d.exists():
            continue
        meta = json.loads((d / "tiles.json").read_text())
        with Image.open(meta["src"]) as src:
            strip = src.convert("RGB")
            factor = max_w / strip.width
            strip = strip.resize((max_w, max(1, int(strip.height * factor))), Image.LANCZOS)
        parts.append(("orig", f"{iid} — {meta['src_w']}x{meta['src_h']} / {meta['n_tiles']} tiles", strip))
        for t in meta["tiles"][:6]:
            with Image.open(d / t["file"]) as tim:
                th = max(1, int(tim.height * min(1.0, 700 / max(1, tim.width))))
                parts.append(("tile", f"tile {t['idx']} x0={t['x0']} {t['w']}x{t['h']}",
                              tim.convert("RGB").resize((700, th), Image.LANCZOS)))
    if not parts:
        return
    from PIL import ImageDraw
    pad, label_h = 8, 14
    height = sum(p[2].height + label_h + pad for p in parts) + pad
    canvas = Image.new("RGB", (max_w + 2 * pad, height), (25, 25, 25))
    draw = ImageDraw.Draw(canvas)
    y = pad
    for _, label, img in parts:
        draw.text((pad, y), label, fill=(220, 220, 120))
        y += label_h
        canvas.paste(img, (pad, y))
        y += img.height + pad
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, "JPEG", quality=88)
    print(f"preview: {out}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="nur die ersten N Bilder")
    ap.add_argument("--only", nargs="*", default=None, help="explizite image_ids")
    ap.add_argument("--overlap", type=float, default=OVERLAP)
    ap.add_argument("--height-cap", type=int, default=0, help="Höhe auf N px begrenzen")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--preview-images", type=int, default=2)
    args = ap.parse_args()

    rows = [json.loads(l) for l in (ROOT / "data/subset_resolved.jsonl").read_text().splitlines()]
    if args.only:
        want = set(args.only)
        rows = [r for r in rows if r["image_id"] in want]
    if args.limit:
        rows = rows[:args.limit]
    total_tiles = 0
    for r in rows:
        p = Path(r["path"])
        d = TILE_DIR / r["image_id"]
        if (d / "tiles.json").exists():
            total_tiles += json.loads((d / "tiles.json").read_text())["n_tiles"]
            continue
        if args.height_cap:
            global MAX_SIDE
            with Image.open(p) as chk:
                scale = min(1.0, args.height_cap / chk.height)
            tmp = d.parent / f".tmp_{r['image_id']}.jpg"
            with Image.open(p) as src:
                im = src.convert("RGB")
                im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
            d.mkdir(parents=True, exist_ok=True)
            tmp2 = d / "_src_scaled.jpg"
            im.save(tmp2, "JPEG", quality=QUALITY)
            meta = make_tiles(tmp2, d, args.overlap)
            meta["src"] = str(p)
            meta["src_w_orig"] = r["width"]
            meta["src_h_orig"] = r["height"]
            (d / "tiles.json").write_text(json.dumps(meta, indent=1) + "\n")
            tmp2.unlink(missing_ok=True)
            tmp.unlink(missing_ok=True)
        else:
            meta = make_tiles(p, d, args.overlap)
        total_tiles += meta["n_tiles"]
    print(json.dumps({"images": len(rows), "tiles": total_tiles}, indent=2))
    if args.preview:
        preview([r["image_id"] for r in rows[:args.preview_images]], ROOT / "outputs/previews/tiles_preview.jpg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
