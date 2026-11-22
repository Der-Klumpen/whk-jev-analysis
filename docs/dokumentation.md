# Dokumentation: Item-Existenz-Experiment mit Jev auf Reifenpanoramen

Stand 22.11.2026. Bericht über Aufbau, Anpassungen und Kosten des Experiments im
Verzeichnis `/home/iiot/data/jev-analysis` (Repository `whk-jev-analysis`).
Fachbegriffe sind kursiv gesetzt und im Verzeichnis am Ende erklärt.

## 1. Ausgangslage und Ziel

Die Reifenbestände des OCR-Projekts (Gruppen **VW** und **4W**) enthalten
entrollte Reifenwandaufnahmen: Die Reifenwand ist abgewickelt und als langes
Band abgelegt, damit die Schrift darauf in einer Zeile liegt. Zu jedem Bild
existiert eine Label-Datei mit den Rechtecken des annotierten Texts und ein
Subset `all_test.txt` mit 557 Bildern (289 VW, 268 4W), das den Testanteil
festlegt.

Ziel des Experiments ist keine Transkription, sondern eine
*Existenzentscheidung*: Für jedes Bild des Subsets wird für jedes Item des
*Katalogs* einzeln gefragt, ob dieser Text auf dem Reifen zu lesen ist. Die
Frage ist englisch formuliert, die Antwort ist auf `yes`/`no` beschränkt. Die
Antworten werden je Bild und Item gespeichert und anschließend gegen den
*Ground Truth* verglichen, der aus denselben Labels abgeleitet wird. Damit
misst das Experiment die *Recall*- und *Precision*-Fähigkeit des Modells auf
einem Material, das für klassische OCR untypisch ist, und liefert Zahlen, die
sich mit den generativen OCR-Ergebnissen desselben Bestands vergleichen lassen.

Die Reihenfolge ist bildweise: erst alle Items für Bild 1, dann alle Items für
Bild 2. Der Lauf ist über die *image_id* unterbrechbar und wiederaufsetzbar,
sodass die Reihenfolge auch nach einem Abbruch erhalten bleibt.

## 2. Datengrundlage und Zuordnung

Das Subset liegt als Kopie unter `data/subset_all_test.txt`, unverändert. Die
darin enthaltenen Pfade zeigen auf einen fremden Rechner
(`/home/seko040e/...`) und werden vom ersten Skript über Gruppe und Dateiname
auf `/home/iiot/data/OCR/<Gruppe>/images/<Datei>` aufgelöst; alle 557 Bilder
sind lokal vorhanden, es gibt keine Dubletten.

Die Label-Datei heißt wie das Bild und hat die Endung `.txt`. Jede Zeile
enthält die Klasse (immer `0`) und vier normierte Polygonpunkte eines
Textrechtecks. Der eigentliche Text steht nicht in der Label-Datei, sondern in
den Annotationsträgern:

- bei 4W im Attribut `Content` der Box `Text_Area` in `4W_annotations.xml`,
- bei VW in der Transkription des zum Rechteck gehörenden OCR-Ausschnitts
  `VW/OCR_annotations-cleaned_v01.json`.

Beide Träger sind über die Zeilennummer an die Label-Zeile gebunden: Zeile *i*
gehört zu Box *i*, und bei VW ist die Box *i* identisch mit dem Ausschnitt
`<stem>_bbox_i.jpg`. Diese Bindung wurde nicht angenommen, sondern geprüft: Die
Pixelmaße der Ausschnitte stimmen mit den Polygonmaßen überein (Verhältnis 1,00
über Stichproben), und die Reihenfolge der XML-Boxen entspricht der
Zeilenreihenfolge der Label-Datei. Zeilen ohne Transkription oder ohne
`Content` tragen kein Item — bei 4W sind das die Pfeilsymbole
(`Alpine`, `Rotation_left/right`, `OEM_Q`), bei VW jene leeren Boxen, die die
Bereinigung entfernt hat.

## 3. Katalog

Der Katalog wird ausschließlich aus den Labels des Subsets gebildet, nicht aus
Fachwissen. Er umfasst alle Textstrings, die auf mindestens einem Subsetbild
annotiert sind: 6.803 Instanzen, nach Kleinschreibung und Leerraum-Normalisierung
dedupliziert 824 Items. Bei reinen Schreibvarianten bleibt die häufigste
Schreibweise als Item stehen, die übrigen werden als Alias dokumentiert. Der
Katalog liegt als `outputs/catalog.json` (mit Häufigkeit und Bildanzahl) und als
`outputs/catalog.txt` (eine Zeile je Item, Arbeitsdatei des Runners) vor.

