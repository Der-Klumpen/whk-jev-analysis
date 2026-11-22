# Design: Item-Existenz mit Jev auf Reifenpanoramen

Stand: wird beim Lauf fortgeschrieben. Jede Festlegung hier ist eine
Entscheidung mit Begründung, keine Beschreibung des Ist-Zustands.

## 1. Aufgabe

Pro Bild des Subsets (`all_test.txt`, 557 Bilder: 289 VW, 268 4W) wird Jev 1.14
**jedes Item des Katalogs** einzeln gefragt: „Is the exact text `X` readable on
the tire?" Antwort nur `yes`/`no` (Choice mit zwei Optionen). Danach Vergleich
gegen GT.

Reihenfolge: bildweise — für Bild 1 alle Items, dann Bild 2 usw. Ein Lauf ist
über `image_id`-Resume unterbrechbar; die Reihenfolge ist damit erhalten.

## 2. Warum mehrere Fragen pro Request (Antwort auf die Ausgangsfrage)

Ein Request kann mehrere Fragen enthalten. Notwendig ist es aus zwei Gründen:

1. **Kosten**: Das Bild wird pro Request einmal berechnet, unabhängig von der
   Fragenzahl. Eine Frage pro Request zahlt die Bild-Token 824-mal pro Bild.
2. Durchsatz/Zeit.

Grenze in der Gegenrichtung: Der Request hat ein Token-/Größenlimit (gemessen,
siehe §6). Fragen werden deshalb in Blöcke gepackt, die zusammen mit den
Kacheln unter dem Limit bleiben. Jede Frage hat eigene `criteria` — Jev
dedupliziert Fragen mit identischem `criteria`, wortgleiche Criteria würden
also kollabieren.

## 3. Ground-Truth-Definition

GT = annotierter Text. Pro Bild: Menge der Strings aus den Labels.
- 4W: `Content`-Attribut der `Text_Area`-Boxen.
- VW: Transkription des zugehörigen OCR-Crops (`_bbox_i`).
- Vergleich casefold + Whitespace-normiert; Katalog casefold-dedupliziert
  (häufigste Schreibweise als Item, Abweichungen als Alias dokumentiert).

**Bewusste Grenze:** „nicht annotiert" heißt nicht „nicht sichtbar". Reifen
tragen weiteren nicht katalogisierten Text. Ein FP kann also ein real
gelesener, aber nicht annotierter Text sein — bei der Interpretation der
Precision mitzulesen, nicht als reines Modellversagen.

Item-Qualität (dokumentiert, nicht bereinigt):
- Ein-Zeichen-Items (113 Instanzen, z. B. `6`): Grenzfall der Frageformulierung.
- Randfragmente (180 Instanzen, z. B. `ICHELIN`): Text an der Bildkante
  abgeschnitten; GT ist der Fragmentstring.
- Wiederholte Items pro Bild (z. B. `205/55R16` 6× auf einem Reifen) zählen
  als **ein** GT-Item: gefragt wird die Existenz, nicht die Anzahl.

## 4. Kachelung (erzwungen)

Panoramen bis 17.906 × 278 px (AR bis 45); Jev erlaubt 280–1568 px je Seite und
AR ≤ 2,5. Ein Bild passt nie in einen Request.

- Höhe bleibt erhalten (kein Höhenverlust, kein Padding-Balken); nur wenn die
  Höhe außerhalb 280–1568 liegt, wird skaliert.
- Kachelbreite = min(1568, Höhe×2,5), Schrittweite = Breite × (1−Überlappung).
- Überlappung ≥ 50 %, damit Text an Kachelnähten in der Nachbarkachel
  vollständig liegt (Boxbreite median 374 px, p99 2346 px).
- Letzte Kachel wird bündig an den rechten Rand gezogen (kein Reststreifen).
- Keine Markierungen in den Kacheln. Kachel-Offsets in `tiles.json` für
  spätere Positionsanalysen.
- Boxen breiter als die Kachelbreite (378 Instanzen > 1568 px) verteilen sich
  über mehrere Kacheln; das Item bleibt in der Regel in mindestens einer
  Kachel lesbar.

## 5. Aggregation

Ein Item gilt für ein Bild als erkannt, wenn **irgendein** Request des Bildes
`yes` liefert (Max-Pooling). `p_yes` wird als Maximum über die Requests des
Items gespeichert, damit die Kalibrierung auswertbar bleibt.

## 6. Request-Grenzen (gemessen, s. outputs/runs/probe*.json, docs/limits.md)

- Bild wird **pro Frage** berechnet: 1 Kachel + 1 Frage = 6.665 Token,
  1 Kachel + 5 Fragen = 32.086. Bündeln spart keine Bildkosten.
- Arbeitsgrenze ~24.000 Input-Token pro Request (`max_tokens_exceeded` ab ~32k).
- Maximal ~6 Bilder pro Request; ab 7 `400 Invalid image request`.
- Jedes Asset muss in jeder Frage referenziert werden, sonst
  `400 Invalid image request`.
- Konsequenz für den Runner: Kacheln werden in Gruppen (≤6) und Fragen in
  Blöcke (Budget/Token) geteilt; jedes Item wird damit **einmal pro
  Kachelgruppe** gefragt, nicht einmal pro Bild.

## 7. Prompt

Vorlagen: `prompts/templates.md` (Variante `long` = Produktivpfad). „exact
text" ist gesetzt, weil GT annotierte Textboxen sind; ohne „exact" zählen
Substring-Treffer (`EXTRA` in `EXTRA LOAD`) mit.

## 8. Auswertung

Accuracy, Precision, Recall, F1, ECE, Verwechslungszählung, Zerlegung nach
Gruppe, Item-Häufigkeit, Item-Länge, Randfragment, Boxbreite. Unbeantwortet =
falsch (Konvention des Referenz-Evaluators).
