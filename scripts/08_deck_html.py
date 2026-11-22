#!/usr/bin/env python3
"""08 — HTML-Präsentation (selbsttragend, 1920×1080, Tastatur-Navigation).

Ersetzt die frühere .pptx. Diagramme werden als Data-URI eingebettet, damit die
Datei allein lauffähig ist. Ausgabe docs/praesentation.html.
"""
from __future__ import annotations
import base64, mimetypes
from pathlib import Path

ROOT = Path("/home/iiot/data/jev-analysis")
OUT = ROOT / "docs/praesentation.html"


def img(path: Path, alt: str) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f'<img src="data:{mime};base64,{b64}" alt="{alt}">'


S = []  # (klasse, inneres HTML)

S.append(("titel", """
  <p class="kicker">Messbericht · Testset VW/4W · Jev 1.14 (API) · 22.11.2026</p>
  <h1>Item-Existenz auf<br>Reifenpanoramen</h1>
  <p class="lead">Ein kalibriertes Entscheidungsmodell wird pro Bild zu jedem von 824 Items
  einzeln gefragt, ob der Text auf dem Reifen zu lesen ist. Hier stehen Aufbau,
  Eingriffe und Kosten — und wo die Messung trägt und wo nicht.</p>
  <p class="leise">← → blättern · P drucken · Zahl der Folien unten rechts</p>"""))

S.append(("", """
  <p class="nr">01 — Frage</p>
  <h2>Was genau gemessen wird</h2>
  <div class="zwei">
    <ul class="liste">
      <li>Frage je Bild × Item: <em>„Is the exact text `X` readable on the tire?“</em></li>
      <li>Antwort nur <code>yes</code>/<code>no</code>, englisch, eine Choice-Frage</li>
      <li>Katalog aus den Labels: 6.803 Instanzen → 824 Items</li>
      <li>Ground Truth aus denselben Labels, Antworten je Paar gespeichert</li>
    </ul>
    <div class="kasten">
      <p class="klein">Testsubset <code>all_test.txt</code></p>
      <p class="gross">557</p>
      <p class="klein">Bilder (289 VW, 268 4W)</p>
      <hr>
      <p class="klein">Katalog</p>
      <p class="gross">824</p>
      <p class="klein">Items · 6.803 Label-Instanzen</p>
    </div>
  </div>
  <p class="fuss">Bildweise Reihenfolge, Resume über <code>image_id</code>, Auswertung gegen GT.</p>"""))

S.append(("", """
  <p class="nr">02 — Datenlage</p>
  <h2>Zwei Probleme, die das Design bestimmen</h2>
  <div class="zwei">
    <div>
      <h3>Bildformat</h3>
      <ul class="liste klein2">
        <li>Panoramen bis 17.906 × 278 px, Seitenverhältnis bis 45</li>
        <li>Jev erlaubt 280–1.568 px je Seite und Seitenverhältnis ≤ 2,5</li>
        <li>Ein Bild passt nie in einen Aufruf → Kachelung erzwungen</li>
      </ul>
    </div>
    <div>
      <h3>Katalog</h3>
      <ul class="liste klein2">
        <li>Labels enthalten Randfragmente: <code>ICHELIN</code>, <code>TUR</code>, <code>6</code></li>
        <li>„Ist <code>ELIN</code> zu lesen?“ ist bei sichtbarem <code>MICHELIN</code> sachlich ja</li>
        <li>Exakter Vergleich bestraft das → zweite, containment-tolerante Metrik</li>
      </ul>
    </div>
  </div>
  <p class="fuss">Zusätzlich: nicht annotierter Text auf dem Reifen ist sichtbar und erzeugt Treffer ohne GT.</p>"""))

S.append(("bild", f"""
  <p class="nr">03 — Eingriff</p>
  <h2>Kachelung</h2>
  <div class="bildrahmen">{img(ROOT / "docs/charts/kachelung.jpg", "Panorama und Kacheln")}</div>
  <p class="fuss">Höhe auf 627 px begrenzt · Breite 2,5 × Höhe · 50 % Überlappung · keine Markierungen · Offsets protokolliert</p>"""))

S.append(("bild", f"""
  <p class="nr">04 — Eingriff</p>
  <h2>Request-Grenzen</h2>
  <div class="bildrahmen">{img(ROOT / "docs/charts/grenzen_request.png", "Request-Grenzen")}</div>
  <p class="fuss">34 Grenzmessungen: ab ~32.000 Token <code>max_tokens_exceeded</code>, ab 7 Bildern <code>invalid image request</code> → Kachelgruppen ≤ 6</p>"""))

