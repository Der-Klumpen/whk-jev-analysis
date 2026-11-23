#!/usr/bin/env python3
"""09 — Excel-Kostentabelle des Brand-Experiments (Laufebene, aus outputs/kosten_daten.json)."""
from __future__ import annotations
import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter

ROOT = Path("/home/iiot/data/jev-analysis/brand-experiment")
DATA = json.loads((ROOT / "outputs/kosten_daten.json").read_text(encoding="utf-8"))

wb = Workbook()
kopf = Font(bold=True, color="FFFFFF")
fkopf = PatternFill("solid", fgColor="1F3864")
wst = PatternFill("solid", fgColor="FCE4D6")

ws = wb.active; ws.title = "Läufe"
kopfzeile = ["Lauf", "Kachelgruppen", "Bilder", "Input-Token", "USD", "Notiz"]
ws.append(kopfzeile)
for c in ws[1]:
    c.font, c.fill, c.alignment = kopf, fkopf, Alignment(horizontal="center", wrap_text=True)
for l in DATA["laeufe"]:
    ws.append([l["lauf"], l["kachelgruppen"], l["bilder"], l["input_token"], l["usd"], l["notiz"]])
ws.append(["Summe", sum(l["kachelgruppen"] for l in DATA["laeufe"]),
           100, sum(l["input_token"] for l in DATA["laeufe"]), DATA["summe_usd"], ""])
for c in ws[ws.max_row]:
    c.fill = wst; c.font = Font(bold=True)
for i, b in enumerate([44, 15, 9, 14, 11, 60], 1):
    ws.column_dimensions[get_column_letter(i)].width = b
for r in range(2, ws.max_row + 1):
    ws.cell(r, 5).number_format = "0.0000"
ch = BarChart(); ch.title = "Kosten je Lauf (USD)"; ch.y_axis.title = "USD"
ch.add_data(Reference(ws, min_col=5, min_row=1, max_row=ws.max_row - 1), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=2, max_row=ws.max_row - 1))
ws.add_chart(ch, "H2")

ws = wb.create_sheet("Token je Kachelgruppe")
ws.append(["Lauf", "Ø Input-Token je Kachelgruppe", "Ø USD je Bild"])
r_i = 2
for l in DATA["laeufe"]:
    tok_kg = l["input_token"] / l["kachelgruppen"]
    usd_bild = l["usd"] / l["bilder"]
    ws.append([l["lauf"], round(tok_kg), round(usd_bild, 5)])
for i, b in enumerate([44, 30, 16], 1):
    ws.column_dimensions[get_column_letter(i)].width = b

ws = wb.create_sheet("Budget")
ws.append(["Position", "USD"])
for c in ws[1]:
    c.font, c.fill = kopf, fkopf
zeilen = [
    ["Katalog-Experiment gesamt (Pilot + Messlauf + Sonden)", 4.2997],
    ["Brand: Pilot", DATA["laeufe"][0]["usd"]],
    ["Brand: Hauptlauf", DATA["laeufe"][1]["usd"]],
    ["Brand: Nachlauf", DATA["laeufe"][2]["usd"]],
    ["Brand: Summe", DATA["summe_usd"]],
    ["Kumuliert über beide Experimente", round(4.2997 + DATA["summe_usd"], 4)],
    ["Test-Key-Budget", 5.0],
    ["Rest", round(5.0 - 4.2997 - DATA["summe_usd"], 4)],
]
for z in zeilen:
    ws.append(z)
ws.cell(ws.max_row, 2).font = Font(bold=True)
for r in range(2, ws.max_row + 1):
    ws.cell(r, 2).number_format = "0.0000"
ws.column_dimensions["A"].width = 52
ws.column_dimensions["B"].width = 12

p = ROOT / "outputs/token_kosten.xlsx"
wb.save(p)
print("xlsx:", p)
