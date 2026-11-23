# Abstract

**Experiment:** Item-Existenz mit Jev 1.14 auf entrollten Reifenwandaufnahmen
(Testsubset VW/4W, 557 Bilder). **Stand:** 22.11.2026, vorläufig, budget-gedeckelt.

## Frage

Kann ein kalibriertes Entscheidungsmodell (Jev 1.14, API) entscheiden, ob ein
konkreter, aus den Annotationen abgeleiteter Text auf einem Reifenpanorama zu
lesen ist? Das Testsubset `all_test.txt` (289 VW, 268 4W) und die Labels liefern
Fragekatalog und Sollwert; jedes Bild wird zu jedem Katalog-Item einzeln
gefragt („Is the exact text `X` readable on the tire?", Antwort `yes`/`no`,
englisch), bildweise und wiederaufsetzbar.

## Aufbau

Der Katalog ist rein datengetrieben: 6.803 Label-Instanzen, casefold-dedupliziert
824 Items. Der Ground Truth wird aus denselben Labels gebaut (Texte, Boxen,
Randmerker). Die Reihenfolge der Label-Zeilen ist an die OCR-Ausschnitte
gebunden und wurde über identische Pixelmaße geprüft. Ausgewertet wird streng
(exakter String) und containment-tolerant (Item zählt, wenn es in einem
GT-String steckt) — Letzteres, weil der Katalog Randfragmente wie `ICHELIN`
enthält und ein Ja auf `ELIN` bei sichtbarem `MICHELIN` sachlich richtig ist.

## Anpassungen

Das Bildformat erzwang Eingriffe: Panoramen bis 17.906 × 278 px (Seitenverhältnis
45) gegen Jev-Limits von 280–1.568 px und Seitenverhältnis 2,5. Lösung ist eine
Kachelung mit erhaltener Höhe (auf 627 px begrenzt), Breite 2,5×Höhe und 50 %
Überlappung, ohne Markierungen. Die Grenzmessungen (34 Requests) ergaben
zusätzlich: maximal sechs Bilder und etwa 32.000 Input-Token pro Request, jedes
Bild muss referenziert werden. Der Runner arbeitet daher mit Kachelgruppen ≤ 6,
einer automatischen, bei Ablehnung selbst halbierenden Blockgröße, Resume und
Budget-Wache.

Kritischer Messbefund: **Jev rechnet das Bild pro Frage ab** (1 Frage = 6.665
Token, 5 Fragen = 32.086). Bündeln spart nur HTTP-Aufrufe. Die Kosten hängen am
Produkt aus Fragen und Bildfläche.

## Ergebnisse

Pilot (2 Bilder, voller Katalog): 0,708 USD, Mechanik bestätigt. Messlauf (15
Bilder, 250-Item-Katalog, 3.750 Bild-Item-Paare): exakt Accuracy 0,940,
Precision 0,361, Recall 0,947, F1 0,522, ECE 0,107; containment-tolerant
Accuracy 0,959, Precision 0,698, Recall 0,825, F1 0,756, ECE 0,064.

Der Recall ist hoch, die Precision schwach. Ursachen: (1) Ein-Zeichen-Items sind
unbrauchbar (Acc 0,067, immer ja, weil `6` in `ALPIN6` steckt), (2) seltene Items
werden durch das Pooling über 7–33 Kacheln fast immer bejaht, (3) der zweite
FP-Anteil sind nicht annotierte, real sichtbare Texte — die bekannte
Annotation-Lücke des Bestands. Die echte Modellschwäche liegt bei langen Strings
(`ContiWinterContact TS 800`, `PILOT ALPIN 5`, `PIRELLI`).

## Kosten

Gemessen: 4W 0,197 USD/Bild, VW 0,400 USD/Bild bei 250 Items (VW-Streifen
brauchen rund 30 Kacheln, 4W rund 7). Auf 557 Bilder: 168 USD mit der
ursprünglichen, zu kleinen Blockgröße, etwa 84 USD korrigiert; voller Katalog
etwa 180–555 USD. Verbraucht: 4,30 von 5,00 USD des Testschlüssels.

## Schlussfolgerung

Der Fragekatalog-Ansatz misst auf diesem Material zuverlässig den Recall, seine
Precision ist ohne Katalogpflege und ohne bereinigten Sollwert nicht
interpretierbar. Für einen belastbaren Vollauf sind drei Entscheidungen nötig
(Scope, Metrik-Konvention, Pooling-Schwelle) plus Budgetaufstockung; empfohlen
sind containment-tolerantes GT als Leitmetrik, Entfernen der Ein-Zeichen-Items
und Abbilden der Randfragmente auf ihre Trägertexte.

**Rohdaten und Skripte:** Repository `whk-jev-analysis` (`docs/design.md`,
`docs/limits.md`, `docs/pilot.md`, `docs/run24.md`, `docs/dokumentation.md`,
`outputs/token_kosten.xlsx`).
