# Brand-Experiment: Markenerkennung auf Reifenpanoramen (Jev 1.14)

**Status: Planung.** Noch nichts gelaufen; dieser Ordner enthält Struktur und
Plan. Ziel ist die Trennung vom Katalog-Experiment (Item-Existenz), damit
Dokumente und Auswertungen übersichtlich bleiben.

## Frage

Erkennt Jev 1.14 die **Marke** eines Reifens? Gegenstand sind die
Reifenmarken aus den Labels des Subsets (BRIDGESTONE, MICHELIN, Continental,
Dunlop, …) — nicht beliebige Textstrings wie im Katalog-Experiment.

## Offene Design-Entscheidungen (Nutzer)

1. **Frageform** — Kandidaten:
   - Brand-Existenz: „Is the tire brand `X` present on the tire?" je Marke
     Ja/Nein (analog Katalog-Experiment, Vergleichbarkeit hoch)
   - Brand-Choice: Marke aus Kandidatenliste + `none_of_the_above` wählen
     (billiger, aber anderes Messobjekt)
   - Freie Antwort (offenes Modell), bewertet per Namensmatch
2. **Marken-Katalog** — welche Strings zählen als Marke? Vorschlag: manuelle
   Liste (Marke + gängige Schreibvarianten), abgeglichen mit den Labels; nicht
   der ganze 824er-Katalog.
3. **Scope** — voller Subset (557 Bilder) oder Stichprobe; Budget auf dem
   Test-Key ist knapp (~0,70 USD Rest).
4. **Pooling-Schwelle und Metrik** — Voreinstellung aus dem Katalog-Experiment
   übernehmen (any-tile + Sensitivität, exakt + containment-tolerant).

## Geplanter Aufbau (an das Katalog-Experiment angelehnt)

```
data/          subset-Kopie, Markenliste, Resolved-Dateien
scripts/       numerierte Pipeline (Auflösung, Marken-GT, Kachelung, Runner, Auswertung)
outputs/       GT, Kacheln, Läufe, Auswertung (nicht versioniert: tiles, runs)
docs/          design, limits (Verweis auf Katalog-Experiment), Befunde
```

Wiederverwendbar aus dem Katalog-Experiment: Subset-Auflösung, Kachelung,
Runner (Budget-Wache, adaptive Blockgröße), Evaluator, Kostenmodell. Die
Skripte werden kopiert und auf Marken angepasst, nicht importiert — jedes
Experiment bleibt in sich verständlich.

## Abgrenzung zum Katalog-Experiment

| | Katalog-Experiment | Brand-Experiment |
|---|---|---|
| Frage | „Ist Text `X` lesbar?" (824 Items) | „Ist Marke `X` vorhanden?" (Markenliste) |
| GT | annotierte Textstrings | Marke(n) je Bild laut Labels |
| Kein Interesse an | Position, Anzahl | Nicht-Marken-Text (DOT, M+S, …) |

## Nächste Schritte

1. Markenliste aus den Labels ableiten (Häufigkeit, Schreibvarianten) und mit
   Nutzer abstimmen
2. Frageform festlegen (oben 1.)
3. Kostenprojektion mit dem Kachel-/Fragenmodell des Katalog-Experiments
4. Kleinlauf (3–5 Bilder) vor jedem größeren Lauf
