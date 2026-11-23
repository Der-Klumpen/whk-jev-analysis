# Prompt-Vorlagen

Zwei Varianten, beide mit Choice-Antwort `yes`/`no`. Jede Frage hat **eigene**
criteria (Jev dedupliziert Fragen mit identischem criteria). Alle Assets eines
Requests müssen in jeder Frage referenziert werden, sonst
`400 Invalid image request`.

## A) `long` (Produktivpfad, Kachelgruppe ≤6)

```
instructions:
The images `tile00`, `tile01`, `tile02`, `tile03`, `tile04`, `tile05` show
consecutive, overlapping sections of one unwrapped tire wall, ordered left to
right. Is the exact text `<ITEM>` readable on the tire? Answer yes or no.

criteria:
  yes: The exact text "<ITEM>" is legible somewhere in the shown tire sections.
  no:  The exact text "<ITEM>" is not legible anywhere in the shown tire sections.
```

## B) `short` (eine Kachel pro Request, Minimalform)

```
instructions:
Image `tile00` (a section of an unwrapped tire wall). Exact text `<ITEM>` readable?

criteria:
  yes: `<ITEM>` is legible in the image.
  no:  `<ITEM>` is not legible in the image.
```

## Warum „exact text"

GT sind annotierte Textboxen. Ohne „exact" zählt jede Substring-Beziehung mit
(`EXTRA` in `EXTRA LOAD`, `6` in `205/55R16`) und die Precision wird durch die
Item-Konstruktion verzerrt, nicht durch das Modell.

## Warum Englisch

Nutzerentscheidung; deckt sich mit dem EN-Lauf der SORDI-Reihe (EN war dort
minimal, aber nicht signifikant besser als DE — McNemar p ≈ 0,12).

## Antwortauswertung

`choice` ∈ {yes, no}; `probabilities.yes` wird als `p_yes` gespeichert
(Kalibrierung/ECE). Unbeantwortet oder unparsbar = falsch.