Der Katalog ist bewusst nicht bereinigt. Er enthält deshalb zwei Sorten von
Einträgen, die später die Messung prägen: Ein-Zeichen-Items wie `5`, `6`, `55`
und `60` sowie Randfragmente wie `ICHELIN`, `UTSIDE` oder `ntal`, die durch
Annotationen am Bildrand abgeschnitten wurden. Beide Typen sind nach der
Frageformulierung „ist genau dieser Text zu lesen" nur eingeschränkt
beantwortbar, weil die Zeichenfolge irgendwo im Reifenprofil steckt.

## 4. Ground Truth und zwei Messkonventionen

Der *Ground Truth* entsteht als Gegenstück zum Katalog: Pro Bild wird die Menge
der annotierten Strings gespeichert, mit Rechteck, Breite, Höhe und einem
Merker für Randfragmente (`outputs/ground_truth.jsonl`). Ein Item gilt für ein
Bild als vorhanden, wenn mindestens eine Box exakt diesen Text trägt;
Groß-/Kleinschreibung und Leerraum werden verglichen, sonst nichts. Mehrfach
vorkommende Texte auf demselben Reifen zählen als ein Item, weil nach Existenz
und nicht nach Anzahl gefragt wird.

Zwei Eigenschaften dieser Konstruktion verzerren das Ergebnis und werden
deshalb offengelegt:

1. **Fragmente.** Der Katalog enthält Teilstücke. Antwortet Jev bei sichtbarem
   `MICHELIN` auf die Frage nach `ELIN` mit ja, ist das sachlich richtig, im
   exakten Vergleich aber ein *False Positive*. Der Effekt ist groß: Im
   Messlauf sinkt die *Precision* von 0,70 auf 0,36, wenn man ihn nicht
   herausrechnet.
2. **Annotation-Lücke.** „Nicht annotiert" heißt nicht „nicht sichtbar". Die
   Reifen tragen weiteren, nicht katalogisierten Text; ein Teil der
   *False Positives* sind real gelesene Zeichen.

Deshalb wird jede Auswertung doppelt gefahren: einmal streng gegen den exakten
Ground Truth, einmal *containment-tolerant*, wobei ein Item auch dann als
vorhanden gilt, wenn es in einem GT-String steckt oder einen GT-String enthält.
Das strenge Maß ist die Untergrenze, das tolerante Maß die realistische Zahl;
beide werden berichtet.

## 5. Das Bildmaterial und die Kachelung

Die Panoramen sind extrem breit: 11.536 bis 17.906 Pixel Breite bei 278 bis
1.700 Pixel Höhe, Seitenverhältnisse bis 45. Jev akzeptiert Bilder nur zwischen
280 und 1.568 Pixel je Seite, Seitenverhältnis höchstens 2,5, Fläche zwischen
78.400 und 2.458.624 Pixel. Ein ganzes Panorama passt damit nie in einen
Aufruf; eine Verkleinerung auf das erlaubte Seitenverhältnis würde die Breite um
den Faktor 20 stauchen und die Schrift unlesbar machen. Also wird **gekachelt**.

Die Kachelung folgt festen Regeln, die im Skript `scripts/02_make_tiles.py`
stehen:

- Die Höhe wird auf höchstens 627 Pixel begrenzt (1.568 / 2,5 — die größte
  Höhe, bei der eine Kachel die volle erlaubte Breite ausnutzen kann) und auf
  mindestens 280 Pixel angehoben, wenn der Streifen flacher ist. Höhere
  Streifen (4W, 1.436 bis 1.700 Pixel) werden dadurch um 0,36 bis 0,44
  skaliert, flache VW-Streifen bleiben nahezu nativ.
- Die Kachelbreite ist das 2,5-Fache der Höhe, begrenzt auf 1.568 Pixel.
- Der Schrittweite zwischen zwei Kacheln entspricht der halben Kachelbreite
  (**50 % Überlappung**). Text, der auf einer Naht liegt, liegt dadurch
  vollständig in der Nachbarkachel. Bei einer medianen Textbreite von 374
  Pixeln (99 %-Quantil 2.346) ist diese Überlappung nötig, sonst entstünden an
  jeder Naht abgeschnittene Fragen.
