"""AP S8: Der Gitterlauf und die Abbildung des Pruefvorlaufs.

Aufruf: python3 s8_abbildung.py [--nur-zeichnen]

Zwei Teile. Erstens laeuft das Gitter aus `dg.sweep.grid.GITTER_PRUEFVORLAUF`
und legt Ergebnis und Manifest unter `runs/<kennung>/` ab. Zweitens zeichnet
dieses Skript daraus `figures/abb-1-pruefvorlauf.svg` und traegt die Abbildung in
`figures/manifest.json` ein, mit der Kennung des Laufs, aus dem sie stammt.

**Damit ist die Regel aus `gliederung.md` Abschnitt 4 eingeloest**, naemlich dass
keine Abbildung ohne Eintrag im Abbildungsmanifest steht und jede eine Kennung
traegt. Kapitel 9.5 ist entsprechend nachzuziehen.

Mit `--nur-zeichnen` wird der letzte vorhandene Lauf gezeichnet, ohne neu zu
rechnen. Der Lauf dauert rund hundert Sekunden.

Arbeitsspur, **nicht** Teil von `src/dg/`.
"""

from __future__ import annotations

import csv
import io
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from dg.sweep import GITTER_PRUEFVORLAUF as GITTER  # noqa: E402
from dg.sweep import lauf_kennung, laufen, schreiben  # noqa: E402

SEED = 20261011
NAVY, GOLD, ICE, STEEL = "#1B2A4A", "#C9A84C", "#CADCFC", "#2C5282"
LINIE, GRAU, PAPIER = "#E2DFD6", "#6B7688", "#FFFFFF"


