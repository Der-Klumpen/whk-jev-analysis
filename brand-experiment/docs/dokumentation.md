# Dokumentation: Markenerkennung mit Jev (Brand-Experiment)

Stand 23.11.2026. Bericht über Aufbau, Durchführung und Ergebnis des
Brand-Experiments im Ordner `brand-experiment` des Repositories
`whk-jev-analysis`. Fachbegriffe sind kursiv gesetzt und im Verzeichnis am Ende
erklärt. Der technische Unterbau (Kachelung, Request-Mechanik, Grenzen) ist im
Katalog-Experiment ausführlich dokumentiert
(`katalog-experiment/docs/dokumentation.md`, `katalog-experiment/docs/limits.md`)
und wird hier nur soweit wiederholt, wie es zum Verständnis nötig ist.

## 1. Fragestellung

Während das Katalog-Experiment prüfte, ob Jev einen bestimmten Textstring auf
einem Reifenpanorama lesen kann, stellt das Brand-Experiment die nächste Frage:
Erkennt Jev, **zu welcher Marke der Reifen gehört?** Das ist eine
Zuordnungsaufgabe statt einer Existenzaufgabe — das Modell muss den
Markenschriftzug nicht nur finden, sondern ihn einer Marke zuordnen und alle
anderen Optionen ausschließen.

Das Experiment misst diese Fähigkeit unter drei Bedingungen, die im Lauf der
Arbeit entstanden: mit einer Optionsliste, die alle im Subset annotierten
Marken enthält (Hauptlauf), mit einer unvollständigen Optionsliste (die
Goodyear-Fälle des Hauptlaufs) und mit einer vollständigen Liste, die Goodyear
nachträglich aufnimmt (Nachlauf). Genau diese Abfolge macht das Experiment
auswertbar, weil sie die Abhängigkeit eines Choice-Modells von seiner
Optionsliste isoliert.

## 2. Sollwert: woher die „richtige" Marke kommt

Der Sollwert stammt aus denselben Labels wie im Katalog-Experiment: Ein Bild
erhält die Klasse einer Marke, wenn genau ein exakter Markennamen annotiert
ist. Die Prüfung ergab, dass kein Bild zwei verschiedene exakte Markennamen
trägt — scheinbare Mehrfachnennungen lösen sich zu einer Marke samt
Produktlinien auf (`Conti` und `ContiWinterContact` gehören zu
`Continental`).

Von den 557 Bildern des Subsets erfüllen 511 diese Bedingung. Weitere 46 Bilder
ohne Markenannotation wurden zunächst als Klasse „Ohne erkennbare Marke"
geführt. Die **Sichtprüfung** durch den Nutzer ergab später, dass auf allen
acht Bildern dieser Klasse, die ins Test-Set gelost wurden, sehr wohl eine
Marke erkennbar ist — durchgängig **Goodyear**, teils nur schwer lesbar
(die Bemerkungen nennen Licht, Skalierung und geringen Kontrast). Der Sollwert
wurde daraufhin korrigiert: Das Test-Set enthält nun 15 Marken, davon Goodyear
mit acht Bildern, und keine Klasse „ohne Marke" mehr. Diese Korrektur ist der
Grund für den Nachlauf in Abschnitt 5.

Der Unterschied zum Katalog-Experiment ist bemerkenswert: Dort war
„nicht annotiert" ein dauerhaftes Messproblem, weil die GT-Definition am
Annotationbestand hing. Hier wurde es durch die Sichtprüfung aufgelöst —
die acht Bilder zeigen aber zugleich, wie leicht ein Choice-Experiment an
einer unvollständigen Optionsliste scheitert.

## 3. Test-Set

Das Test-Set umfasst 100 Bilder und wird von `scripts/00_make_testset.py`
deterministisch erzeugt (Seed 42). Die Verteilung folgt den Bestandsanteilen,
wobei jede der 14 Marken ursprünglich mit mindestens einem Bild vertreten war:
Bridgestone 33, Continental 24, Michelin 10, Pirelli 9, Dunlop 4, Hankook 4
und sieben Ein-Bild-Marken, plus acht Bilder der zwischenzeitlich aufgelösten
Klasse „Ohne erkennbare Marke". Der Gruppenmix liegt bei 44 VW- und 56
4W-Bildern. Die Verteilung ist bestandsgetreu und nicht gleichmäßig; die
Ein-Bild-Marken erlauben keine Aussage je Marke, sondern nur die Aussage, dass
auch sie korrekt erkannt wurden.