- Die letzte Kachel wird bündig an den rechten Rand gezogen, damit kein
  Reststreifen unter der Mindestbreite bleibt.
- Die Kacheln enthalten keine Markierungen und keine eingezeichneten Boxen;
  die x-Offsets jeder Kachel stehen in `tiles.json`, damit Antworten später auf
  Bildpositionen zurückführbar sind.

Daraus entstehen im Mittel 12,3 Kacheln je Bild (VW typisch 29 bis 33, 4W
typisch 7). 378 GT-Instanzen sind breiter als eine Kachel; sie verteilen sich
über mehrere Kacheln, das Item bleibt aber in der Regel in mindestens einer
Kachel lesbar.

## 6. Was ein „Request" ist

Ein *Request* ist ein einzelner HTTPS-Aufruf an die Jev-API
(`POST https://api.typesafe.ai/v1/systemone`). Er trägt vier Bestandteile:

- `model` — fest auf `jev-1.14.0` gesetzt, weil `jev-latest` wandert;
- `state` — ein Kurzname des Falls; er gruppiert logisch zusammengehörige
  Aufrufe;
- `assets` — die Bilder als Base64-JPEG, jedes mit einem Namen (`tile00`…);
- `questions` — je Frage ein Objekt mit `type: choice`, einer `instructions`
  und zwei `criteria` (`yes`, `no`), also den beiden Antwortoptionen.

Jev antwortet nicht in Freitext, sondern wählt eine Option und liefert die
Wahrscheinlichkeiten aller Optionen zurück (`probabilities.yes`,
`probabilities.no`). Gespeichert werden gewählte Option, `p_yes` und
`confidence`. Zusätzlich verlangt jeder Aufruf mit Bild den Header
`TypeSafe-Danger-Zone-Images: true`, sonst antwortet die API mit 400.
Der Runner setzt ferner eine *Budget-Wache* (Abbruch oberhalb einer Kumulgrenze)
und ein *Resume* über die *image_id*, und er führt mehrere Aufrufe parallel aus
(Standard sechs).

Entscheidend für alle Kostenrechnungen ist eine Messung, die erst im Verlauf
gelang: **Jev berechnet das Bild pro Frage neu**. Ein Aufruf mit einer Kachel
und einer Frage kostet 6.665 *Input-Token*; derselbe Aufruf mit fünf Fragen
kostet 32.086 Token, also fast das Fünffache. Mehrere Fragen in einem Aufruf
sparen folglich nur HTTP-Rundreisen, nicht Bildkosten. Die Kosten hängen am
Produkt aus Fragen und Bildfläche. Für die Frage aus dem Vorfeld, ob man eine
oder mehrere Fragen pro Request stellen soll, heißt das: mehrere Fragen sind
technisch möglich und werden gebündelt, aber der Spareffekt ist begrenzt.

Ebenso gemessen: Ein Request darf höchstens etwa sechs Bilder und etwa 32.000
Input-Token tragen. Ab sieben Bildern antwortet die API mit
`400 Invalid image request`, ab etwa 32.000 Token mit `400
max_tokens_exceeded`. Zusätzlich muss **jedes** Bild im Request in jeder Frage
referenziert werden, sonst kommt derselbe `Invalid image request`. Der Runner
arbeitet daher mit *Kachelgruppen* von höchstens sechs Kacheln und einer
*Blockgröße*, die so gewählt wird, dass der Aufruf unter einer Arbeitsgrenze
von 24.000 Token bleibt. Initial zu groß gewählte Blöcke halbiert er bei einer
Ablehnung selbsttätig.

Der Preis liegt bei 0,042 USD je Million Input-Token; gemessen wurden rund
2.743 Token je Megapixel Bildfläche, also etwa 0,000115 USD je Megapixel. Eine
VW-Kachel (700 × 280) kostet rund 0,0002 USD je Frage, eine 4W-Kachel
(1.568 × 627) rund 0,0008 USD je Frage.

## 7. Grenzmessungen

Vor dem Hauptlauf wurden die Grenzen systematisch ausgemessen, mit 34 einzelnen
Requests (`scripts/03b_probe_limits.py` bis `03e_probe_minimal.py`, Rohdaten in
`outputs/runs/probe*.json`). Die Befunde stehen in `docs/limits.md`:

