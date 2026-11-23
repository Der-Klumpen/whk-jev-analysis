# Pilotlauf: Markenerkennung an 5 Bildern (Choice über 15 Optionen)

Stand 23.11.2026. Zweck des Laufes ist die Prüfung der Frageform, nicht die
Messung der Genauigkeit; fünf Bilder erlauben keine statistischen Aussagen.

## Aufbau

Der Runner stellt für jedes Bild eine Multiple-Choice-Frage über alle 15
Optionen: die 14 Marken des Subsets plus die Option „KEINE MARKE LESBAR". Die
Optionen stehen alphabetisch in den Criteria, jede Option trägt eine eigene
Beschreibung, damit Jev sie nicht dedupliziert. Ein Bild wird in Kachelgruppen
von höchstens sechs Kacheln aufgeteilt; jede Kachelgruppe erhält die Frage
eigenständig und antwortet unabhängig. Die Auswertung folgt dem
any-tile-Pooling: Ein Bild gilt als richtig erkannt, wenn mindestens eine
Kachelgruppe die Sollmarke wählt. Daneben wird die Wahrscheinlichkeit der
Sollklasse (`p_gt`) je Kachelgruppe protokolliert, damit später auch
Schwellenwert- oder Mehrheitsentscheidungen ausgewertet werden können.

Die fünf Pilotbilder decken vier Klassen ab: zwei Michelin- und je ein
Bridgestone- und Continental-Bild aus dem Test-Set sowie ein Bild der Klasse
„Ohne erkennbare Marke" (VW-Bestand, mit Goodyear-Produktnamen laut Label).

## Ergebnis

Die vier Bilder mit klar annotierter Marke werden alle richtig erkannt; die
Wahrscheinlichkeit der Sollklasse liegt zwischen 0,90 und 1,00, die zweite
Option jeweils nahe null. Das Bild ohne Marken-String wird von den drei
Kachelgruppen unterschiedlich beantwortet: einmal `Firestone`, einmal
`Continental`, einmal `KEINE MARKE LESBAR`. Das entspricht der Erwartung aus
der Designanalyse, denn die Flanke trägt Goodyear-Produktnamen, die im
Sollwert nicht als Marke hinterlegt sind; Firestone und Continental sind
Modellfehler, die „keine Marke"-Antwort ist vertretbar. Der Fall bestätigt die
Planung, diese Klasse vor der Endauswertung per Sichtprüfung zu klären.

## Kosten und Zeit

Fünf Bilder mit 55 Kacheln insgesamt kosten 0,0053 USD und brauchen 6,6
Sekunden bei sequentieller Abarbeitung. Je Bild mit sieben Kacheln fallen
etwa 0,0015 bis 0,0024 USD an, je Bild mit 17 Kacheln entsprechend mehr. Auf
das Test-Set von 100 Bildern hochgerechnet sind etwa 0,10 bis 0,15 USD zu
erwarten, abhängig vom Kachelanteil der VW-Bilder; das Restbudget des
Testschlüssels trägt das mit deutlichem Abstand.

## Schlussfolgerung für den Hauptlauf

Die Choice-Frage über die Markenliste funktioniert: Jev benennt die Marke
direkt, die Wahrscheinlichkeiten sind scharf getrennt, und das Pooling über
Kachelgruppen ist konsistent. Für den Hauptlauf über alle 100 Bilder stehen
damit nur noch zwei Entscheidungen aus: die Behandlung der Klasse „Ohne
erkennbare Marke" (Sichtprüfung der acht Test-Set-Bilder) und die
Auswertungsregel für den Konfliktfall, wenn Kachelgruppen unterschiedlich
entscheiden. Rohdaten des Laufes liegen unter
`outputs/runs/brand_pilot5.jsonl`.
