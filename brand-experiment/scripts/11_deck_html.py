#!/usr/bin/env python3
"""11 — HTML-Präsentation des Brand-Experiments (selbsttragend, 1920×1080)."""
from __future__ import annotations
import base64, mimetypes
from pathlib import Path

ROOT = Path("/home/iiot/data/jev-analysis/brand-experiment")
OUT = ROOT / "docs/praesentation.html"


def img(path: Path, alt: str) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f'<img src="data:{mime};base64,{b64}" alt="{alt}">'


S = []  # (klasse, inneres HTML)

S.append(("titel", """
  <p class="kicker">Messbericht · Brand-Experiment · Jev 1.14 (API) · 23.11.2026</p>
  <h1>Welche Marke trägt<br>der Reifen?</h1>
  <p class="lead">100 Bilder des VW/4W-Testsubsets, eine Multiple-Choice-Frage über die
  Markenliste, abgearbeitet auf Kachelgruppen. Ergebnis: Jev erkennt die Marke
  auf 98 von 100 Bildern richtig — und das Experiment zeigt, was eine
  unvollständige Optionsliste anrichtet.</p>
  <p class="leise">← → blättern · P drucken</p>"""))

S.append(("", """
  <p class="nr">01 — Frage und Sollwert</p>
  <h2>Zuordnung statt Existenz</h2>
  <div class="zwei">
    <ul class="liste">
      <li>Frage je Kachelgruppe: <em>„Which brand does this tire belong to?"</em> — genau eine Option wählen</li>
      <li>Optionsliste: 14 annotierte Marken alphabetisch + „KEINE MARKE LESBAR"</li>
      <li>Sollwert aus den Labels: genau ein exakter Markenname je Bild</li>
      <li>8 Bilder ohne Markenannotation: per Sichtprüfung als Goodyear geklärt</li>
    </ul>
    <div class="kasten">
      <p class="klein">Test-Set</p>
      <p class="gross">100</p>
      <p class="klein">Bilder · 44 VW / 56 4W</p>
      <hr>
      <p class="klein">Marken</p>
      <p class="gross">15</p>
      <p class="klein">14 aus den Labels + Goodyear (Sichtprüfung)</p>
    </div>
  </div>
  <p class="fuss">Kein Bild des Subsets trägt zwei verschiedene Markennamen — geprüft, nicht angenommen.</p>"""))

S.append(("bild", f"""
  <p class="nr">02 — Aufbau</p>
  <h2>Je Kachelgruppe eine Entscheidung</h2>
  <div class="bildrahmen">{img(ROOT / "docs/charts/b_je_marke.png", "Verteilung je Marke")}</div>
  <p class="fuss">Bestandsgetreue Verteilung: Bridgestone 33, Continental 24, Michelin 10 … sieben Ein-Bild-Marken zur Abdeckung</p>"""))

S.append(("bild", f"""
  <p class="nr">03 — Ergebnis</p>
  <h2>98 von 100 richtig</h2>
  <div class="bildrahmen">{img(ROOT / "docs/charts/b_regeln.png", "Regeln im Vergleich")}</div>
  <p class="fuss">Leitmetrik Mittel-wahrscheinlichkeit (Nutzerwahl) · any-tile findet die Marke auf jedem Bild · Mehrheit bestraft uneinige Gruppen</p>"""))

S.append(("bild", f"""
  <p class="nr">04 — Befund</p>
  <h2>Die Optionsliste entscheidet</h2>
  <div class="bildrahmen">{img(ROOT / "docs/charts/b_nachlauf.png", "Nachlauf")}</div>
  <p class="fuss">8 Goodyear-Bilder: ohne Goodyear in der Liste 0/8 richtig, mit Goodyear 7/8 (any-tile 8/8) — ein Choice-Modell kann fehlende Optionen nicht benennen</p>"""))

S.append(("", """
  <p class="nr">05 — Kosten</p>
  <h2>0,128 USD für das ganze Experiment</h2>
  <div class="zwei">
    <ul class="liste">
      <li>Pilot (5 Bilder): <strong>0,005 USD</strong></li>
      <li>Hauptlauf (100 Bilder, 332 Kachelgruppen): <strong>0,111 USD</strong></li>
      <li>Nachlauf (8 Bilder, erweiterte Liste): <strong>0,012 USD</strong></li>
      <li>je Bild rund 0,001 USD — eine Frage je Kachelgruppe statt 250 Fragen je Kachel wie im Katalog-Experiment</li>
    </ul>
    <div class="kasten">
      <p class="klein">Restbudget Test-Key</p>
      <p class="gross">4,87&nbsp;$</p>
      <p class="klein">von 5,00 $ · beide Experimente zusammen</p>
    </div>
  </div>
  <p class="fuss">Kachelformat identisch zum Katalog-Experiment: Höhe ≤ 627 px, AR 2,5, 50 % Überlappung.</p>"""))

S.append(("", """
  <p class="nr">06 — Schlussfolgerung</p>
  <h2>Was das Experiment trägt — und was es lehrt</h2>
  <ul class="liste">
    <li><strong>98/100</strong> richtige Marken mit vollständiger Optionsliste; die 2 Fehler sind uneinige Kachelgruppen, keine Verwechslungen</li>
    <li><strong>Optionslisten aus dem Gesamtbestand</strong> ableiten, nicht aus dem Subset — fehlende Marken sind strukturell unerkennbar</li>
    <li>Ausweitbarkeit: 557 Bilder wären bei gleicher Strategie <strong>unter 1 USD</strong></li>
    <li>Kalibrierung mäßig (ECE 0,169 im Hauptlauf) — harte Entscheidungen sind zuverlässiger als die Wahrscheinlichkeiten</li>
  </ul>
  <p class="fuss">Dokumentation: docs/dokumentation.md · Abstract: docs/abstract.md · Rohdaten: outputs/runs/</p>"""))


def build() -> Path:
    folien = "".join(
        f'<section class="folie {k}" data-n="{i+1}">{inner}</section>'
        for i, (k, inner) in enumerate(S))
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Brand-Experiment — Markenerkennung mit Jev</title>
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
  #deckskal {{ position:static; transform:none !important; margin:0 auto; width:1920px; height:1080px; }}
  .folie {{ position:relative; opacity:1; visibility:visible; page-break-after:always; height:1080px; }}
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
let i=Math.min(+(localStorage.getItem('brandDeckFolie')||0), folien.length-1);
function zeige(n){{
  i=Math.max(0,Math.min(folien.length-1,n));
  folien.forEach((f,k)=>f.classList.toggle('aktiv',k===i));
  document.getElementById('pos').textContent=i+1;
  document.getElementById('fortschritt').style.width=((i+1)/folien.length*100)+'%';
  localStorage.setItem('brandDeckFolie',i);
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
