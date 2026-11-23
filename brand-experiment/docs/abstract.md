# Abstract

**Experiment:** Markenerkennung mit Jev 1.14 auf entrollten Reifenwandaufnahmen
(100-Bild-Test-Set aus dem VW/4W-OCR-Subset). **Stand:** 23.11.2026, abgeschlossen.

## Frage

Erkennt das Entscheidungsmodell Jev 1.14, zu welcher Marke ein Reifen gehört?
Anders als im vorangegangenen Katalog-Experiment (Textexistenz je Item) ist
dies eine Zuordnungsaufgabe: Das Modell benennt aus einer Optionsliste genau
eine Marke. Der Sollwert stammt aus den Labels des Subsets (genau ein exakter
Markenname je Bild); acht Bilder ohne Markenannotation wurden per
Nutzer-Sichtprüfung aufgelöst — in allen acht Fällen ist Goodyear erkennbar.

## Aufbau

Das Test-Set umfasst 100 Bilder, bestandsgetreu verteilt über alle 14
annotierten Marken plus die Goodyear-Fälle (Bridgestone 33, Continental 24,
Michelin 10, Pirelli 9, Goodyear 8, Dunlop 4, Hankook 4, sieben Ein-Bild-Marken).
Frageform ist eine Multiple-Choice-Frage über die alphabetische Optionsliste
(14 bzw. 15 Marken plus „KEINE MARKE LESBAR"), je Kachelgruppe einmal
gestellt; die Zusammenführung der Gruppenentscheidungen folgt der vom Nutzer
gewählten Leitmetrik **Mittel-wahrscheinlichkeit** (any-tile und Mehrheit als
Vergleich). Kachelung und Request-Handling entsprechen dem Katalog-Experiment:
Höhe ≤ 627 px, Seitenverhältnis 2,5, 50 % Überlappung, Kachelgruppen ≤ 6,
Budget-Wache, Resume.

## Ablauf und Kosten

Pilot (5 Bilder, 0,005 USD), Hauptlauf (100 Bilder, 332 Kachelgruppen,
0,111 USD) und Nachlauf (8 Goodyear-Bilder mit erweiterter Optionsliste,
0,012 USD); Summe 0,128 USD, Restbudget des Testschlüssels ~4,87 USD.

## Ergebnisse

Mit vollständiger Optionsliste erkennt Jev die Marke auf **98 von 100
Bildern** richtig (any-tile: 100/100, Mehrheit: 93/100). Je Marke liegen die
großen Klassen zwischen 96 und 100 Prozent; die zwei Fehler sind Bilder mit
uneinigen Kachelgruppen, keine systematischen Verwechslungen.

Der instruktivste Befund betrifft die Optionsliste: Im Hauptlauf war Goodyear
nicht wählbar, und alle acht Goodyear-Bilder wurden falsch zugeordnet — mit
niedrigen Wahrscheinlichkeiten und „KEINE MARKE LESBAR" regelmäßig unter den
Top-3. Mit Goodyear in der Liste (Nachlauf) sank dieser Fehler auf eins. Ein
Choice-Modell kann eine Marke, die ihm nicht angeboten wird, strukturell
nicht benennen; Optionslisten müssen daher aus dem Gesamtbestand abgeleitet
werden, nicht aus dem betrachteten Subset.

## Schlussfolgerung

Die Markenerkennung funktioniert mit vollständig abgedeckter Optionsliste
nahezu fehlerfrei und ist mit 0,001 USD je Bild so günstig, dass Ausweitungen
auf das volle Subset (557 Bilder, geschätzt unter 1 USD bei gleicher
Kachelungsstrategie) ohne Bedenken möglich sind. Die Grenzen des Experiments
liegen in der schiefen Markenverteilung des Bestands und in der
annotationsbasierten Sichtprüfung als Sollwert-Quelle.
