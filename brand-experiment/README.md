# Brand-Experiment: Markenerkennung auf Reifenpanoramen (Jev 1.14)

**Status: Pilot gelaufen.** Das Test-Set steht (100 Bilder), der Pilotlauf mit
fünf Bildern ist abgeschlossen. Ziel ist die Messung, ob Jev die Marke eines
Reifens richtig erkennt; die Trennung vom Katalog-Experiment hält Dokumente und
Auswertungen übersichtlich.

## Frage

Erkennt Jev 1.14 die **Marke** eines Reifens? Gegenstand sind die
Reifenmarken aus den Labels des Subsets (BRIDGESTONE, MICHELIN, Continental,
Dunlop, …) — nicht beliebige Textstrings wie im Katalog-Experiment.

## Stand und nächste Schritte

Das Test-Set (`data/testset_100.jsonl`) umfasst 100 Bilder: alle 14 Marken mit
mindestens einem Bild, verteilt nach Bestandsanteil, plus acht Bilder der
Klasse „Ohne erkennbare Marke". Der Pilotlauf (`docs/pilot.md`) hat die
Frageform bestätigt: Jev wählt die Marke direkt aus der Optionsliste, vier von
vier klar markierten Bildern werden richtig erkannt, Kosten 0,0053 USD für
fünf Bilder.

Vor dem Hauptlauf über alle 100 Bilder sind zwei Entscheidungen offen: die
Behandlung der Klasse „Ohne erkennbare Marke" (Sichtprüfung der acht
Test-Set-Bilder empfohlen, weil dort Goodyear-Produktnamen ohne
Herstellername annotiert sind) und die Auswertungsregel für den Fall, dass
Kachelgruppen unterschiedlich entscheiden. Restbudget des Testschlüssels:
etwa 4,69 USD.

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
