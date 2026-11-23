# Hauptlauf: Markenerkennung über das 100er-Test-Set

Stand 23.11.2026, Endauswertung nach Sichtprüfung und Nachlauf. Alle 100 Bilder
des Test-Sets wurden mit der Frageform aus dem Pilotlauf abgefragt: eine
Multiple-Choice-Frage über die Marken des Subsets plus die Option „KEINE MARKE
LESBAR", einmal je Kachelgruppe. Der Hauptlauf kostete 0,111 USD (332
Kachelgruppen, 1.583 Kacheln, rund zwei Minuten), der Nachlauf der acht
Goodyear-Bilder mit erweiterter Optionsliste weitere 0,012 USD; kumuliert mit
Pilot und Katalog-Experiment 0,129 USD.

## Leitmetrik

Als Leitmetrik dient die **Mittel-wahrscheinlichkeit**: Für jede Option wird
die mittlere Wahrscheinlichkeit über alle Kachelgruppen eines Bildes gebildet,
das Bild erhält die Option mit dem höchsten Mittelwert. any-tile und Mehrheit
bleiben als Vergleichsspalten mitgeführt; die Begründung steht in
`docs/auswertungsregeln.md`.

## Sollwert nach Sichtprüfung

Die acht Bilder der Klasse „Ohne erkennbare Marke" wurden per Sichtprüfung
geklärt: **In allen acht Fällen ist eine Marke erkennbar, in allen acht Fällen
Goodyear** — teils nur schwer (die Bemerkungen nennen Licht, Skalierung und
geringen Kontrast als Gründe), aber eindeutig genug für eine Zuordnung. Der
Sollwert dieser Bilder ist korrigiert; die Klasse „Ohne erkennbare Marke"
existiert im Test-Set nicht mehr.

## Nachlauf: Optionsabdeckung geprüft

Im Hauptlauf stand Goodyear in der Optionsliste nicht zur Wahl — die Liste
stammte aus den annotierten Marken des Subsets, und Goodyear ist dort nie als
solches annotiert. Jev konnte die richtige Antwort auf den acht Goodyear-Bildern
also nicht geben. Um die Abdeckung zu prüfen, wurden genau diese acht Bilder
mit **identischem Aufbau, aber 15 Marken plus Leerroption** erneut abfragt
(`outputs/runs/brand_goodyear8.jsonl`, 0,012 USD).

Das Ergebnis bestätigt die Analyse: Jev erkennt Goodyear, sobald es wählbar
ist. any-tile liefert 8/8, Mittel-wahrscheinlichkeit 7/8, Mehrheit 7/8. Der
einzige Mittel-w-Fehler ist ein Bild, dessen Kachelgruppen zwischen
`Continental` und `Goodyear` schwanken — dasselbe Bild, das im Hauptlauf
bereits uneins war. Die mittlere Sollklassen-Wahrscheinlichkeit liegt auf
sieben Bildern zwischen 0,35 und 1,00 und damit deutlich über den
Verwechslungsniveaus des Hauptlaufs.

## Ergebnis über alle 100 Bilder

Hauptlauf für die 92 Bilder mit angebotener Marke, Nachlauf für die acht
Goodyear-Bilder — jede Kachelgruppe je Bild genau einmal gewertet:

| Regel | Richtig | Accuracy |
|---|---|---|
| any-tile | 100 | **1,000** |
| **Mittel-wahrscheinlichkeit (Leitmetrik)** | **98** | **0,980** |
| Mehrheit | 93 | 0,930 |

Je Marke, Leitmetrik: Bridgestone 33/33, Continental 23/24, Michelin 10/10,
Pirelli 9/9, Goodyear 7/8, Dunlop 4/4, Hankook 4/4, alle Ein-Bild-Marken
korrekt. Mit vollständiger Optionsliste erkennt Jev die Marke also auf 98 von
100 Bildern richtig; die zwei Fehler sind Bilder mit uneinigen Kachelgruppen
(Continental 1×, Goodyear 1×), keine Verwechslungen mit systematischer
Richtung.

## Einordnung

Drei Punkte prägen die Interpretation. Erstens erkennt Jev die Marke auf
Reifen mit abgedeckter Optionsliste nahezu fehlerfrei — 98 von 100 unter der
Leitmetrik, 100 von 100 unter any-tile. Zweitens ist der wichtigste
Nebenbefund des Experiments die **Abhängigkeit von der Optionsliste**: Eine
Marke, die im Fragekatalog fehlt, ist für ein Choice-Modell unerkennbar, und
die Fehler landen nicht zufällig, sondern als Streuung über andere Marken mit
niedrigen Wahrscheinlichkeiten. Drittens ist die Kalibrierung mäßig (ECE
0,169 im Hauptlauf), die harten Entscheidungen sind aber nahezu durchweg
richtig.

## Nächste Schritte (Vorschläge)

1. Den Abdeckungsansatz verallgemeinern: Markenliste aus den Labels des
   Gesamtbestands statt nur des Subsets, damit seltenere Hersteller abgedeckt
   sind; das würde den Nachlauf-Trick überflüssig machen.
2. Bericht, Abstract und Präsentation des Brand-Experiments in der Art des
   Katalog-Experiments aufsetzen, auf Basis dieser Zahlen.

Rohdaten: `outputs/runs/brand_voll.jsonl` (332 Zeilen, 92 Bilder gewertet),
`outputs/runs/brand_goodyear8.jsonl` (18 Zeilen, 8 Bilder), korrigierter
Sollwert: `data/sichtpruefung_ohne_marke.jsonl`.
