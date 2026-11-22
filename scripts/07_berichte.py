#!/usr/bin/env python3
"""07 — Diagramme, Excel-Kostentabelle und Präsentation aus outputs/kosten_daten.json.

Reproduzierbar; keine API-Aufrufe. Ausgabe nach docs/charts/, outputs/token_kosten.xlsx,
docs/praesentation.pptx.
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
from pptx import Presentation
from pptx.util import Inches, Pt

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
    ax.set_title("Messlauf, 15 Bilder / 250 Items: Metriken\nunter zwei GT-Konventionen")
    ax.legend(fontsize=8)
    p = CHARTS / "ergebnis_metriken.png"; fig.tight_layout(); fig.savefig(p, dpi=150); plt.close(fig)
    return p


def chart_tiles() -> Path:
    """Vorschau-Montage des Kachel-Verfahrens (aus 02_make_tiles.py --preview)."""
    import shutil
    src = ROOT / "outputs/previews/tiles_preview.jpg"
    dst = CHARTS / "kachelung.jpg"
    if src.exists():
        shutil.copyfile(src, dst)
        return dst
    return src


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


def build_pptx(charts: dict[str, Path]) -> Path:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    titel_layout, content_layout = prs.slide_layouts[0], prs.slide_layouts[1]

    def bullet_slide(titel: str, punkte: list[str]) -> None:
        s = prs.slides.add_slide(content_layout)
        s.shapes.title.text = titel
        tf = s.placeholders[1].text_frame
        tf.text = punkte[0]
        for p in punkte[1:]:
            tf.add_paragraph().text = p
        for p in tf.paragraphs:
            p.font.size = Pt(17)

    def bild_slide(titel: str, pfad: Path, unterzeile: str = "") -> None:
        s = prs.slides.add_slide(prs.slide_layouts[5])
        s.shapes.title.text = titel
        s.shapes.title.top = Inches(0.3)
        s.shapes.add_picture(str(pfad), Inches(1.5), Inches(1.4), height=Inches(5.2))
        if unterzeile:
            tb = s.shapes.add_textbox(Inches(1.5), Inches(6.7), Inches(10), Inches(0.6))
            tb.text_frame.text = unterzeile
            tb.text_frame.paragraphs[0].font.size = Pt(13)
            tb.text_frame.paragraphs[0].font.italic = True

    s = prs.slides.add_slide(titel_layout)
    s.shapes.title.text = "Jev-Item-Existenz auf Reifenpanoramen"
    s.placeholders[1].text = ("Experiment, Anpassungen, Kosten\nTestset VW/4W · Jev 1.14 (API) · 22.11.2026")

    bullet_slide("Idee des Experiments", [
        "Jedes Bild des Testsubsets wird zu jedem Katalog-Item einzeln gefragt:",
        "„Is the exact text `X` readable on the tire?“ — Antwort nur yes/no, englisch",
        "Katalog aus den Labels abgeleitet: 824 Items über 557 Bilder",
        "Ground Truth ebenfalls aus den Labels, Antworten je Bild × Item gespeichert",
        "Auswertung: Vergleich Antwort gegen GT, Accuracy/Precision/Recall/F1/ECE",
    ])

    bullet_slide("Datenlage und zwei Probleme", [
        "Panoramen: bis 17.906 × 278 px, Seitenverhältnis bis 45",
        "Jev erlaubt nur 280–1568 px je Seite und Seitenverhältnis ≤ 2,5",
        "→ ein Bild passt nie in einen Request, Kachelung ist erzwungen",
        "Labels enthalten Fragmente (`ICHELIN`, `6`) — exakter GT-Vergleich bestraft korrekte Antworten",
        "Gegenmittel: containment-tolerantes GT als zweite, faire Metrik",
    ])

    bild_slide("Anpassung 1: Kachelung", charts["tiles"],
               "Höhe auf 627 px begrenzt, Breite 2,5×Höhe, 50 % Überlappung, Offsets protokolliert")

    bild_slide("Anpassung 2: Request-Grenzen", charts["limits"],
               "Ab ~32.000 Token und ab 7 Bildern lehnt die API ab → Kachelgruppen ≤ 6, Blockgröße adaptiv")

    bild_slide("Befund: Bild wird pro Frage abgerechnet", charts["per_q"],
               "Kosten hängen an Fragen × Bildfläche — Bündeln spart nur HTTP-Aufrufe")

    bild_slide("Anpassung 3: Blockgröße und Pooling", charts["per_image"],
               "Erst zu klein geschätzt (Q≈3, teuer), dann skalenfrei auf 55 Kachel-Frage-Paare korrigiert")

    bild_slide("Kosten", charts["projection"],
               "Gemessen: 4W 0,197 USD/Bild, VW 0,400 USD/Bild bei 250 Items · Budget 5 USD, verbraucht 4,30 USD")

    bild_slide("Ergebnis Messlauf (15 Bilder, 250 Items)", charts["results"],
               "Recall hoch, Precision durch Fragmente und nicht annotierten Text gedrückt")

    bullet_slide("Grenzen und offene Entscheidungen", [
        "Ein-Zeichen-Items unbrauchbar: `5`, `6`, `55`, `60` → Acc 0,067, immer ja",
        "Lange Strings sind die echte Schwäche (`PILOT ALPIN 5`, `PIRELLI`)",
        "Offen: Budget-Scope (824/250/170/111 Items), Metrik-Konvention, Pooling-Schwelle",
        "Ohne Aufstockung kein Vollauf: kleinster sinnvoller Scope ≈ 75 USD",
    ])

    p = ROOT / "docs/praesentation.pptx"
    prs.save(p)
    return p


def main() -> int:
    CHARTS.mkdir(parents=True, exist_ok=True)
    charts = {"limits": chart_limits(), "per_q": chart_per_question(),
              "per_image": chart_per_image(), "projection": chart_projection(),
              "results": chart_results(), "tiles": chart_tiles()}
    print(json.dumps({"charts": [str(p) for p in charts.values()]}, indent=1))
    print("xlsx:", build_xlsx())
    print("pptx:", build_pptx(charts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