## 4. Frageform

Gewählt wurde eine **Multiple-Choice-Frage**: Jev bekommt alle Kacheln einer
Kachelgruppe (bis zu sechs zusammengehörige Kacheln eines Bildes) und die
Anweisung, genau eine Option zu wählen. Die Optionen sind die Marken in
alphabetischer Reihenfolge plus „KEINE MARKE LESBAR"; jede Option trägt eine
eigene `criteria`-Beschreibung, damit Jev sie nicht dedupliziert. Diese Form
bildet die Fragestellung direkt ab — das Modell benennt die Marke, statt die
Existenz eines Strings zu bestätigen — und ist zugleich die günstigste: Ein
Bild kostet unabhängig von der Optionszahl eine einzige Frage je Kachelgruppe.

Je Bild entstehen so mehrere unabhängige Entscheidungen, eine je Kachelgruppe.
Ihre Zusammenführung erfolgt nach drei Regeln (any-tile, Mehrheit,
Mittel-wahrscheinlichkeit), deren Bewertung und Vergleich
`docs/auswertungsregeln.md` dokumentiert. Der Nutzer hat die
**Mittel-wahrscheinlichkeit** als Leitmetrik bestimmt; any-tile und Mehrheit
bleiben Vergleichsspalten.

## 5. Ablauf der Läufe

