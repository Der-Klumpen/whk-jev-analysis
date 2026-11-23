# whk-jev-analysis — Jev-Experimente auf Reifenpanoramen

Sammlung abgeschlossener und laufender Experimente mit dem Entscheidungsmodell
Jev 1.14 (TypeSafe-API) auf den Reifenbeständen VW/4W des OCR-Projekts. Jedes
Experiment ist ein eigenständiger Ordner mit eigener Pipeline, Dokumentation und
Auswertung; Experimente teilen sich keine Dateien.

## Experimente

- **[katalog-experiment/](katalog-experiment/)** — Item-Existenz: Für jedes Bild
  des Subsets wird Jev jedes von 824 Items aus den Labels einzeln als
  Ja/Nein-Frage gestellt („Ist `X` auf dem Reifen zu lesen?"). Abgeschlossen
  (Pilot + budget-gedeckelter Messlauf), Dokumentation im Ordner.
- **[brand-experiment/](brand-experiment/)** — Markenerkennung: Jev wählt aus
  einer Optionsliste die Marke eines Reifens. Abgeschlossen; 98 von 100
  Testbildern richtig (Leitmetrik Mittel-wahrscheinlichkeit), Nebenbefund zur
  Abhängigkeit von der Optionslisten-Abdeckung.

## Gemeinsame Datenbasis (nur lesend, liegt außerhalb des Repos)

- Subset: `/home/iiot/data/OCR/all_test.txt`, 557 Bilder (289 VW, 268 4W)
- Bilder/Labels: `/home/iiot/data/OCR/{VW,4W}/{images,labels}`
- Annotationen: VW `OCR_annotations-cleaned_v01.json`, 4W `4W_annotations.xml`
- Jev-Key: `~/TypeSafe-Keys/Jev-Test-Key.txt`, Budget-Wache je Experiment

## Technische Randbedingungen (für alle Experimente gültig)

Jev rechnet das Bild **pro Frage** ab (gemessen, nicht geschätzt): Kosten =
Fragen × Kachelfläche. Request-Grenzen: ~32.000 Input-Token, maximal ~6 Bilder
je Request, jedes Asset muss in jeder Frage referenziert werden. Panoramen
(A Seitenverhältnis bis 45) werden gekachelt: Höhe auf 627 px begrenzt, Breite
2,5 × Höhe, 50 % Überlappung. Details und Messreihen:
`katalog-experiment/docs/limits.md`.
