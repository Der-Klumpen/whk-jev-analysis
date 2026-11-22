# jev-analysis — Item-Existenz auf Reifenpanoramen (Jev 1.14)

Experiment: Für jedes Bild des Subsets `all_test.txt` wird Jev 1.14 (API) **jedes
Item des Katalogs** als eigene Ja/Nein-Frage gestellt („Ist `X` auf dem Reifen zu
lesen?"). Antworten werden pro Bild × Item gegen den aus den Labels abgeleiteten
Ground-Truth ausgewertet.

## Aufbau

```
data/subset_all_test.txt        Kopie der Subset-Definition (557 Zeilen, unverändert)
data/subset_resolved.jsonl      Subset aufgelöste Pfade (image_id, group, Pfad, W, H)
outputs/ground_truth.jsonl      GT pro Bild: Items laut Labels (+ Box-Metadaten)
outputs/catalog.json            Katalog: eindeutige Items + Häufigkeit + Aliase
outputs/tiles/                  Jev-konforme Kacheln (nicht im Repo)
outputs/runs/                   Antwort-JSONL je Lauf (Resume-fähig)
outputs/eval/                   Auswertung
scripts/                        Pipeline (numeriert, in Reihenfolge)
docs/                           Design, Datenlage, Befunde
prompts/                        Prompt-/Criteria-Vorlagen
```

## Datenherkunft (nur lesend, nichts wird verändert)

Quelle: `/home/iiot/data/OCR/{VW,4W}/{images,labels}` + Annotationen.

- Subset: `/home/iiot/data/OCR/all_test.txt`, 557 Bilder (289 VW, 268 4W), alle lokal vorhanden.
- Label-Datei = Bildname + `.txt`; Zeile *i* ist Box *i* (Polygon, normiert, eine Klasse).
- Box *i* ↔ Crop `<stem>_bbox_i.jpg` ↔ Transkription: bei VW aus
  `VW/OCR_annotations-cleaned_v01.json`, bei 4W aus dem `Content`-Attribut der
  Text_Area-Box in `4W_annotations.xml`.
  Alignment geprüft: Crop-Maße == Polygon-Maße (Verhältnis 1,00 über Stichproben).

## Bildformat-Problem

Die Panoramen sind bis 17.906 × 278 px (AR bis 45). Jev erzwingt 280–1568 px je
Seite und AR ≤ 2,5 → ein Bild passt nie in einen Request. Lösung: Kachelung,
Details in `docs/design.md`.

## Dokumente

- `docs/dokumentation.md` — Bericht über Aufbau, Kachelung, Request-Mechanik,
  Ablauf, Ergebnisse, Kosten + Fachwortverzeichnis
- `docs/abstract.md` — Abstract (eine Seite)
- `docs/praesentation.pptx` — Kurzpräsentation (Idee, Anpassungen, Kosten)
- `outputs/token_kosten.xlsx` — Token-/Kostenaufstellung, Projektion, Budget
- `docs/charts/` — Diagramme der Präsentation und des Berichts
- technische Einzeldokumente: `docs/design.md`, `docs/limits.md`,
  `docs/pilot.md`, `docs/run24.md`

## Pipeline

```bash
python3 scripts/00_resolve_subset.py
python3 scripts/01_build_ground_truth.py
python3 scripts/06_select_run_sets.py            # Item-Teilkatalog + Bildstichprobe
python3 scripts/02_make_tiles.py --only $(cat data/run_set_24.txt)
python3 scripts/03_jev_item_existence.py --run messlauf --items outputs/catalog_top250.txt \
        --only-images $(cat data/run_set_24.txt) --questions-per-request 0
python3 scripts/04_evaluate.py outputs/runs/messlauf.jsonl
python3 scripts/05_cost_model.py                  # Projektion Vollauf
```

Sonden (Grenzen/Kosten): `scripts/03b_probe_limits.py` … `03e_probe_minimal.py`.
Befunde dazu in `docs/limits.md`.

## Stand

- Subset/GT/Katalog/Kachelung/Runner/Auswertung fertig und gelaufen.
- Pilot (2 Bilder, voller Katalog): docs/pilot.md. Kosten 0,71 USD.
- Messlauf (15 Bilder, 250 Items, budget-gedeckelt): docs/run24.md.
  Exakt P 0,36 / R 0,95; containment-tolerant P 0,70 / R 0,83 / Acc 0,96.
- Jev rechnet das Bild **pro Frage** → voller Katalog über 557 Bilder ≈ 180-280 USD
  (je nach Blockgroesse), Katalog mit 250 Items ≈ 80-170 USD (docs/limits.md, docs/run24.md).
- Befund: Ein-Zeichen-Items (`5`, `6`, `55`, `60`) sind mit dieser Frageform
  unbrauchbar (Acc 0,067) — aus dem Katalog nehmen oder Sonderregel.
- Offene Nutzerentscheidungen: Budget-Scope, Metrik-Konvention (exakt vs.
  containment-tolerant), Pooling-Schwelle. Voreinstellungen: beide Metriken,
  any-tile-Pooling + Sensitivitätsauswertung.
- Restbudget des Test-Keys nach den Läufen: ~0,70 von 5,00 USD.

Key: `~/TypeSafe-Keys/Jev-Test-Key.txt`. Budget-Wache im Runner (Abbruch bei
konfigurierbarer Kumul-Grenze). Keine Boxen/Markierungen in den Kacheln.