Der **Pilotlauf** fragte fünf Bilder ab (zwei Michelin, je ein Bridgestone,
Continental und ein Bild der damaligen Klasse „Ohne erkennbare Marke"). Er
bestätigte die Frageform: Alle vier klar markierten Bilder wurden in jeder
Kachelgruppe richtig benannt, mit Sollklassen-Wahrscheinlichkeiten von 0,90
bis 1,00; das fünfte Bild wurde uneins beantwortet. Kosten: 0,0053 USD.

Der **Hauptlauf** fragte alle 100 Bilder ab — 332 Kachelgruppen, 1.583
Kacheln, 0,111 USD, rund zwei Minuten. Er lief mit der ursprünglichen
Optionsliste aus 14 Marken plus Leerroption.

Der **Nachlauf** wiederholte genau die acht Bilder, deren Sollwert nach der
Sichtprüfung Goodyear lautet, mit identischem Aufbau, aber Goodyear als
zusätzlicher Option (15 Marken plus Leerroption). Kosten: 0,012 USD. Dieser
Nachlauf ist die Kontrollmessung zur Optionsabdeckung; ohne ihn bliebe offen,
ob die Fehler dieser Bilder dem Modell oder der Optionsliste anzulasten sind.

Insgesamt belaufen sich die Kosten des Brand-Experiments auf 0,128 USD; das
Restbudget des Testschlüssels beträgt rund 4,87 USD.

## 6. Ergebnisse

Über alle 100 Bilder, jede Kachelgruppe genau einmal gewertet (Hauptlauf für
92 Bilder, Nachlauf für die acht Goodyear-Bilder):

| Regel | Richtig | Accuracy |
|---|---|---|
| any-tile | 100 | **1,000** |
| **Mittel-wahrscheinlichkeit (Leitmetrik)** | **98** | **0,980** |
| Mehrheit | 93 | 0,930 |

Je Marke unter der Leitmetrik: Bridgestone 33/33, Continental 23/24, Michelin
10/10, Pirelli 9/9, Goodyear 7/8, Dunlop 4/4, Hankook 4/4, und alle
Ein-Bild-Marken korrekt. Die zwei Fehler sind Bilder mit uneinigen
Kachelgruppen (ein Continental-Bild, ein Goodyear-Bild), nicht
systematische Verwechslungen; unter any-tile wird jedes Bild mindestens einmal
richtig benannt.

Der Hauptlauf allein — mit unvollständiger Optionsliste — hatte auf den
Goodyear-Bildern null Treffer ergeben: Jev wählte Dunlop, Firestone,
Continental und Nokian, mit niedrigen Wahrscheinlichkeiten und „KEINE MARKE
LESBAR" regelmäßig unter den Top-3. Der Nachlauf drehte dieses Bild: 7/8 unter
der Leitmetrik, 8/8 unter any-tile. Der Unterschied zwischen beiden Läufen ist
das eigentliche Ergebnis des Experiments neben der hohen Erkennungsrate: Ein
Choice-Modell kann eine Marke, die ihm nicht als Option angeboten wird,
strukturell nicht benennen. Die Optionen müssen daher aus dem Gesamtbestand
abgeleitet werden, nicht aus dem Subset.

## 7. Grenzen

Drei Grenzen sind bei der Interpretation zu beachten. Erstens ist die
Verteilung stark schief: Bridgestone und Continental stellen 57 Prozent der
Bilder, die Aussage je Marke ist für die kleinen Klassen auf „korrekt
erkannt" beschränkt. Zweitens bleibt der Sollwert annotationsbasiert; die
Sichtprüfung hat die offenen Fälle geklärt, aber sie stützt sich auf das Auge
des Nutzers, nicht auf eine zweite unabhängige Annotation. Drittens sind die
Kalibrierungszahlen des Hauptlaufs (ECE 0,169) unter der unvollständigen
Optionsliste entstanden und für die Endauswertung nicht mehr maßgeblich; eine
Kalibrierungsmessung unter der vollständigen Liste steht noch aus.

## 8. Reproduzierbarkeit

Die Pipeline ist numeriert und ohne API-Zugriff bis zu den Läufen wiederholbar:
`00_make_testset.py` (Test-Set, Seed 42), `02_make_tiles.py` (Kachelung),
`01_jev_brand_choice.py` (Runner mit Choice-Frage, Resume, Budget-Wache),
`02_evaluate_brand.py` (Bild- und Kachelebenen-Auswertung),
`09_token_xlsx.py` (Kostentabelle), `10_charts_brand.py` (Diagramme). Die
Sichtprüfung des Nutzers liegt als annotierte Datei
(`data/sichtpruefung_ohne_marke.jsonl`) im Repo und ist damit Teil der
Datenbasis.

---

# Fachwortverzeichnis

**any-tile-Pooling** — Auswertungsregel: Ein Bild gilt als Marke X erkannt,
wenn mindestens eine Kachelgruppe X wählt. Maximiert den Recall.

**Choice-Frage** — Frageform der Jev-API mit vorgegebenen Optionen; das Modell
wählt genau eine und liefert Wahrscheinlichkeiten für alle Optionen.

**Criteria** — Beschreibungen der Optionen einer Choice-Frage. Müssen sich je
Frage unterscheiden, sonst dedupliziert Jev die Fragen.

**ECE (Expected Calibration Error)** — Abstand der gemeldeten
Wahrscheinlichkeiten von der tatsächlichen Trefferquote; 0 ist perfekt
kalibriert.

**Ein-Bild-Marken** — Marken mit nur einem Bild im Test-Set (Falken,
Firestone, Fulda, Kleber, Kumho, Nokian, Semperit, Vredestein). Keine
Aussage je Marke möglich, nur Gesamtabdeckung.

**Goodyear-Fälle** — Die acht Bilder, deren Marke (Goodyear) nicht annotiert
war und im Hauptlauf nicht in der Optionsliste stand. Nach Sichtprüfung und
Nachlauf der zentrale Abdeckungsbefund.

**Kachelgruppe** — Bis zu sechs Kacheln desselben Bildes in einem Request. Je
Kachelgruppe fällt eine unabhängige Markenentscheidung.

**Leitmetrik** — Die für den Bericht maßgebliche Auswertungsregel; hier die
Mittel-wahrscheinlichkeit, vom Nutzer gewählt.

**Mehrheit** — Auswertungsregel: Das Bild erhält die von den meisten
Kachelgruppen gewählte Marke; Stimmengleichheit gilt als falsch.

**Mittel-wahrscheinlichkeit** — Auswertungsregel: Mittlere Wahrscheinlichkeit
je Option über alle Kachelgruppen; das Bild erhält die Option mit dem
höchsten Mittelwert. Leitmetrik dieses Experiments.

**Optionsliste** — Die einer Choice-Frage angebotenen Marken. Stammte im
Hauptlauf aus den annotierten Marken des Subsets (14 + Leerroption), im
Nachlauf aus 15 + Leerroption.

**p_gt** — Von Jev gemeldete Wahrscheinlichkeit der Sollklasse. Grundlage für
Kalibrierungsauswertungen.

**Sichtprüfung** — Manuelle Markenbestimmung der acht Bilder ohne
Markenannotation durch den Nutzer; Ergebnis als annotierte JSONL im Repo.

**VW / 4W** — Die beiden Bestandsgruppen. VW: flache Streifen, mehr Kacheln
je Bild; 4W: hohe Streifen, die auf 627 px skaliert werden.
