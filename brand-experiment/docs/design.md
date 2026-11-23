# Design: Markenerkennung mit Jev (Brand-Experiment)

## 1. Zielsetzung

In diesem Experiment wird gemessen, ob das Entscheidungsmodell Jev 1.14 die
Marke eines Reifens richtig erkennt. Anders als im Katalog-Experiment geht es
nicht um die Existenz einzelner Textstrings, sondern um eine Zuordnung: Zu
welcher Marke gehört der Reifen auf dem Bild? Der Sollwert ist die Marke, die
laut Annotation eindeutig auf der Reifenflanke steht.

## 2. Datenbasis und Sollwert

Grundlage ist dasselbe Testsubset wie im Katalog-Experiment
(`all_test.txt`, 557 Bilder: 289 VW, 268 4W). Der Sollwert wird aus den
Labels abgeleitet: Ein Bild erhält die Klasse einer Marke, wenn genau ein
exakter Marken-String annotiert ist (zum Beispiel `BRIDGESTONE` oder
`Continental`). Mehrere unterschiedliche Marken kommen auf keinem Bild vor,
das wurde geprüft; scheinbare Mehrfachnennungen lösen sich zu einer Marke mit
ihren Produktlinien auf (`Conti` und `ContiWinterContact` gehören zu
`Continental`).

Von den 557 Bildern tragen 511 genau eine klar annotierte Marke und bilden den
eigentlichen Messbestand. Weitere 46 Bilder enthalten keinen Marken-String;
sie sind in einer eigenen Klasse „Ohne erkennbare Marke" zusammengefasst. Bei
einem Teil von ihnen stehen Produktnamen ohne den Herstellernamen auf der
Flanke (zum Beispiel `EfficientGrip` oder `UltraGrip` von Goodyear), weshalb
der Sollwert dieser Klasse unsicher ist und vor der Endauswertung durch
Sichtprüfung geklärt werden sollte.

## 3. Test-Set

Das Test-Set umfasst 100 Bilder und wird vom Skript `scripts/00_make_testset.py`
deterministisch erzeugt (Seed 42). Die Verteilung folgt den Anteilen der
Klassen im Bestand, wobei alle 14 Marken mit mindestens einem Bild vertreten
sind und die kleinen Marken dadurch von den größten Klassen abgezweigt wurden.
Das Ergebnis: Bridgestone 33, Continental 24, Michelin 10, Pirelli 9, ohne
erkennbare Marke 8, Dunlop 4, Hankook 4 und die übrigen neun Marken mit je
einem Bild. Der Gruppenmix liegt bei 44 VW- und 56 4W-Bildern.

Die Verteilung ist absichtlich nicht gleichmäßig, sondern bestandsgetreu: Die
sechs Ein-Bild-Marken (Kleber, Semperit, Fulda, Nokian, Kumho, Firestone,
Falken, Vredestein) erlauben keine belastbare Aussage je Marke und dienen nur
der Abdeckung. Aussagen je Marke sind daher für die vier größten Klassen
erwartbar, für die übrigen nur Summenauswertungen.

## 4. Frageform (noch offen)

Die genaue Frageform ist noch nicht festgelegt. Kandidaten sind eine
Multiple-Choice-Frage über die Klassenliste (mit einer Option „keine Marke
lesbar"), eine Ja/Nein-Frage je Marke im Stil des Katalog-Experiments oder eine
freie Antwort. Die Wahl bestimmt die Auswertung unmittelbar und wird mit dem
Nutzer abgestimmt, bevor der Pilotlauf ausgewertet wird.

Für den Pilotlauf wird die Multiple-Choice-Variante verwendet, weil sie das
Messobjekt am direktesten abbildet: Jev soll die Marke benennen, nicht die
Existenz eines Strings bestätigen.

## 5. Technischer Rahmen

Der technische Rahmen entspricht den Messungen des Katalog-Experiments und wird
dort dokumentiert (`katalog-experiment/docs/limits.md`). Kernpunkte: Jev
berechnet das Bild pro Frage neu, ein Request trägt höchstens sechs Bilder und
rund 32.000 Input-Token, jedes Asset muss referenziert werden. Die Kachelung
begrenzt die Höhe auf 627 Pixel, setzt die Breite auf das 2,5-Fache der Höhe
und überlappt benachbarte Kacheln um 50 Prozent, damit Text an den Nähten
nicht verloren geht. Der Runner übernimmt Budget-Wache und Resume aus dem
Katalog-Experiment.

## 6. Pilotlauf

Der Pilotlauf prüft die Frageform an fünf Bildern des Test-Sets. Er ist
bewusst klein gehalten und dient drei Fragen: Liefert die Choice-Frage über die
Markenliste brauchbare Antworten? Wie groß ist der Token- und damit der
Kostenaufwand je Bild? Und wie verhält sich Jev bei den Randfällen
Produktname-ohne-Markenname und unlesbarer Flanke?