S.append(("bild", f"""
  <p class="nr">05 — Befund</p>
  <h2>Das Bild wird pro Frage abgerechnet</h2>
  <div class="bildrahmen">{img(ROOT / "docs/charts/bild_pro_frage.png", "Token je Frage")}</div>
  <p class="fuss">1 Frage 6.665 Token, 5 Fragen 32.086 → Bündeln spart nur HTTP-Aufrufe, keine Bildkosten</p>"""))

S.append(("bild", f"""
  <p class="nr">06 — Eingriff</p>
  <h2>Blockgröße korrigiert</h2>
  <div class="bildrahmen">{img(ROOT / "docs/charts/kosten_je_bild.png", "Kosten je Bild")}</div>
  <p class="fuss">Erst zu klein geschätzt (Q ≈ 3, teuer), dann skalenfrei auf 55 Kachel-Frage-Paare je Aufruf — VW-Streifen brauchen ~30 Kacheln, 4W nur 7</p>"""))

S.append(("bild", f"""
  <p class="nr">07 — Kosten</p>
  <h2>Projektion und Restbudget</h2>
  <div class="bildrahmen">{img(ROOT / "docs/charts/projektion_vollauf.png", "Kostenprojektion")}</div>
  <p class="fuss">Gemessen: 4W 0,197 USD/Bild, VW 0,400 USD/Bild bei 250 Items · verbraucht 4,30 von 5,00 USD · ohne Aufstockung kein Vollauf</p>"""))

S.append(("bild", f"""
  <p class="nr">08 — Ergebnis</p>
  <h2>Messlauf: 15 Bilder, 250 Items, 3.750 Paare</h2>
  <div class="bildrahmen">{img(ROOT / "docs/charts/ergebnis_metriken.png", "Metriken")}</div>
  <p class="fuss">Recall 0,95 in beiden Konventionen · Precision 0,36 exakt / 0,70 containment-tolerant · ECE 0,107</p>"""))

S.append(("", """
  <p class="nr">09 — Grenzen</p>
  <h2>Was die Zahlen sagen und was offen ist</h2>
  <div class="zwei">
    <ul class="liste">
      <li><strong>Ein-Zeichen-Items unbrauchbar:</strong> <code>5</code>, <code>6</code>, <code>55</code>, <code>60</code> — Acc 0,067, immer ja</li>
      <li><strong>Echte Schwäche sind lange Strings:</strong> <code>PILOT ALPIN 5</code>, <code>PIRELLI</code></li>
      <li>Seltene Items: Precision 0,14 durch Pooling über 7–33 Kacheln</li>
    </ul>
    <div class="kasten">
      <p class="klein">Offen — Entscheidung beim Nutzer</p>
      <ul class="liste klein2">
        <li>Scope: 824 / 250 / 170 / 111 Items</li>
        <li>Metrik: beide · nur loose · Katalog bereinigen · nur exakt</li>
        <li>Pooling: any-tile · mit Sensitivitätslauf · strenge Schwelle</li>
      </ul>
    </div>
  </div>
  <p class="fuss">Empfehlung: containment-tolerantes GT führen, Ein-Zeichen-Items entfernen, Randfragmente auf Trägertexte abbilden.</p>"""))