def lesen(ordner: Path) -> list[dict]:
    with io.open(ordner / "ergebnis.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def zeichnen(zeilen: list[dict], kennung: str) -> str:
    """Die Abbildung als eingebettetes SVG.

    Gezeigt wird, **wo** der Pruefvorlauf positiv ist, nicht wie hoch er ist: Er
    betraegt auf dem ganzen Gitter entweder null oder eine Periode. Genau das ist
    die Aussage, und eine Farbskala wuerde eine Abstufung behaupten, die es nicht
    gibt.
    """
    k_werte = sorted({float(z["k_R"]) for z in zeilen})
    z_werte = sorted({float(z["zeta"]) for z in zeilen}, reverse=True)
    wert = {(float(z["k_R"]), float(z["zeta"])): float(z["pruef_vorlauf_faelle"])
            for z in zeilen}

    links, oben = 86, 80
    zb, zh = 62, 34
    breite = links + len(k_werte) * zb + 24
    hoehe = oben + len(z_werte) * zh + 86

    t = [f'<svg viewBox="0 0 {breite} {hoehe}" xmlns="http://www.w3.org/2000/svg" '
         'role="img" aria-label="Der Pruefvorlauf ueber Pruefkostenverhaeltnis und '
         'Zensurgrad: die Region, in der er positiv ist">']
    t.append(f'<rect x="0" y="0" width="{breite}" height="{hoehe}" fill="{PAPIER}"/>')
    t.append(f'<text x="10" y="20" font-family="Georgia,serif" font-size="13" fill="{NAVY}" '
             'font-weight="bold">Der Prüfvorlauf ist ein Band, und seine untere Kante '
             'ist die Lage der Meinung</text>')
    t.append(f'<text x="10" y="38" font-family="Arial" font-size="10.5" fill="{GRAU}">'
             'Gestoppte Fälle, die am Anfang gegen das myopische Urteil zu prüfen '
             'sind. Leer heißt null.</text>')

    # Spaltenkoepfe
    for j, k in enumerate(k_werte):
        x = links + j * zb
        t.append(f'<text x="{x + zb/2}" y="{oben - 8}" text-anchor="middle" '
                 f'font-family="Arial" font-size="10" fill="{NAVY}">{k:.3f}</text>'.replace(
                     f"{k:.3f}", f"{k:.3f}".replace(".", ",")))
    t.append(f'<text x="{links + len(k_werte)*zb/2}" y="{oben + len(z_werte)*zh + 34}" '
             f'text-anchor="middle" font-family="Arial" font-size="11" fill="{NAVY}" '
             'font-weight="bold">Prüfkostenverhältnis k/R</text>')
    t.append(f'<text x="14" y="{oben + len(z_werte)*zh/2}" font-family="Arial" '
             f'font-size="11" fill="{NAVY}" font-weight="bold" '
             f'transform="rotate(-90 14 {oben + len(z_werte)*zh/2})" '
             'text-anchor="middle">Zensurgrad ζ</text>')

    # Zellen
    for i, z in enumerate(z_werte):
        y = oben + i * zh
        t.append(f'<text x="{links - 10}" y="{y + zh/2 + 4}" text-anchor="end" '
                 f'font-family="Arial" font-size="10.5" fill="{NAVY}">'
                 f'{("%.3f" % z).replace(".", ",")}</text>')
        for j, k in enumerate(k_werte):
            x = links + j * zb
            v = wert[(k, z)]
            fuell = NAVY if v > 0 else "#FAF9F6"
            rand = NAVY if v > 0 else LINIE
            t.append(f'<rect x="{x}" y="{y}" width="{zb}" height="{zh}" fill="{fuell}" '
                     f'stroke="{rand}" stroke-width="1"/>')
            if v > 0:
                t.append(f'<text x="{x + zb/2}" y="{y + zh/2 + 4}" text-anchor="middle" '
                         f'font-family="Arial" font-size="11" fill="{GOLD}" '
                         f'font-weight="bold">{v:.0f}</text>')

    # Die beiden analytischen Marken, an den Zellgrenzen
    def kante(wert_kr: float) -> float:
        """Die x-Stelle einer Marke.

        Trifft die Marke eine Spalte genau, so liegt sie an deren **linker
        Kante**: Die Spalte gehoert dann schon zum Band, und eine Linie durch
        ihre Mitte wuerde eine Grenze innerhalb der Spalte behaupten. Sonst wird
        zwischen den Spaltenmitten geradlinig eingesetzt.
        """
        for j, k in enumerate(k_werte):
            if abs(k - wert_kr) < 1e-9:
                return links + j * zb
        for j in range(len(k_werte) - 1):
            if k_werte[j] <= wert_kr <= k_werte[j + 1]:
                anteil = (wert_kr - k_werte[j]) / (k_werte[j + 1] - k_werte[j])
                return links + (j + 0.5 + anteil) * zb
        return links + 0.5 * zb

    unten_y = oben + len(z_werte) * zh
    for stelle, text in ((GITTER.g_0, "g₀ = 0,05"),
                         (GITTER.g_wahr, "g = 0,093")):
        x = kante(stelle)
        t.append(f'<line x1="{x}" y1="{oben - 24}" x2="{x}" y2="{unten_y + 6}" '
                 f'stroke="{GOLD}" stroke-width="2" stroke-dasharray="4 3"/>')
        t.append(f'<text x="{x + 4}" y="{oben - 28}" font-family="Arial" font-size="10" '
                 f'fill="#AF8E33" font-weight="bold">{text}</text>')

    t.append(f'<text x="10" y="{hoehe - 24}" font-family="Arial" font-size="9.5" '
             f'fill="{GRAU}">Lauf {kennung} · Beispielwerte nach Anhang C: '
             f'π = 0,20, R = 100, L = 50, Stärke 20, δ = 0,95, '
             f'Horizont 30, 150 Ziehungen je Punkt</text>')
    t.append(f'<text x="10" y="{hoehe - 10}" font-family="Arial" font-size="9.5" '
             f'fill="{GRAU}">Der Erkundungsanteil ε* ist auf allen '
             f'{len(zeilen)} Gitterpunkten null.</text>')
    t.append("</svg>")
    return "\n".join(t)


def manifest_schreiben(kennung: str, datei: Path, zeilen: list[dict]) -> None:
    """Traegt die Abbildung ein, mit der Kennung des Laufs, aus dem sie stammt."""
    pfad = Path("figures/manifest.json")
    pfad.parent.mkdir(parents=True, exist_ok=True)
    bestand = {}
    if pfad.exists():
        bestand = json.loads(io.open(pfad, encoding="utf-8").read())
    positiv = sum(1 for z in zeilen if float(z["pruef_vorlauf_faelle"]) > 0)
    bestand["abb-1-pruefvorlauf"] = {
        "datei": str(datei),
        "kapitel": "8.4",
        "titel": "Der Pruefvorlauf ueber Pruefkostenverhaeltnis und Zensurgrad",
        "lauf_kennung": kennung,
        "erzeugt_von": "s8_abbildung.py:zeichnen",
        "gitterpunkte": len(zeilen),
        "punkte_mit_vorlauf": positiv,
    }
    io.open(pfad, "w", encoding="utf-8").write(
        json.dumps(bestand, ensure_ascii=False, indent=2) + "\n")


def main() -> int:
    nur_zeichnen = "--nur-zeichnen" in sys.argv
    kennung = lauf_kennung(GITTER, SEED)
    ordner = Path("runs") / kennung

    if not nur_zeichnen or not (ordner / "ergebnis.csv").exists():
        print(f"Gitter {GITTER.name}, {GITTER.punkte} Punkte, Lauf {kennung}")
        t0 = time.time()
        zaehler = [0]

        def melden(_zeile) -> None:
            zaehler[0] += 1
            if zaehler[0] % len(GITTER.zeta) == 0:
                print(f"  {zaehler[0]:>3}/{GITTER.punkte}  {time.time() - t0:5.0f}s")

        zeilen_typ = laufen(GITTER, seed=SEED, melden=melden)
        ordner = schreiben(zeilen_typ, GITTER, SEED)
        print(f"  abgelegt in {ordner}, {time.time() - t0:.0f}s")

    zeilen = lesen(ordner)
    datei = Path("figures/abb-1-pruefvorlauf.svg")
    datei.parent.mkdir(parents=True, exist_ok=True)
    io.open(datei, "w", encoding="utf-8").write(zeichnen(zeilen, kennung) + "\n")
    manifest_schreiben(kennung, datei, zeilen)

    positiv = sum(1 for z in zeilen if float(z["pruef_vorlauf_faelle"]) > 0)
    print(f"{datei} erzeugt, {positiv} von {len(zeilen)} Punkten mit Vorlauf")
    print("figures/manifest.json fortgeschrieben")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
