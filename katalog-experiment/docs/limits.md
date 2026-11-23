# Gemessene Jev-API-Grenzen (Sonden 03, 03b–03e)

Alle Zahlen aus eigenen Requests am 22.11.2026, Modell `jev-1.14.0`,
Rohdaten in `outputs/runs/probe*.json`.

## 1. Request-Limit (Input-Token)

Ein Request über ~32k Input-Token scheitert:

- 1 Kachel (1568×1551) + 5 Fragen = **32.086 Token → OK**
- 1 Kachel (1568×1551) + 20 Fragen → **HTTP 400 `max_tokens_exceeded`**
- 19 Kacheln + 10 Fragen → HTTP 413 „Request exceeds size limits"
- 18/14/10 Kacheln (je 1568×1000) + 1 Frage → HTTP 400 `max_tokens_exceeded`
- 6 Kacheln (je 1568×1000) + 1 Frage = 24.621 Token → OK

→ Arbeitsgrenze: **~24k Input-Token pro Request**. Der Runner setzt die
Blockgröße entsprechend automatisch (Ziel < 24k).

## 2. Bilder pro Request

**Maximal 6 Bilder pro Request.** Ab 7 Bildern antwortet die API mit
`400 Invalid image request` — unabhängig von der Bildgröße (7/8/9 winzige
Kacheln à 300×280 scheitern genauso wie große).

## 3. Kritisch: das Bild wird PRO FRAGE berechnet

| Request | Input-Token |
|---|---|
| 1 Kachel, 1 Frage | 6.665 |
| 1 Kachel, 5 Fragen | 32.086 |
| 1 winzige Kachel (300×280), 30 Fragen | 9.760 |

Token ≈ Fragen × Kachelfläche. Bündeln vieler Fragen in einen Request spart
**keine** Bildkosten, nur HTTP-Roundtrips. Konsequenz: die Kosten hängen fast
ausschließlich am Produkt **Fragen × Fläche**, nicht an der Request-Struktur.

Gemessene Rate: 6.665 Token für 2,43 Mpx ≈ **2.743 Token/Mpx**;
Preis 0,042 USD/Mtok (Preisliste) → **0,115 USD/Mpx**.

## 4. Fragen-Overhead

Der Text einer Frage (Instructions + zwei Criteria) kostet ~300 Token,
davon nur ~25 eigene Zeichen — der Rest ist Format-Overhead.
`criteria` können auf `{"yes":"y","no":"n"}` verkürzt werden (gültig, getestet);
Frage-Keys `yes`/`no` sind Pflicht, sonst `400 Invalid image request`.
Criteria-Werte müssen sich pro Frage unterscheiden (Jev dedupliziert sonst).

## 5. Kostenzwang durch das Bildformat

Weil die Kosten pro (Frage × Fläche) laufen und die Kachelfläche durch
AR ≤ 2,5 und Höhe ≤ 1568 gedeckelt ist, ist der Vollauf über alle 824 Items
teuer. Projektion (`scripts/05_cost_model.py`, 557 Bilder):

- 824 Items, Überlappung 0,5: ~$470
- 824 Items, Überlappung 0,25: ~$317
- 250 Items (≥3 Vorkommen), Überlappung 0,25: ~$96
- 111 Items (alle Positiven + 100 Zufallsnegative je Bild), Überlappung 0,25: ~$43

Aktuelles Restbudget des Test-Keys: ~4,6 von 5 USD. Ein Vollauf mit allen 824
Items ist ohne Aufstockung nicht möglich.

## 6. Kachelgröße (Kostenhebel)

Höhe wird auf 627 px begrenzt (=1568/2,5, maximale Breite ausnutzbar), nie
unter 280 px. Flachere Streifen (VW, Höhe 278–600) bleiben nahezu nativ, hohe
Streifen (4W, Höhe 1436–1700) werden auf 0,36–0,44 skaliert.
Weitere Reduktion nur über (a) kleinere Höhe (Textverlust), (b) weniger
Überlappung (Text an Nähten), (c) weniger Items (GT-Abdeckung).