def build() -> Path:
    folien = "".join(
        f'<section class="folie {k}" data-n="{i+1}">{inner}</section>'
        for i, (k, inner) in enumerate(S))
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Item-Existenz auf Reifenpanoramen — Messbericht</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {{
  --papier:#f4f1ea; --ink:#17181a; --muted:#5c5f63; --linie:#c9c3b6;
  --rost:#a63a1c; --tief:#154a48; --karte:#fbfaf7;
}}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; height:100%; background:#26272a; }}
body {{ font-family:"IBM Plex Sans","Segoe UI",system-ui,sans-serif; color:var(--ink); }}
#buehne {{ position:absolute; inset:0; overflow:hidden; }}
#deckskal {{
  position:absolute; left:50%; top:50%; width:1920px; height:1080px;
  transform:translate(-50%,-50%) scale(var(--s,1)); transform-origin:center center;
}}
.folie {{
  position:absolute; inset:0; padding:88px 110px; background:var(--papier);
  display:flex; flex-direction:column; pointer-events:none; visibility:hidden;
}}
.folie.aktiv {{ pointer-events:auto; visibility:visible; }}
.folie::after {{
  content:""; position:absolute; left:0; right:0; bottom:0; height:12px;
  background:linear-gradient(90deg,var(--rost) 0 33%,var(--tief) 33% 66%,var(--linie) 66% 100%);
}}
h1 {{ font-size:74px; line-height:1.03; letter-spacing:-.02em; margin:18px 0 26px; max-width:15em; }}
h2 {{ font-size:48px; line-height:1.1; letter-spacing:-.015em; margin:10px 0 34px; max-width:20em; }}
h3 {{ font-size:26px; margin:0 0 12px; color:var(--tief); }}
p, li {{ font-size:25px; line-height:1.5; }}
.lead {{ font-size:29px; max-width:26em; color:#2a2c2f; }}
.nr {{ font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:20px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--rost); margin:0; }}
.kicker {{ font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:20px; letter-spacing:.06em;
  color:var(--muted); margin:0; }}
.fuss {{ margin-top:auto; font-size:21px; color:var(--muted); max-width:52em; border-top:1px solid var(--linie);
  padding-top:18px; }}
.leise {{ color:var(--muted); font-size:21px; margin-top:22px; }}
code {{ font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:.92em; background:#e7e2d6;
  padding:1px 6px; border-radius:3px; }}
.titel {{ justify-content:center; }}
.zwei {{ display:grid; grid-template-columns:1.35fr .95fr; gap:64px; align-items:start; }}
.liste {{ margin:0; padding-left:26px; }}
.liste li {{ margin-bottom:16px; }}
.klein2 li {{ font-size:23px; }}
.kasten {{ background:var(--karte); border:1px solid var(--linie); padding:26px 28px; }}
.kasten hr {{ border:0; border-top:1px solid var(--linie); margin:16px 0; }}
.klein {{ font-size:19px; color:var(--muted); margin:0; }}
.gross {{ font-size:56px; font-weight:700; margin:2px 0 0; color:var(--tief); font-variant-numeric:tabular-nums; }}
.bild .bildrahmen {{ flex:1; display:flex; align-items:center; justify-content:center; min-height:0; }}
.bild img {{ max-width:100%; max-height:100%; object-fit:contain; border:1px solid var(--linie); background:#fff; }}
#zaehler {{ position:fixed; right:22px; bottom:18px; font-family:"IBM Plex Mono",monospace; font-size:15px;
  color:#c9c3b6; letter-spacing:.08em; }}
#fortschritt {{ position:fixed; left:0; top:0; height:4px; background:var(--rost); transition:width .18s linear; }}
@media print {{
  #zaehler,#fortschritt {{ display:none; }}
  html,body {{ background:#fff; }}
  #buehne {{ position:static; display:block; }}
  #deckskal {{ transform:none !important; width:1920px; height:1080px; }}
  .folie {{ position:relative; opacity:1; visibility:visible; page-break-after:always; height:1080px; }}
  #deckskal {{ position:static; transform:none !important; margin:0 auto; }}
}}
@media (prefers-reduced-motion:reduce) {{ .folie {{ transition:none; }} }}
</style>
</head>
<body>
<div id="fortschritt"></div>
<div id="buehne"><div id="deckskal">{folien}</div></div>
<div id="zaehler"><span id="pos">1</span> / {len(S)}</div>
<script>
const folien=[...document.querySelectorAll('.folie')];
let i=Math.min(+(localStorage.getItem('jevDeckFolie')||0), folien.length-1);
function zeige(n){{
  i=Math.max(0,Math.min(folien.length-1,n));
  folien.forEach((f,k)=>f.classList.toggle('aktiv',k===i));
  document.getElementById('pos').textContent=i+1;
  document.getElementById('fortschritt').style.width=((i+1)/folien.length*100)+'%';
  localStorage.setItem('jevDeckFolie',i);
}}
function skalieren(){{
  const s=Math.min(innerWidth/1920, innerHeight/1080);
  document.getElementById('deckskal').style.setProperty('--s', s);
}}
addEventListener('resize',skalieren);
addEventListener('keydown',e=>{{
  if(['ArrowRight','ArrowDown',' ','PageDown'].includes(e.key)){{e.preventDefault();zeige(i+1);}}
  if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){{e.preventDefault();zeige(i-1);}}
  if(e.key==='Home')zeige(0);
  if(e.key==='End')zeige(folien.length-1);
  if(e.key.toLowerCase()==='p')print();
}});
addEventListener('click',e=>zeige(e.clientX>innerWidth*0.25?i+1:i-1));
skalieren(); zeige(i);
</script>
</body>
</html>
"""
    OUT.write_text(html, encoding="utf-8")
    return OUT


if __name__ == "__main__":
    p = build()
    print(f"{p} ({p.stat().st_size/1024:.0f} kB, {len(S)} Folien)")
