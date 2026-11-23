# Hauptlauf: Markenerkennung über das 100er-Test-Set

Stand 23.11.2026, Endauswertung nach Sichtprüfung. Alle 100 Bilder des
Test-Sets wurden mit der Frageform aus dem Pilotlauf abgefragt: eine
Multiple-Choice-Frage über die 14 Marken des Subsets plus die Option „KEINE
MARKE LESBAR", einmal je Kachelgruppe. Der Lauf kostete 0,111 USD (kumuliert
mit Pilot und Katalog-Experiment 0,117 USD), er umfasst 332 Kachelgruppen mit
1.583 Kacheln und lief in rund zwei Minuten.

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
Sollwert dieser Bilder ist daher korrigiert; die Klasse „Ohne erkennbare
Marke" existiert im Test-Set nicht mehr.

## Ergebnis

Über alle 100 Bilder:

| Regel | Richtig | Accuracy |
|---|---|---|
| any-tile | 92 | 0,920 |
| **Mittel-wahrscheinlichkeit (Leitmetrik)** | **91** | **0,910** |
| Mehrheit | 86 | 0,860 |

Je Marke, Leitmetrik (n ≥ 4): Bridgestone 33/33, Continental 23/24, Michelin
10/10, Pirelli 9/9, Dunlop 4/4, Hankook 4/4. Alle Ein-Bild-Marken (Falken,
Firestone, Fulda, Kleber, Kumho, Nokian, Semperit, Vredestein) wurden korrekt
erkannt; die Mehrheitsregel wäre bei Nokian gescheitert, die Mittel-Regel
nicht.

Die neun Fehler verteilen sich so: acht auf die Goodyear-Bilder, die mit
anderen Marken beantwortet wurden (Dunlop 3×, Firestone 2×, Continental 2×,
Nokian 1×), und einen auf ein Continental-Bild, dessen Gruppen uneins waren.
Für die Goodyear-Fälle gilt eine wichtige Einschränkung: **Goodyear stand in
der Optionsliste nicht zur Auswahl** — die Optionsliste stammt aus den
annotierten Marken des Subsets, und Goodyear ist dort nie als solches
annotiert. Jev konnte die richtige Antwort also nicht geben; die acht Bilder
messen die Zuordnungsfähigkeit nur unter unvollständiger Optionsmenge. Damit
ist die messbare Aussage: Auf 92 Bildern mit einer der 14 angebotenen Marken
liegt die Leitmetrik bei 91 von 92 richtig (0,989); die Goodyear-Bilder sind
ein separater Befund über Optionslisten-Abdeckung, nicht über
Erkennungsfehler.

## Einordnung

Drei Punkte prägen die Interpretation. Erstens erkennt Jev die Marke auf
Reifen, deren Marke in der Optionsliste steht, nahezu fehlerfrei: 91 von 92
unter der Leitmetrik, 92 von 92 unter any-tile. Zweitens sind die
Goodyear-Fälle strukturiert: Jev wählt dort andere Marken mit niedrigen
Wahrscheinlichkeiten und nennt in jeder Kachelgruppe mindestens einmal „KEINE
MARKE LESBAR" unter die Top-3 — das Bild einer unvollständigen Optionsmenge,
nicht das eines Verwechslungsfehlers. Drittens ist die Kalibrierung mäßig
(ECE 0,169 über die mittlere Sollklassen-Wahrscheinlichkeit), die harten
Entscheidungen sind aber nahezu durchweg richtig.

## Nächste Schritte (Vorschläge)

1. Goodyear in die Optionsliste aufnehmen und die acht Bilder erneut abfragen
   (Kosten: unter 0,01 USD), um die Optionslisten-Abdeckung zu prüfen.
2. Den Abdeckungsansatz verallgemeinern: Markenliste aus den Labels des
   Gesamtbestands statt nur des Subsets, damit seltenere Hersteller abgedeckt
   sind.
3. Bericht, Abstract und Präsentation des Brand-Experiments in der Art des
   Katalog-Experiments aufsetzen, auf Basis dieser Zahlen.

Rohdaten: `outputs/runs/brand_voll.jsonl` (332 Zeilen), Auswertung:
`outputs/eval/brand_voll_eval.json`, korrigierter Sollwert:
`data/sichtpruefung_ohne_marke.jsonl`.
