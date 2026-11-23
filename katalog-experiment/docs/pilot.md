# Pilotlauf (22.11.2026): 2 Bilder, voller Katalog, 1.648 Fragen

Zweck: Ende-zu-Ende-Validierung (Kacheln → Requests → Antworten → Auswertung)
und Messung der echten Kosten pro Bild. Kein Ergebnisfund, nur Machbarkeit.

## Aufbau

- Bilder: `418185599_HR` (4W, 7 Kacheln à 1568×627) und
  `893c4666…QA0170090050_train` (VW, 33 Kacheln à 700×280).
- Voller Katalog (824 Items), Bild 1 in einem Request-Blockverfahren
  (kurze Vorlage), Bild 2 in Kachelgruppen à 6 (lange Vorlage). Beide
  Varianten sind im Antwort-Pooling identisch; Endgültig ist die
  Kachelgruppen-Variante.
- Pooling: Item = `yes`, wenn irgendeine Kachelgruppe `yes` sagt;
  `p_yes` = Maximum. 5.768 Rohzeilen → 1.648 Bild-Item-Paare.

## Kosten und Zeit (gemessen, nicht geschätzt)

- 4W-Bild: **0,094 USD**, 103 Requests.
- VW-Bild: **0,614 USD**, 4944 Antworten (6 Kachelgruppen), 35 s bei 6 Threads.
- Kumul im Pilot: 0,71 USD; Restbudget des Keys danach ~4,26 USD.
- Hochrechnung Vollauf (557 Bilder, 824 Items): 289 × 0,61 + 268 × 0,094
  ≈ **200 USD**, Laufzeit ≈ 5–6 h bei 6 Threads.
- Treiber: flache VW-Streifen brauchen ~33 Kacheln (Höhe 278–600 px, AR ~40),
  4W-Streifen nur 7 (Höhe wird auf 627 px skaliert).

## Ergebnis (2 Bilder, 824 Items × 2 = 1.648 Bild-Item-Paare)

Exakter GT-Vergleich (Item muss als eigener Label-String vorkommen):

| Slice | n | Acc | P | R | F1 | ECE |
|---|---|---|---|---|---|---|
| alle | 1648 | 0,942 | 0,139 | 0,636 | 0,228 | 0,103 |
| VW | 824 | 0,922 | 0,151 | 0,846 | 0,256 | 0,169 |
| 4W | 824 | 0,962 | 0,107 | 0,333 | 0,162 | 0,038 |

Containment-tolerantes GT (Item zählt als vorhanden, wenn es in einem
GT-String steckt oder einen enthält):

| Slice | n | Acc | P | R | F1 | ECE |
|---|---|---|---|---|---|---|
| alle | 1648 | 0,967 | 0,703 | 0,740 | 0,721 | 0,058 |
| VW | 824 | 0,961 | 0,712 | 0,825 | 0,765 | 0,108 |
| 4W | 824 | 0,972 | 0,679 | 0,576 | 0,623 | 0,019 |

## Befund: der Katalog enthält Fragmente

Häufigste FPs sind `ELIN` (2), `tal`, `215`, `EXTR`, `TUR`, `R16`, `60`,
`MICHE`, `CHELIN`, `ental` — also Teilstücke vorhandener Texte (MICHELIN,
Continental, 215/60R16). Beispiel: Reifen trägt `MICHELIN`, GT-String eines
anderen Bildes ist der Randabschnitt `ICHELIN`; die Frage „Ist `ELIN` zu
lesen?" ist sachlich **richtig** mit ja beantwortet, im exakten Vergleich aber
FP. Das drückt die Precision von 0,70 auf 0,14, ohne Modellfehler.

Ursachen: (a) Randfragmente aus dem Annotationsbestand (180 GT-Instanzen),
(b) Ein-Zeichen-Items (`6`, 113 Instanzen), (c) Item-Wiederholungen.

Entscheidung nötig (siehe Rückfrage): exakte Metrik führen, containment-tolerant
führen, oder Katalog bereinigen (Fragmente auf Trägerstring abbilden).

## Technische Befunde des Piloten

- 33 Kacheln in einem Request gehen nicht (nur ≤6, s. docs/limits.md).
- Fragenblöcke müssen aus dem Tokenbudget berechnet werden, nicht aus der
  Fragenzahl (Bild zählt pro Frage).
- Resume über `image_id` funktioniert; Abbruch/Neustart verliert nichts.
- Keine unbeantworteten Fragen, keine API-Fehler bei 6 Threads.
