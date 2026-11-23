# Messlauf 22.11.2026: 15 Bilder, 250-Item-Teilkatalog, 3.750 Bild-Item-Paare

Budget-gedeckelter Lauf bis zur Budget-Wache (4,30 von 5,00 USD verbraucht).
Startset waren 12 VW + 12 4W; fertig wurden 12 4W und 3 VW.

## Konfiguration

- Items: `outputs/catalog_top250.txt` (250 Items mit ≥3 Vorkommen, 90 % der
  GT-Instanzen des Subsets).
- Bilder: `data/run_set_24.txt` (äquidistant je Gruppe).
- Vorlage `long`, Pooling any-tile (Item = ja, wenn eine Kachelgruppe ja sagt).
- Achtung: In diesem Lauf war die Blockgröße zu klein geschätzt, der Runner
  hat Requests adaptiv halbiert (Q ≈ 3 statt ≈ 9). Die Requests sind dadurch
  überteuert; die Regel ist danach auf ein skalenfreies Maß
  (55 Kachel-Frage-Paare/Request) umgestellt. Der Lauf ist damit teurer als
  nötig, inhaltlich aber gültig.

## Kosten (gemessen, aus den Laufzeilen)

| Gruppe | Bilder | Kosten | je Bild |
|---|---|---|---|
| VW | 3 | 1,200 USD | 0,400 USD |
| 4W | 12 | 2,361 USD | 0,197 USD |

Hochrechnung 557 Bilder × 250 Items mit dieser (zu kleinen) Blockgröße:
**~168 USD**. Mit der korrigierten Blockgröße (55 Kachel-Frage-Paare/Request,
rund halb so viele Requests) etwa 80–90 USD; voller Katalog (824 Items)
entsprechend ~280 USD bei alter, ~180 USD bei korrigierter Blockgröße.

Zur Vorsicht bei Zwischenrechnungen: eine Zählung über eindeutige
Token-Signaturen untertreibt (4W 0,128 statt 0,197 USD/Bild), weil Requests mit
gleicher Kachelgruppe/Tokenzahl zu einer Signatur zusammenfallen. Belastbar sind
nur die Zeilensummen je Bild.

## Ergebnis

Exaktes GT:

| Slice | n | Acc | P | R | F1 | ECE |
|---|---|---|---|---|---|---|
| alle | 3750 | 0,940 | 0,361 | 0,947 | 0,522 | 0,107 |
| VW | 750 | 0,907 | 0,327 | 0,943 | 0,485 | 0,180 |
| 4W | 3000 | 0,948 | 0,375 | 0,948 | 0,537 | 0,089 |

Containment-tolerantes GT:

| Slice | n | Acc | P | R | F1 | ECE |
|---|---|---|---|---|---|---|
| alle | 3750 | 0,959 | 0,698 | 0,825 | 0,756 | 0,064 |
| VW | 750 | 0,944 | 0,654 | 0,904 | 0,759 | 0,129 |
| 4W | 3000 | 0,962 | 0,716 | 0,798 | 0,755 | 0,048 |

## Zerlegung (exaktes GT)

- **Ein-Zeichen-Items sind unbrauchbar:** n = 30, TP 0, FP 28, Acc 0,067,
  ECE 0,870. `5`, `6`, `55`, `60` werden praktisch immer mit ja beantwortet —
  sie stecken irgendwo im Reifenprofil (`ALPIN6`, `205/55R16`). Lösung: aus dem
  Katalog nehmen oder eigene Regel.
- Item-Häufigkeit: bei Items, die auf >50 Bildern vorkommen, Recall 0,985 /
  P 0,620; bei Items mit 1–10 Bildern P 0,137 / R 0,926. Seltene Items werden
  also fast immer bejaht (any-tile-Pooling über 7–33 Kacheln).
- Längere Strings sind das eigentliche Modellproblem (FN): `ContiWinterContact
  TS 800`, `TS 850 P`, `PILOT ALPIN 5`, `PIRELLI` — Recall dort niedriger,
  während Fragmente (`ntal`, `STONE`, `UTSIDE`) massenhaft ja bekommen.

## Einordnung

Die hohe FP-Zahl ist zwei Quellen zuzuschreiben, die nicht Modellversagen sind:
(1) Fragment-Items, deren Zeichenfolge in einem sichtbaren anderen Text steckt
(im loose-GT aufgelöst, P 0,36 → 0,70), (2) nicht annotierter, real sichtbarer
Reifentext. Für die Precision ist deshalb das containment-tolerante GT die
belastbarere Zahl; das exakte GT bleibt als strenge Untergrenze dokumentiert.

Rohdaten: `outputs/runs/run24_top250.jsonl` (9.250 Zeilen),
Auswertung: `outputs/eval/run24_top250_eval.json`.