- Eine Kachel plus 20 Fragen scheitert bereits an `max_tokens_exceeded`, eine
  winzige Kachel (300 × 280) trägt 30 Fragen, 200 nicht mehr.
- Sechs Kacheln (1.568 × 1.000) plus eine Frage laufen mit 24.621 Token durch,
  zehn Kacheln scheitern.
- Sieben bis neun winzige Kacheln scheitern ebenfalls — die Grenze liegt bei der
  Bildanzahl, nicht nur am Volumen.
- Die Kürzung der Criteria auf `{"yes":"y","no":"n"}` ist zulässig und spart
  Text, der Frage-Overhead von rund 300 Token je Frage bleibt aber bestehen.

## 8. Ablauf der Läufe

Gelaufen sind zwei Stufen, beide mit *any-tile-Pooling*: Ein Item gilt für ein
Bild als erkannt, wenn irgendeine Kachelgruppe `yes` liefert; `p_yes` wird als
Maximum über die Gruppen gespeichert, damit die Kalibrierung auswertbar bleibt.

Der **Pilot** umfasste zwei Bilder (je eines pro Gruppe) mit dem vollen
Katalog, also 824 Fragen je Bild, und diente der Ende-zu-Ende-Prüfung. Er
kostete 0,094 USD für das 4W-Bild und 0,614 USD für das VW-Bild (dort 4.944
Antworten über sechs Kachelgruppen) und legte den Mechanismus der
Bildabrechnung offen.

Der **Messlauf** umfasste ein Startset von 12 VW- und 12 4W-Bildern, gezogen
äquidistant über die sortierte Bildliste, mit einem auf 250 Items reduzierten
Katalog (alle Items mit mindestens drei Vorkommen, das sind 90 % der
GT-Instanzen). Er lief bis zur Budget-Wache: fertig wurden 12 4W- und 3
VW-Bilder, 15 Bilder mit 3.750 Bild-Item-Paaren und 9.250 Rohantworten.

## 9. Ergebnisse

Auf dem Messlauf, exakter Vergleich: *Accuracy* 0,940, *Precision* 0,361,
*Recall* 0,947, *F1* 0,522, *ECE* 0,107. Containment-tolerant: Accuracy 0,959,
Precision 0,698, Recall 0,825, F1 0,756, ECE 0,064 (Details in
`docs/run24.md`).

Der Recall ist in beiden Konventionen sehr hoch, die Precision ist der
schwache Wert. Die Zerlegung zeigt drei Ursachen:

- **Ein-Zeichen-Items sind unbrauchbar.** n = 30, kein einziger Treffer, 28
  *False Positives*, Accuracy 0,067, ECE 0,870. `5`, `6`, `55` und `60` werden
  praktisch immer bejaht, weil sie in `ALPIN6` oder `205/55R16` stecken.
- **Häufige Items** (auf mehr als 50 Bildern) erreichen Recall 0,985 bei
  Precision 0,620, **seltene Items** (1–10 Bilder) Precision 0,137 bei Recall
  0,926 — das Pooling über 7 bis 33 Kacheln je Bild erzeugt viele Gelegenheiten
  für ein Ja.
- **Lange Strings** sind die echte Modellschwäche: `ContiWinterContact TS 800`,
  `TS 850 P`, `PILOT ALPIN 5` und `PIRELLI` sind die häufigsten *False
  Negatives*, während Fragmente massenhaft bejaht werden.

## 10. Kosten

Gemessen, aus den Laufzeilen: 4W 0,197 USD je Bild, VW 0,400 USD je Bild bei
250 Items. Der Unterschied kommt vom Format: VW-Streifen sind flacher und
brauchen rund 29 bis 33 Kacheln, 4W-Streifen nur rund 7. Auf 557 Bilder
hochgerechnet sind das 168 USD mit der (zu klein gewählten) Blockgröße des
Messlaufs und etwa 84 USD mit der korrigierten, sparsameren Blockgröße. Mit dem
vollen Katalog von 824 Items verdoppelt bis verdreifacht sich das auf 277 bis
555 USD, sparsam gerechnet etwa 180 USD.

