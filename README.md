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

## Pipeline

```bash
python3 scripts/00_resolve_subset.py
python3 scripts/01_build_ground_truth.py
python3 scripts/02_make_tiles.py --limit 20 --preview
python3 scripts/03_jev_item_existence.py --limit-images 8 --questions-per-request 200
python3 scripts/04_evaluate.py outputs/runs/<run>.jsonl
```

Key: `~/TypeSafe-Keys/Jev-Test-Key.txt`. Budget-Wache im Runner (Abbruch bei
konfigurierbarer Kumul-Grenze). Keine Boxen/Markierungen in den Kacheln.
