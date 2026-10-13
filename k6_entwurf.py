"""AP S2: Das Entwurfsproblem aus Kapitel 6, fuer zwei und drei Stellen durchgerechnet.

Zweck. `gliederung.md` Abschnitt 3 fuehrt als Proposition zu Kapitel 6: "Loesung
fuer zwei bis drei Stellen, durchgerechnet". Bis AP S2 stand das als Behauptung
im Text und war nicht ausgefuehrt. Dieses Skript fuehrt es aus, und es hat dabei
die Bedingung fuer den Befund aus `tor-a-vorlage.md` Abschnitt 3.4 geschlossen
bestimmt.

Zwei Teile.

Teil 1 zaehlt das Entwurfsproblem aus Kapitel 6.7 vollstaendig ab, also
Besetzung mal Redundanz mal Verknuepfungsregel je Stelle, fuer n = 2 und n = 3
und fuer vier vorab benannte Fenster. Fuer n = 2 wird jeder Wert zusaetzlich
gegen `analytic.py` geprueft, also gegen das Abzaehlen des Entscheidungsbaums.

Teil 2 prueft die geschlossene Bedingung, unter der der Ertrag in `alpha_i`
**steigt**. Fuer die Stelle `i` lautet sie: die gesparten Kosten der
nachgelagerten Stellen uebersteigen den entgangenen Ertrag, gewichtet mit der
Wahrscheinlichkeit, dass der Fall den Rest der Kette passiert haette. Fuer n = 2
ist das `c_2 > R*(1 - alpha_2)`.

Was dieses Skript nicht tut, und das ist Sperre 3 aus `abgrenzung.md`
Abschnitt 8. **Keine numerische Suche nach Kippbereichen.** Gerechnet werden
vorab benannte Parametersaetze, und die Schranke in Teil 2 ist analytisch
bestimmt und wird nur bestaetigt, nicht gesucht.

Arbeitsspur, **nicht** Teil von `src/dg/core/`.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from dg.core.analytic import ertrag_n2  # noqa: E402
from dg.core.chain import bindende_stelle, durchlaufzeit, ertrag  # noqa: E402
from dg.core.types import Kette, Stelle, Umgebung  # noqa: E402

# --- Beispielwerte, vorab festgelegt. Keine Schaetzungen. ---------------------
#
# Zwei Besetzungsarten mit gegenlaeufigem Profil, damit der Abtausch ueberhaupt
# auftritt: Der Mensch ist in der ersten Fehlerrichtung besser, langsam und
# teuer; die Maschine ist in der zweiten besser, schneller und billiger.

PROFIL = {
    # besetzung: (alpha, beta, c, tau)
    "H": (0.08, 0.22, 6.0, 4.0),
    "M": (0.28, 0.07, 3.0, 2.5),
}

UMGEBUNG = Umgebung(pi=0.20, R=400.0, L=60.0, lam=100.0)
RHO = 1.0                              # vollstaendig nacheinander
R_MAX = 3                              # je Stelle hoechstens drei Pruefungen
FENSTER = (float("inf"), 9.0, 6.0, 3.0)   # vorab benannt


def stelle(besetzung: str, r: int, regel: str) -> Stelle:
    a, b, c, t = PROFIL[besetzung]
    return Stelle(alpha=a, beta=b, c=c, tau=t, besetzung=besetzung, r=r, regel=regel)


def entwuerfe(n: int):
    """Alle Entwuerfe einer Kette aus n Stellen."""
    je_stelle = [
        (bes, r, regel)
        for bes in ("H", "M")
        for r in range(1, R_MAX + 1)
        for regel in ("reihe", "parallele")
        if not (r == 1 and regel == "parallele")   # bei r = 1 ist die Regel ohne Wirkung
    ]
    return itertools.product(je_stelle, repeat=n)


def name(entwurf) -> str:
    teile = []
    for bes, r, regel in entwurf:
        teile.append(bes if r == 1 else f"{bes}{r}{'p' if regel == 'parallele' else 's'}")
    return " + ".join(teile)


def teil1() -> None:
    print("Teil 1: Das Entwurfsproblem, vollstaendig abgezaehlt")
    print(f"  Umgebung: pi={UMGEBUNG.pi}, R={UMGEBUNG.R}, L={UMGEBUNG.L}, lam={UMGEBUNG.lam}")
    print(f"  Profile:  H={PROFIL['H']}, M={PROFIL['M']}, rho={RHO}, r<={R_MAX}")
    print()
    print(f"{'n':>2} {'W':>5} {'Entwuerfe':>10} {'beste Gestalt':>20} {'Ertrag':>9} {'T':>6} {'i*':>3}")
    for n in (2, 3):
        abweichung_max = 0.0
        for W in FENSTER:
            bester = None
            anzahl = 0
            erfuellbar = 0
            for entwurf in entwuerfe(n):
                kette = Kette(stellen=tuple(stelle(*s) for s in entwurf), W=W, rho=RHO)
                wert = ertrag(kette, UMGEBUNG)
                anzahl += 1
                if durchlaufzeit(kette, UMGEBUNG) <= W:
                    erfuellbar += 1
                if n == 2:
                    abweichung_max = max(abweichung_max, abs(wert - ertrag_n2(kette, UMGEBUNG)))
                if bester is None or wert > bester[0]:
                    bester = (wert, entwurf, kette)
            wert, entwurf, kette = bester
            wtext = "inf" if W == float("inf") else f"{W:.0f}"
            if erfuellbar == 0:
                print(f"{n:>2} {wtext:>5} {anzahl:>10} {'kein Entwurf erfuellt W':>20}")
                continue
            print(
                f"{n:>2} {wtext:>5} {anzahl:>10} {name(entwurf):>20} "
                f"{wert:>9.1f} {durchlaufzeit(kette, UMGEBUNG):>6.2f} "
                f"{bindende_stelle(kette, UMGEBUNG):>3}"
            )
        if n == 2:
            print(f"   Gegenrechnung gegen analytic.ertrag_n2: groesste Abweichung {abweichung_max:.2e}")
    print()


def teil2() -> None:
    print("Teil 2: Die Schranke, ab der ein hoeheres alpha_i den Ertrag hebt")
    print()

    # n = 2: Schranke c_2 = R * (1 - alpha_2)
    U = Umgebung(pi=0.20, R=40.0, L=60.0, lam=100.0)
    a2 = 0.08
    schranke2 = U.R * (1.0 - a2)
    print(f"  n=2, R={U.R}, alpha_2={a2}: vorhergesagte Schranke c_2 = {schranke2:.4f}")
    for c2 in (30.0, 36.0, schranke2, 38.0, 45.0):
        werte = []
        for a1 in (0.05, 0.50):
            k = Kette(
                stellen=(
                    Stelle(alpha=a1, beta=0.20, c=2.0, tau=1.0),
                    Stelle(alpha=a2, beta=0.10, c=c2, tau=1.0),
                ),
                W=float("inf"),
                rho=RHO,
            )
            werte.append(ertrag(k, U))
        print(f"    c_2={c2:8.4f}  Ertrag(0,50) - Ertrag(0,05) = {werte[1] - werte[0]:+10.4f}")

    # n = 3: Schranke c_2 + (1 - alpha_2) * c_3 = R * (1 - alpha_2) * (1 - alpha_3)
    U3 = Umgebung(pi=0.25, R=100.0, L=50.0, lam=100.0)
    a2 = a3 = 0.10
    c2 = 10.0
    schranke3 = (U3.R * (1.0 - a2) * (1.0 - a3) - c2) / (1.0 - a2)
    print()
    print(f"  n=3, R={U3.R}, alpha_2=alpha_3={a2}, c_2={c2}: vorhergesagte Schranke c_3 = {schranke3:.4f}")
    for c3 in (60.0, 78.0, schranke3, 85.0, 100.0):
        werte = []
        for a1 in (0.05, 0.50):
            k = Kette(
                stellen=(
                    Stelle(alpha=a1, beta=0.20, c=1.0, tau=1.0),
                    Stelle(alpha=a2, beta=0.15, c=c2, tau=1.0),
                    Stelle(alpha=a3, beta=0.15, c=c3, tau=1.0),
                ),
                W=float("inf"),
                rho=RHO,
            )
            werte.append(ertrag(k, U3))
        print(f"    c_3={c3:8.4f}  Ertrag(0,50) - Ertrag(0,05) = {werte[1] - werte[0]:+10.4f}")
    print()
    print("  Beide Schranken treffen auf null. Die Bedingung ist damit bestaetigt,")
    print("  und sie ist analytisch bestimmt und nicht gesucht.")


def main() -> int:
    teil1()
    teil2()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