Verbraucht sind 4,30 von 5,00 USD des Testschlüssels: 0,0046 USD für die
Grenzmessungen, 0,708 USD für den Pilot und 3,561 USD für den Messlauf. Die
Aufstellung steht in `outputs/token_kosten.xlsx`; die Projektionen in
`docs/charts/projektion_vollauf.png`.

Ein Vollauf ist ohne Aufstockung nicht möglich. Die Optionen, alle mit dem
gleichen Messaufbau: voller Katalog mit 824 Items (etwa 180 bis 280 USD),
250 Items (etwa 84 bis 168 USD), 170 Items mit mindestens fünf Vorkommen
(etwa 57 bis 114 USD, 86 % der GT-Instanzen) oder 111 Items als Stichprobe aus
allen Positiven plus 100 Zufallsnegativen je Bild (etwa 37 bis 75 USD).

## 11. Was noch offen ist

Drei Entscheidungen liegen beim Nutzer und sind noch nicht getroffen: der
Budget-Scope, die Metrik-Konvention (beide parallel, nur containment-tolerant,
Katalogbereinigung oder nur exakt) und die Pooling-Schwelle (any-tile,
any-tile mit Sensitivitätslauf oder strenge Schwelle ab zwei Gruppen). Als
Voreinstellung implementiert sind beide Metriken, any-tile-Pooling und
zusätzlich eine Sensitivitätsauswertung mit strengerer Schwelle. Unabhängig
davon empfiehlt sich, Ein-Zeichen-Items aus dem Katalog zu nehmen und
Randfragmente auf ihren Trägertext abzubilden.

## 12. Reproduzierbarkeit

Die Pipeline ist numeriert und ohne API-Zugriff bis zum Lauf wiederholbar:
`00_resolve_subset.py` (Pfade), `01_build_ground_truth.py` (GT und Katalog),
`06_select_run_sets.py` (Teilkatalog, Bildstichprobe), `02_make_tiles.py`
(Kacheln), `03_jev_item_existence.py` (Lauf, benötigt den Schlüssel in
`~/TypeSafe-Keys/Jev-Test-Key.txt`), `04_evaluate.py` (Auswertung),
`05_cost_model.py` (Projektion), `07_berichte.py` (Diagramme, diese Tabelle,
Präsentation). Kacheln und Vorschauen sind nicht versioniert, sie entstehen aus
den Skripten neu.

---

# Fachwortverzeichnis

**Accuracy** — Anteil aller richtigen Antworten (richtig ja plus richtig nein)
an allen Antworten. Bei stark ungleichen Klassen, wie hier mit 824 Fragen und
im Schnitt 11 echten Treffern je Bild, ist sie hoch, ohne viel auszusagen.

**Annotation-Lücke** — Der Ground Truth enthält nur annotierten Text. Sichtbarer
nicht annotierter Text auf dem Reifen erzeugt *False Positives*, die kein
Modellfehler sind.

**any-tile-Pooling** — Auswertungsregel dieses Experiments: Ein Item gilt als
erkannt, wenn irgendeine Kachelgruppe es bejaht. Sie erhöht den Recall und
erhöht zugleich die Zahl der *False Positives*.

**AR (aspect ratio, Seitenverhältnis)** — Breite geteilt durch Höhe eines Bildes.
Jev erlaubt höchstens 2,5; die Panoramen erreichen 45, deshalb die Kachelung.

**Asset** — Ein Bild im Request, benannt (`tile00`, `tile01`…). Jedes Asset muss
in jeder Frage des Requests referenziert werden.

**Blockgröße (Q)** — Zahl der Fragen, die der Runner in einen Request packt. Sie
wird aus der Kachelgröße berechnet (Ziel: 55 Kachel-Frage-Paare, unter 24.000
Token) und bei Ablehnung halbiert.

**Budget-Wache** — Abbruchbedingung des Runners: Überschreitet die kumulierte
Summe im Ledger die Grenze, wird kein weiteres Bild begonnen.

**Choice-Frage** — Frageform der Jev-API mit vorgegebenen Optionen. Hier immer
zwei Optionen, `yes` und `no`; die Antwort ist eine der Optionen plus
Wahrscheinlichkeiten.

**containment-tolerant** — Zweite, mildere GT-Konvention: Ein Item zählt als
vorhanden, wenn es in einem GT-String steckt oder einen GT-String enthält.
Bildet Fragment-Items fair ab.

