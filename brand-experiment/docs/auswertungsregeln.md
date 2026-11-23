# Auswertungsregeln bei widersprüchlichen Kachelgruppen (Entscheidungsvorlage)

Im Hauptlauf entscheidet Jev nicht einmal je Bild, sondern einmal je
**Kachelgruppe** — einem Request mit bis zu sechs Kacheln desselben Bildes. Ein
Bild mit 30 Kacheln erzeugt also fünf voneinander unabhängige
Markenentscheidungen. Diese Vorlage beschreibt die drei Regeln, mit denen aus
den Gruppenentscheidungen eine Bildentscheidung wird, zeigt ihre Wirkung auf
dem Pilotlauf und dem bisherigen Stand des Vollaufs und begründet, wann welche
Regel die Leitmetrik sein sollte. Die Entscheidung, welche Regel die Leitmetrik
wird, trifft der Nutzer (Eintrag am Ende dieser Datei).

## Die drei Regeln

**1. any-tile** — Das Bild gilt als Marke X erkannt, wenn mindestens eine
Kachelgruppe X wählt. Dies ist die Regel des Pilotlaufs. Sie maximiert den
Recall: Kein echter Markenschriftzug geht verloren, weil eine einzige Kachel
ihn klar sieht. Ihr Preis ist die Precision, denn eine einzige Fehlentscheidung
einer Kachelgruppe genügt, um ein Bild falsch zu markieren — und je mehr
Kachelgruppen ein Bild hat (VW bis zu fünf, 4W meist zwei), desto größer ist
diese Angriffsfläche. Diese Asymmetrie ist nicht unteilbar: Sie fällt bei
4W-Bildern mit zwei Gruppen viel schwächer ins Gewicht als bei VW-Bildern mit
fünf.

**2. Mehrheit** — Das Bild erhält die Marke, die die meisten Kachelgruppen
wählen; bei Stimmengleichheit gilt das Bild als „uneins" und zählt als falsch.
Diese Regel ist robust gegen einzelne Fehlentscheidungen, bezahlt das aber mit
Recall auf Bildern, wo der Markenschriftzug nur in einer einzigen Kachel klar
lesbar ist — gerade bei sehr langen VW-Panoramen mit vielen Kacheln eine reale
Situation.

**3. Mittel-wahrscheinlichkeit** — Für jede Option wird die mittlere
Wahrscheinlichkeit über alle Kachelgruppen gebildet; das Bild erhält die Option
mit dem höchsten Mittelwert. Diese Regel nutzt die volle Information der
Wahrscheinlichkeiten statt nur der harten Entscheidungen und ist die
kalibrierungsärmste Interpretation. Sie kann von beiden anderen abweichen, weil
eine Gruppe mit sehr hoher Sicherheit die moderaten Wahrscheinlichkeiten der
übrigen Gruppen überstimmen kann.

Ergänzend wird für alle drei Regeln die Wahrscheinlichkeit der Sollklasse
protokolliert (`p_gt` je Kachelgruppe, daraus Maximum und Mittelwert), sodass
die Kalibrierung (ECE) und Schwellenwertvarianten nachträglich ausgewertet
werden können, ohne den Lauf zu wiederholen.

## Wirkung auf dem Pilotlauf (5 Bilder)

Auf den vier klar markierten Bildern entscheiden sich alle drei Regeln
identisch: Die Kachelgruppen stimmen fast ausnahmslos überein, die Sollmarke
gewinnt nach jeder Regel. Der einzige Unterschied zeigt sich beim Bild der
Klasse „Ohne erkennbare Marke" mit Goodyear-Produktnamen: any-tile wählt
`Firestone` (eine Gruppe sagte das), Mehrheit ergäbe ebenfalls `Firestone`,
Mittel-wahrscheinlichkeit wählte `Continental`. Da dieses Bild in allen Regeln
falsch liegt, trennt der Pilot die Regeln nicht — das kann nur der Hauptlauf.

## Wirkung auf dem Vollauf (bisheriger Stand)

Der Vollauf liefert für jedes Bild alle Gruppenentscheidungen, sodass alle
drei Regeln aus denselben Rohdaten berechnet werden — die Wahl der Leitmetrik
kostet keine erneuten API-Aufrufe. Die Auswertung (`scripts/02_evaluate_brand.py`)
berechnet deshalb alle drei parallel und weist zusätzlich aus, welcher Anteil
der Bilder überhaupt „uneins" war, denn dieser Anteil bestimmt, wie stark sich
die Regeln überhaupt unterscheiden können. Bei vollständiger Einstimmigkeit
sind alle drei Regeln identisch.

## Empfehlung

Als Leitmetrik empfiehlt sich **Mittel-wahrscheinlichkeit**, mit any-tile und
Mehrheit als Vergleichsspalten. Drei Gründe sprechen dafür: Sie nutzt die
Information aller Gruppen statt nur der harten Votes; sie ist die einzige der
drei Regeln, die nicht systematisch Richtung Recall oder Richtung Precision
verzerrt, sondern die Modellwahrscheinlichkeit direkt interpretiert; und sie
bleibt auch bei unterschiedlich vielen Kachelgruppen pro Bild vergleichbar,
während any-tile mit wachsender Gruppenzahl systematisch großzügiger wird.
Für die Frage „erkennt Jev die Marke überhaupt irgendwo" bleibt any-tile die
richtige Ergänzungsmetrik und sollte im Bericht mitgeführt werden.

## Entscheidung

*(wird vom Nutzer eingetragen)*

Leitmetrik: Mittel-wahrscheinlichkeit, mit any-tile und
Mehrheit als Vergleichsspalten
