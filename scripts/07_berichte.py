#!/usr/bin/env python3
"""07 — Diagramme und Excel-Kostentabelle aus outputs/kosten_daten.json.

Reproduzierbar; keine API-Aufrufe. Ausgabe nach docs/charts/ und outputs/token_kosten.xlsx.
Die HTML-Präsentation baut 08_deck_html.py aus diesen Diagrammen.
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter

ROOT = Path("/home/iiot/data/jev-analysis")
CHARTS = ROOT / "docs/charts"
DATA = json.loads((ROOT / "outputs/kosten_daten.json").read_text(encoding="utf-8"))

GRUEN, ROT, BLAU, GRAU = "#2e7d32", "#c62828", "#1565c0", "#607d8b"
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": .3,
                     "figure.facecolor": "white", "axes.edgecolor": "#444"})

PROJEKTION = {824: (555, 277), 250: (168, 84), 170: (114, 57), 111: (75, 37)}


def chart_limits() -> Path:
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ok = [r for r in DATA["sonden"] if r["ok"]]
    bad = [r for r in DATA["sonden"] if not r["ok"]]
    ax.scatter([r["kacheln"] for r in ok], [r["input_token"] for r in ok], s=45,
               color=GRUEN, label="Request angenommen", zorder=3)
    ax.scatter([r["kacheln"] for r in bad], [30000] * len(bad), s=45, marker="x",
               color=ROT, label="abgelehnt (im Bild auf 30k gesetzt)", zorder=3)
    ax.axhline(24000, color=BLAU, ls="--", lw=1.4)
    ax.text(0.3, 24600, "Arbeitsgrenze des Runners (24.000 Token)", color=BLAU, fontsize=9)
    ax.axhline(32000, color=ROT, ls=":", lw=1.4)
    ax.text(0.3, 32600, "gemessene Obergrenze (~32.000 Token)", color=ROT, fontsize=9)
    ax.set_xlabel("Bilder (Kacheln) im Request")
    ax.set_ylabel("Input-Token des Requests")
    ax.set_title("Request-Grenzen: Bilderzahl und Tokenvolumen")
    ax.set_xlim(0, 20)
    ax.legend(loc="lower right", fontsize=8)
    p = CHARTS / "grenzen_request.png"; fig.tight_layout(); fig.savefig(p, dpi=150); plt.close(fig)
    return p


def chart_per_question() -> Path:
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    pts = [(r["fragen"], r["input_token"]) for r in DATA["sonden"]
           if r["kacheln"] == 1 and r["input_token"] and r["fragen"] >= 5]
    pts.append((1, 6665))
    pts.sort()
    ax.plot([p[0] for p in pts], [p[1] for p in pts], "o-", color=ROT, lw=1.6)
    ax.set_xlabel("Fragen in EINEM Request (gleiches Bild)")
    ax.set_ylabel("Input-Token")
    ax.set_title("Jev rechnet das Bild pro Frage ab\n(1 Kachel: 6.665 Token/Frage, linear)")
    ax.set_ylim(0, 12500)
    ax.annotate("Bündeln spart keine Bildkosten,\nnur HTTP-Aufrufe", xy=(22, 7300),
                xytext=(6, 10500), fontsize=9, color="#333",
                arrowprops={"arrowstyle": "->", "color": "#555"})
    p = CHARTS / "bild_pro_frage.png"; fig.tight_layout(); fig.savefig(p, dpi=150); plt.close(fig)
    return p


def chart_per_image() -> Path:
    gruppen = {"VW": [], "4W": []}
    for r in DATA["lauf_bildkosten"]:
        gruppen[r["gruppe"]].append(r["usd"])
    labels = ["VW\n(250 Items)", "4W\n(250 Items)", "VW\n(824 Items)", "4W\n(824 Items)"]
    werte = [sum(gruppen["VW"][3:]) / 3, sum(gruppen["4W"][:12]) / 12,
             gruppen["VW"][1], gruppen["4W"][0]]
    farben = [BLAU, GRAU, BLAU, GRAU]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    bars = ax.bar(labels, werte, color=farben)
    for b, v in zip(bars, werte):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.008, f"{v:.3f} $", ha="center", fontsize=9)
    ax.set_ylabel("USD je Bild")
    ax.set_title("Gemessene Kosten je Bild\n(VW-Streifen brauchen ~33 Kacheln, 4W nur 7)")
    p = CHARTS / "kosten_je_bild.png"; fig.tight_layout(); fig.savefig(p, dpi=150); plt.close(fig)
    return p


def chart_projection() -> Path:
    items = [824, 250, 170, 111]
    alt = [PROJEKTION[i][0] for i in items]
    neu = [PROJEKTION[i][1] for i in items]
    x = range(len(items))
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.bar([i - 0.2 for i in x], alt, 0.4, color=ROT,
           label="Blockgröße des Messlaufs (zu klein, teuer)")
    ax.bar([i + 0.2 for i in x], neu, 0.4, color=GRUEN, label="korrigierte Blockgröße")
    for i, (a, n) in enumerate(zip(alt, neu)):
        ax.text(i - 0.2, a + 8, f"{a} $", ha="center", fontsize=8)
        ax.text(i + 0.2, n + 8, f"{n} $", ha="center", fontsize=8)
    rest = float(DATA["budget"]["rest_usd"])
    ax.axhline(rest, color=BLAU, ls="--", lw=1.3,
               label=f"Restbudget Test-Key ({rest:.2f} $)".replace(".", ","))
    ax.set_ylim(0, max(alt) * 1.18)
    ax.set_xticks(list(x)); ax.set_xticklabels([f"{i} Items" for i in items])
    ax.set_ylabel("USD für alle 557 Bilder")
    ax.set_title("Projektion Vollauf nach Kataloggröße")
    ax.legend(fontsize=8, loc="upper right")
    p = CHARTS / "projektion_vollauf.png"; fig.tight_layout(); fig.savefig(p, dpi=150); plt.close(fig)
    return p


def chart_results() -> Path:
    daten = {"exakt": {"P": 0.361, "R": 0.947, "F1": 0.522},
             "containment-tolerant": {"P": 0.698, "R": 0.825, "F1": 0.756}}
    metriken = ["P", "R", "F1"]
    x = range(len(metriken))
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.bar([i - 0.2 for i in x], [daten["exakt"][m] for m in metriken], 0.4, color=ROT,
           label="exaktes GT")
    ax.bar([i + 0.2 for i in x], [daten["containment-tolerant"][m] for m in metriken], 0.4,
           color=GRUEN, label="containment-tolerantes GT")
    for i, m in enumerate(metriken):
        ax.text(i - 0.2, daten["exakt"][m] + .015, f"{daten['exakt'][m]:.2f}", ha="center", fontsize=8)
        ax.text(i + 0.2, daten["containment-tolerant"][m] + .015,
                f"{daten['containment-tolerant'][m]:.2f}", ha="center", fontsize=8)
    ax.set_xticks(list(x)); ax.set_xticklabels(metriken)
    ax.set_ylim(0, 1.05); ax.set_ylabel("Wert")
    ax.set_title("Messlauf, 15 Bilder / 250 Items: Metriken\nunter zwei GT-Konventionen", pad=26)
    ax.legend(fontsize=9, loc="lower center", bbox_to_anchor=(0.5, -0.28), ncol=2, frameon=False)
    p = CHARTS / "ergebnis_metriken.png"; fig.tight_layout(); fig.savefig(p, dpi=150); plt.close(fig)
    return p


def chart_tiles() -> Path:
    """Breite Montage: ganzer Streifen oben, drei Kacheln mit Versatz darunter."""
    from PIL import Image, ImageDraw
    iid = "418185599_HR"
    d = ROOT / "outputs/tiles" / iid
    meta = json.loads((d / "tiles.json").read_text())
    breite = 1560
    with Image.open(meta["src"]) as src:
        strip = src.convert("RGB")
        strip = strip.resize((breite, max(1, int(strip.height * breite / strip.width))))
    th = 300
    tiles = []
    for t in meta["tiles"][:3]:
        with Image.open(d / t["file"]) as im:
            tiles.append(im.convert("RGB").resize((int(th * 2.5), th)))
    pad, kopf = 6, 26
    hoehe = kopf + strip.height + pad + kopf + th + pad
    c = Image.new("RGB", (breite + 2 * pad, hoehe), (240, 237, 229))
    dr = ImageDraw.Draw(c)
    dr.text((pad, 6), f"Original: {meta['src_w']} x {meta['src_h']} px — Seitenverhaeltnis "
                      f"{meta['src_w']/meta['src_h']:.0f} (Jev erlaubt 2,5)", fill=(60, 60, 60))
    c.paste(strip, (pad, kopf))
    y = kopf + strip.height + pad
    dr.text((pad, y - 18), "drei von %d Kacheln (50 %% Ueberlappung, Hoehe auf 627 px begrenzt)"
            % meta["n_tiles"], fill=(60, 60, 60))
    x = pad
    for t, im in zip(meta["tiles"][:3], tiles):
        c.paste(im, (x, y + 18)); x += im.width + pad
    dst = CHARTS / "kachelung.jpg"
    c.save(dst, "JPEG", quality=90)
    return dst


def build_xlsx() -> Path:
    wb = Workbook()
    kopf = Font(bold=True, color="FFFFFF")
    fkopf = PatternFill("solid", fgColor="1F3864")
    wst = PatternFill("solid", fgColor="FCE4D6")

    def tab(ws, kopfzeile, zeilen, breiten):
        ws.append(kopfzeile)
        for c in ws[1]:
            c.font, c.fill, c.alignment = kopf, fkopf, Alignment(horizontal="center", wrap_text=True)
        for z in zeilen:
            ws.append(z)
        for i, b in enumerate(breiten, 1):
            ws.column_dimensions[get_column_letter(i)].width = b
        ws.freeze_panes = "A2"

    ws = wb.active; ws.title = "Messungen"
    zeilen = [[r["quelle"], r["kacheln"], r["fragen"], r["input_token"], r["usd"],
               r["usd_je_frage"], r["usd_je_kachel"], "ja" if r["ok"] else "nein", r["fehler"]]
              for r in DATA["sonden"]]
    tab(ws, ["Quelle", "Kacheln", "Fragen", "Input-Token", "USD", "USD/Frage", "USD/Kachel",
             "angenommen", "Fehler"], zeilen, [14, 9, 9, 13, 11, 11, 11, 12, 34])
    for z in ws.iter_rows(min_row=2, min_col=5, max_col=7):
        for c in z:
            c.number_format = "0.000000"

    ws = wb.create_sheet("Kosten je Bild")
    zeilen = [[r["lauf"], r["gruppe"], r["bild"], r["items"], r["antworten"], r["usd"]]
              for r in DATA["lauf_bildkosten"]]
    tab(ws, ["Lauf", "Gruppe", "Bild", "Items", "Antworten", "USD"], zeilen, [14, 8, 16, 8, 11, 11])
    ws.append([])
    ws.append(["Summe", "", "", "", "", round(sum(r["usd"] for r in DATA["lauf_bildkosten"]), 4)])
    ws.cell(ws.max_row, 6).font = Font(bold=True)
    ws.cell(ws.max_row, 1).font = Font(bold=True)
    for c in ws[ws.max_row]:
        c.fill = wst
    n = ws.max_row
    ws.cell(n + 1, 1, "Mittel VW (250 Items)"); ws.cell(n + 1, 6, 0.3999)
    ws.cell(n + 2, 1, "Mittel 4W (250 Items)"); ws.cell(n + 2, 6, 0.1968)
    ws.cell(n + 4, 1, "Hochrechnung 557 Bilder, 250 Items (alte Blockgröße)")
    ws.cell(n + 4, 6, 168.3).font = Font(bold=True)
    ws.cell(n + 5, 1, "dito, korrigierte Blockgröße (55 Kachel-Frage-Paare/Request)")
    ws.cell(n + 5, 6, 84.2).font = Font(bold=True)

    ws = wb.create_sheet("Projektion")
    tab(ws, ["Items im Katalog", "USD Vollauf, alte Blockgröße", "USD Vollauf, korrigiert"],
        [[k, v[0], v[1]] for k, v in PROJEKTION.items()], [18, 26, 24])
    ch = BarChart(); ch.title = "Projektion Vollauf (557 Bilder)"; ch.y_axis.title = "USD"
    ch.add_data(Reference(ws, min_col=2, max_col=3, min_row=1, max_row=5), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=2, max_row=5))
    ws.add_chart(ch, "E2")

    ws = wb.create_sheet("Budget")
    tab(ws, ["Position", "USD"], [
        ["Test-Key-Budget", DATA["budget"]["limit_usd"]],
        ["verbraucht (Stand 22.11.2026)", DATA["budget"]["verbraucht_usd"]],
        ["Rest", DATA["budget"]["rest_usd"]],
        ["Kosten Sonden (Grenzmessung)", round(sum(r["usd"] or 0 for r in DATA["sonden"]), 4)],
        ["Kosten Pilot (2 Bilder, 824 Items)", 0.7084],
        ["Kosten Messlauf (15 Bilder, 250 Items)", 3.5609]], [34, 12])
    for r in range(2, ws.max_row + 1):
        ws.cell(r, 2).number_format = "0.0000"

    ws = wb.create_sheet("Ableitung")
    tab(ws, ["Größe", "Wert", "Quelle / Bedeutung"], [
        ["Preis", 0.042, "USD je 1 Mio Input-Token (Preisliste TypeSafe)"],
        ["Token je Mpx Bildfläche", 2743, "gemessen: 6.665 Token für 1.568×1.551 px"],
        ["Kosten je Mpx", 0.0001152, "Preis × Token/Mpx"],
        ["Stützpunkt 1", 6665, "1 Kachel + 1 Frage"],
        ["Stützpunkt 2", 32086, "1 Kachel + 5 Fragen"],
        ["Stützpunkt 3", 24621, "6 Kacheln + 1 Frage (gerade noch zulässig)"],
        ["Arbeitsgrenze Request", 24000, "Zielwert des Runners, darunter bleiben"],
        ["harte Obergrenze Request", 32000, "ab hier HTTP 400 max_tokens_exceeded"],
        ["max. Bilder je Request", 6, "ab 7 HTTP 400 Invalid image request"],
        ["Referenz: VW-Kachel", "700×280 px", "≈ 0,0002 USD je Frage"],
        ["Referenz: 4W-Kachel", "1568×627 px", "≈ 0,0008 USD je Frage"]],
        [26, 14, 46])

    p = ROOT / "outputs/token_kosten.xlsx"
    wb.save(p)
    return p


def main() -> int:
    CHARTS.mkdir(parents=True, exist_ok=True)
    charts = {"limits": chart_limits(), "per_q": chart_per_question(),
              "per_image": chart_per_image(), "projection": chart_projection(),
              "results": chart_results(), "tiles": chart_tiles()}
    print(json.dumps({"charts": [str(p) for p in charts.values()]}, indent=1))
    print("xlsx:", build_xlsx())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
