#!/usr/bin/env python3
"""10 — Diagramme des Brand-Experiments (Accuracy je Regel, je Marke, Nachlauf-Befund)."""
from __future__ import annotations
import collections, json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("/home/iiot/data/jev-analysis/brand-experiment")
CH = ROOT / "docs/charts"
GRUEN, ROT, BLAU, GRAU = "#2e7d32", "#c62828", "#1565c0", "#607d8b"
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": .3})

ev = json.loads((ROOT / "outputs/eval/brand_voll_eval.json").read_text(encoding="utf-8"))


def chart_regeln() -> Path:
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    labels, werte = [], []
    for k, lab in (("any_tile", "any-tile"), ("mittel_p", "Mittel-w.\n(Leitmetrik)"), ("mehrheit", "Mehrheit")):
        labels.append(lab)
        werte.append(ev["uebersicht"][k]["richtig"])
    bars = ax.bar(labels, werte, color=[GRUEN, BLAU, GRAU])
    ax.set_ylim(0, 112); ax.set_ylabel("richtig erkannte Bilder")
    for b, v in zip(bars, werte):
        ax.text(b.get_x() + b.get_width() / 2, v + 3.5, f"{v}/100", ha="center",
                fontsize=10, fontweight="bold", va="bottom")
    ax.set_title("Markenerkennung über 100 Bilder\n(nach Auswertungsregel)")
    p = CH / "b_regeln.png"; fig.tight_layout(); fig.savefig(p, dpi=150); plt.close(fig)
    return p


def chart_je_marke() -> Path:
    jm = ev["je_marke"]
    marken = sorted(jm, key=lambda m: -jm[m]["n"])
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    n = [jm[m]["n"] for m in marken]
    anyv = [jm[m]["any"] * 100 for m in marken]
    mp = [jm[m]["mittel_p"] * 100 for m in marken]
    x = range(len(marken))
    ax.bar([i - 0.2 for i in x], n, 0.4, color=GRAU, label="Bilder im Test-Set")
    ax.bar([i + 0.2 for i in x], mp, 0.4, color=BLAU, label="richtig (Mittel-w.)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(marken, rotation=38, ha="right", fontsize=9)
    ax.set_ylabel("Bilder")
    ax.set_title("Je Marke: Bestand und richtige Erkennung (Leitmetrik)")
    ax.legend(fontsize=8)
    p = CH / "b_je_marke.png"; fig.tight_layout(); fig.savefig(p, dpi=150); plt.close(fig)
    return p


def chart_nachlauf() -> Path:
    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    szenen = ["Hauptlauf\n(ohne Goodyear\nin Optionen)", "Nachlauf\n(mit Goodyear\nin Optionen)"]
    werte = [0, 7]   # Mittel-wahrscheinlichkeit (Leitmetrik)
    any8 = [0, 8]    # any-tile
    x = range(2)
    ax.bar([i - 0.18 for i in x], werte, 0.36, color=ROT, label="richtig (Mittel-w., Leitmetrik)")
    ax.bar([i + 0.18 for i in x], any8, 0.36, color=GRUEN, label="richtig (any-tile)")
    for i, (w, a) in enumerate(zip(werte, any8)):
        ax.text(i - 0.18, w + 0.25, f"{w}/8", ha="center", fontsize=9)
        ax.text(i + 0.18, a + 0.25, f"{a}/8", ha="center", fontsize=9)
    ax.set_xticks(list(x)); ax.set_xticklabels(szenen, fontsize=9)
    ax.set_ylim(0, 10.5); ax.set_ylabel("richtig erkannte Goodyear-Bilder")
    ax.set_title("8 Goodyear-Bilder: Optionsliste entscheidet", pad=8)
    fig.subplots_adjust(bottom=0.34)
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=2, frameon=False)
    p = CH / "b_nachlauf.png"; fig.savefig(p, dpi=150); plt.close(fig)
    return p


def main() -> int:
    CH.mkdir(parents=True, exist_ok=True)
    for f in (chart_regeln(), chart_je_marke(), chart_nachlauf()):
        print(f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
