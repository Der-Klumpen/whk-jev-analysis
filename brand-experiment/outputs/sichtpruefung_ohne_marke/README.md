# Sichtprüfung: die 8 Bilder der Klasse „Ohne erkennbare Marke"

Diese Bilder tragen im Sollwert keine Marke, weil kein Markenname annotiert
ist. Vor der Endauswertung ist zu klären, ob auf der Flanke tatsächlich keine
Marke erkennbar ist — oder ob eine Marke physisch vorhanden, aber nie
annotiert wurde. Bis dahin zählen diese Bilder in der Auswertung als falsch,
sobald Jev irgendeine Marke wählt; das drückt die Accuracy der Klasse
künstlich auf null.

## Wo sind die Bilder?

Der Ordner `outputs/sichtpruefung_ohne_marke/` enthält Kopien aller acht
Bilder (Dateiname = image_id + Endung). Die zugehörigen Metadaten und die
annotierten Texte stehen in `data/sichtpruefung_ohne_marke.jsonl`, je Zeile
mit `image_id`, Dateinamen und `label_items`.

## So annotierst du

Trage deine Sichtprüfung direkt in `data/sichtpruefung_ohne_marke.jsonl` ein,
je Bild zwei neue Felder:

- `"marke_sichtpruefung"`: der Markenname, den du auf der Flanke erkennst —
  in der Schreibweise der 15 Optionen des Experiments (Bridgestone,
  Continental, Dunlop, Falken, Firestone, Fulda, Hankook, Kleber, Kumho,
  Michelin, Nokian, Pirelli, Semperit, Vredestein) — oder genau der String
  `"Ohne erkennbare Marke"`, wenn wirklich kein Markenname lesbar ist. Ist die
  Marke erkennbar, aber nicht in der Optionsliste (zum Beispiel Goodyear),
  schreibe den Namen so, wie er dasteht; die Auswertung behandelt das als
  eigene Klasse.
- `"bemerkung"` (optional): kurz, was du gesehen hast, zum Beispiel
  „Goodyear über Produktnamen EfficientGrip erkennbar" oder „nur DOT und
  Dimensionsangaben".

Beispiel einer ausgefüllten Zeile:

```json
{"image_id": "ea5aaec8…", "datei": "ea5aaec8….jpg", "label_items": ["GOOD", "EfficientGrip", "…"],
 "marke_sichtpruefung": "Goodyear", "bemerkung": "EfficientGrip ist Goodyear-Produktlinie, Logo klein erkennbar"}
```

Die Datei ist die einzige Quelle der Auswertung; Änderungen an den Bildern
selbst sind nicht nötig.

## Was die Auswertung damit macht

Nach deiner Eintragung wird die Klasse aufgelöst: Bilder mit erkannter Marke
wandern in die jeweilige Markenklasse (und Jevs Antworten werden neu gegen
den korrigierten Sollwert gewertet), Bilder mit bestätigtem „keine Marke"
bleiben in der Negativklasse. Die Accuracy der bisherigen Klasse 0,00 ist
damit voraussichtlich deutlich zu pessimistisch; wie viel genau, zeigt die
Neuauswertung nach deiner Eintragung.

## Hinweis zur Erwartung

Sieben der acht Bilder tragen laut Labels Goodyear-typische Produktnamen
(`EfficientGrip`, `UltraGrip`, `BLIZZAK`, `LM-32`), eines nur allgemeine Texte.
Es ist also wahrscheinlich, dass ein großer Teil der Klasse nach der
Sichtprüfung zu Goodyear wird — einer Marke, die in der Optionsliste des
Laufs nicht enthalten war. Für die Interpretation heißt das: Jev konnte diese
Marke nicht wählen; die Auswertung sollte diese Bilder dann als
„Marke außerhalb der Optionen" gesondert ausweisen, nicht als einfache
Fehlentscheidung.
