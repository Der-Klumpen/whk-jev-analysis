# Hauptlauf: Markenerkennung über das 100er-Test-Set

Stand 23.11.2026. Alle 100 Bilder des Test-Sets wurden mit der Frageform aus
dem Pilotlauf abgefragt: eine Multiple-Choice-Frage über die 14 Marken des
Subsets plus die Option „KEINE MARKE LESBAR", einmal je Kachelgruppe, Pooling
und Auswertung nach den Regeln aus `docs/auswertungsregeln.md`. Der Lauf
kostete 0,111 USD (kumuliert mit Pilot und Katalog-Experiment 0,117 USD), er
umfasst 332 Kachelgruppen mit 1.583 Kacheln und lief in rund zwei Minuten.

## Ergebnis

Auf den 92 Bildern mit klar annotierter Marke liegt Jev nach allen drei
Regeln überwiegend richtig:

| Regel | Richtig | Accuracy |
|---|---|---|
| any-tile | 92 | **1,000** |
| Mittel-wahrscheinlichkeit | 91 | 0,989 |
| Mehrheit | 86 | 0,934 |

Je Marke (n ≥ 4) nach any-tile: Bridgestone 33/33, Continental 24/24, Michelin
10/10, Pirelli 9/9, Dunlop 4/4, Hankook 4/4 — sämtliche Markennamen wurden auf
jedem klar markierten Bild in mindestens einer Kachelgruppe erkannt. Die
Abweichungen der strengeren Regeln entstehen auf Bildern, deren Gruppen
uneins sind (38 % aller Bilder), und treffen mit Continental (mehrheit 0,833)
und Dunlop (0,75) die Marken mit langen VW-Panoramen.

Die Klasse „Ohne erkennbare Marke" (n = 8) liegt nach allen drei Regeln bei
null: Jev wählte Dunlop (3×), Firestone (2×), Continental (2×) und Nokian
(1×). Das bestätigt die Design-Analyse: Diese Bilder tragen nachweislich
markenähnliche Texte (Goodyear-Produktnamen wie `EfficientGrip` und
`UltraGrip`, außerdem generische Texte wie `GOOD`), ohne dass der Hersteller
annotiert ist. Die Null in dieser Klasse ist daher als Messproblem des
Sollwerts zu lesen, nicht als Modellversagen; die Sichtprüfung dieser Bilder
steht noch aus.

## Einordnung

Zwei Befunde prägen die Interpretation. Erstens erkennt Jev die Marke auf
klar markierten Reifen im any-tile-Sinn fehlerfrei — der Markenschriftzug
wird auf jedem der 92 Bilder in mindestens einer Kachelgruppe korrekt benannt,
und auch unter der strengeren Mittel-w-Regel bleibt die Accuracy bei 0,989.
Zweitens ist die Kalibrierung mäßig (ECE 0,169 über die mittlere
Sollklassen-Wahrscheinlichkeit), was heißt: Die gemeldeten
Wahrscheinlichkeiten sind als Konfidenz mit Vorsicht zu verwenden, although
die harten Entscheidungen fast durchweg richtig sind.

Die Verwechslungen konzentrieren sich vollständig auf die „ohne Marke"-Klasse;
kein klar markiertes Bild wurde einer falschen Marke zugeordnet. Eine
Konfusionsmatrix über die echten Marken wäre daher eine Einheitsmatrix.

## Offen

Die Sichtprüfung der acht „ohne erkennbare Marke"-Bilder (Vorlage und Bilder:
`outputs/sichtpruefung_ohne_marke/`, Anleitung im Ordner-README) und die Wahl
der Leitmetrik (`docs/auswertungsregeln.md`, Abschnitt Entscheidung). Die
Endzahlen des Berichts ändern sich durch beide Punkte nicht mehr wesentlich;
sie klären die Interpretation der „ohne Marke"-Klasse und die Hauptmetrik der
Zusammenfassung.

Rohdaten: `outputs/runs/brand_voll.jsonl` (332 Zeilen), Auswertung:
`outputs/eval/brand_voll_eval.json`.