**Criteria** — Die Antwortoptionen einer Choice-Frage mit Beschreibung. Müssen
sich pro Frage unterscheiden, weil Jev Fragen mit identischem Criteria
dedupliziert (dann fehlt eine Antwort).

**Danger-Zone-Header** — Pflicht-Header `TypeSafe-Danger-Zone-Images: true` bei
jedem Request mit Bild; ohne ihn antwortet die API mit 400.

**DOT** — Kennung auf der Reifenflanke (Herstellercode, Produktionswoche). Im
Katalog als Ziffernfolge enthalten.

**ECE (Expected Calibration Error)** — Maß dafür, wie weit die gemeldeten
Wahrscheinlichkeiten von der Trefferquote entfernt sind. 0 ist perfekt
kalibriert. Hohe Werte bei Ein-Zeichen-Items zeigen selbstsichere Fehler.

**F1** — Harmonisches Mittel aus Precision und Recall.

**False Negative / False Positive (FN/FP)** — Item ist vorhanden und wird
verneint (FN) beziehungsweise Item fehlt und wird bejaht (FP).

**Fragment** — Am Bildrand abgeschnittener Text, der als eigener String
annotiert wurde (`ICHELIN`, `UTSIDE`, `ntal`). Im Katalog als Item enthalten.

**Ground Truth (GT)** — Sollwert. Hier: Menge der annotierten Texte je Bild, aus
den Labels abgeleitet, mit Box und Randmerker.

**image_id** — Dateiname ohne Endung; Schlüssel für Resume, GT-Zuordnung und
Auswertung.

**Input-Token** — Abgerechnete Eingabemenge eines Requests, Bildanteil
eingeschlossen. Grundlage jeder Kostenrechnung.

**Invalid image request** — Fehler 400 der API bei mehr als sechs Bildern pro
Request oder bei einem Bild, das in einer Frage nicht referenziert wird.

**Jev** — Proprietäres Entscheidungsmodell von TypeSafe (Version 1.14.0), das
statt Freitext eine Option aus vorgegebenen Kriterien wählt.

**Kachel / Kachelgruppe** — Waagerechter Ausschnitt des Panoramas mit erhaltener
Höhe (Kachel) beziehungsweise die bis zu sechs Kacheln, die ein Request trägt
(Kachelgruppe).

**Katalog** — Menge aller abfragbaren Items: 824 Strings aus den Labels des
Subsets, casefold-dedupliziert.

**Ledger** — Datei mit der kumulierten Kostensumme, Grundlage der Budget-Wache.

**max_tokens_exceeded** — Fehler 400 der API bei zu großem Request, praktisch ab
etwa 32.000 Input-Token.

**Mpx (Megapixel)** — Eine Million Bildpixel. Kostenmaß: rund 2.743 Token je
Mpx.

**p_yes** — Von Jev gemeldete Wahrscheinlichkeit für die Option `yes`. Grundlage
für ECE und für Schwellenwertvarianten.

**Precision** — Anteil der bejahten Items, die tatsächlich vorhanden sind.
Sinkt durch Fragmente und Annotation-Lücken.

**Recall** — Anteil der vorhandenen Items, die bejaht werden.

**Request** — Ein einzelner HTTPS-Aufruf an die Jev-API mit Modell, State,
Assets und Fragen. Das Bild wird dabei pro Frage abgerechnet.

**Resume** — Wiederaufsetzen eines Laufs über die bereits bearbeiteten
`image_id`s, ohne Antworten doppelt zu erzeugen.

**State** — Kurzname im Request, der zusammengehörige Aufrufe logisch gruppiert.

**Subset / all_test.txt** — Testanteil des Bestands, 557 Bildzeilen (289 VW, 268
4W). Unverändert als Kopie im Arbeitsverzeichnis.

**Token/Mpx** — Gemessene Tokenmenge je Megapixel Bildfläche (rund 2.743); über
den Preis umgerechnet 0,000115 USD je Mpx.

**Überlappung** — Anteil, um den sich benachbarte Kacheln doppeln (hier 50 %),
damit Text auf Nähten nicht verloren geht.

**4W** — Bestandsgruppe „4 Wheels“, hohe Streifen (1.436–1.700 px), etwa 7
Kacheln je Bild.

**VW** — Bestandsgruppe „VW“, flache Streifen (278–600 px), etwa 29–33 Kacheln
je Bild und dadurch teurer.
