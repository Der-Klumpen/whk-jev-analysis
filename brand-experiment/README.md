# Brand-Experiment: Markenerkennung auf Reifenpanoramen (Jev 1.14)

**Status: Hauptlauf gelaufen.** Das Test-Set (100 Bilder) ist vollständig
abgefragt; die Auswertung steht, zwei Klärungen sind offen (Sichtprüfung der
Klasse „Ohne erkennbare Marke", Wahl der Leitmetrik). Ziel ist die Messung, ob
Jev die Marke eines Reifens richtig erkennt.

## Frage

Erkennt Jev 1.14 die **Marke** eines Reifens? Gegenstand sind die
Reifenmarken aus den Labels des Subsets (BRIDGESTONE, MICHELIN, Continental,
Dunlop, …) — nicht beliebige Textstrings wie im Katalog-Experiment.

## Stand und nächste Schritte

Das Test-Set (`data/testset_100.jsonl`) umfasst 100 Bilder: alle 14 Marken mit
mindestens einem Bild, verteilt nach Bestandsanteil, plus acht Bilder der
Klasse „Ohne erkennbare Marke". Der Hauptlauf (`docs/hauptlauf.md`) fragte
alle Bilder ab (332 Kachelgruppen, 0,111 USD): Auf den 92 klar markierten
Bildern erkennt Jev die Marke nach any-tile in 100 Prozent der Fälle, nach
Mittel-wahrscheinlichkeit in 98,9 Prozent; alle Verwechslungen entfallen auf
die Klasse „Ohne erkennbare Marke".

Zwei Klärungen sind offen: die Sichtprüfung der acht Bilder ohne annotierte
Marke (Vorlage in `outputs/sichtpruefung_ohne_marke/`, Eintragung in
`data/sichtpruefung_ohne_marke.jsonl`) und die Wahl der Leitmetrik in
`docs/auswertungsregeln.md` (Abschnitt Entscheidung). Restbudget des
Testschlüssels: etwa 4,88 USD.

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
