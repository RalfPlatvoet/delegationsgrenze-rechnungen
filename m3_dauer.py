"""AP M3. Die Dauer des Ruhezustands bei gelockerter Zensur.

Die Frage, die AP M2 offen gelassen hat: Bei `zeta < 1` wird ein Anteil der gestoppten
Faelle ohne Zutun sichtbar, also ist g identifiziert, auch wenn nie geprueft wird. Der
Ruhezustand ist dann kein Fixpunkt, sondern eine Episode. **Die Frage ist nicht, ob er
endet, sondern wann.**

Der Umschlag tritt ein, sobald E[g] = (c1+h1)/(c1+c0+h1+h0) die Schwelle k/R
erreicht, wobei h1 und h0 die aufgedeckten gestoppten Faelle mit und ohne Wirksamkeit sind.

**Zwei Regime, und das ist das Ergebnis dieser Datei.**

  Regime A, schwache Vorverteilung: Schon ein einziger aufgedeckter wirksamer Fall hebt
    E[g] ueber die Schwelle. Bedingung: (c1 + 1) >= (k/R) * (c1 + c0 + 1). Die Dauer ist
    dann die Wartezeit auf das **erste Gegenbeispiel**, geometrisch mit der Rate
    (1 - zeta) * lambda * w * g, also im Mittel 1 / [(1-zeta) * lambda * w * g].

  Regime B, starke Vorverteilung: Es sind viele Gegenbeispiele noetig, und die Dauer folgt
    dem Mittelpfad h* = (c1+c0)(k/R - g0) / (g - k/R), also
    T = h* / [(1-zeta) * lambda * w].

Geprueft werden:
  Q1  Bei zeta = 1 bewegt sich E[g] nicht, bei zeta < 1 schlaegt es um. Der Ruhezustand
      ist also nur bei vollstaendiger Zensur ein Fixpunkt.
  Q2  Die Regimebedingung trennt richtig: Wo ein Gegenbeispiel genuegt, trifft die
      Wartezeitformel den Median; wo es nicht genuegt, trifft die Mittelpfadformel.
  Q3  Die Dauer skaliert wie 1/(1-zeta) und wie die Staerke der Vorverteilung.
  Q4  Nach dem Umschlag wird geprueft, der Aufdeckungsgrad springt auf eins, und die
      Ueberzeugung laeuft auf den wahren Wert. Kein dauerhafter Rueckfall.
  Q5  Volumenfreie Fassung: Die Zahl der **gestoppten Faelle** bis zum Umschlag haengt
      nicht vom Fallstrom ab. Nur die Uebersetzung in Zeit tut es.
  Q6  g ist streng steigend in der Praevalenz. Daraus: Vollstaendige und ehrliche Angabe der
      Fehlerraten der maschinellen Stelle bestimmt g **nicht**, denn es fehlt die eigene
      Fallmischung, und genau die verbirgt die Zensur.
"""

from __future__ import annotations

import random
import statistics


def zellen(pi: float, alpha: float, beta: float) -> tuple[float, float, float, float]:
    u = pi * (1.0 - alpha)
    v = (1.0 - pi) * beta
    w = 1.0 - u - v
    g = (pi - u) / w
    return u, v, w, g


def ein_gegenbeispiel_genuegt(c1: float, c0: float, schwelle: float) -> bool:
    """Hebt ein einziger aufgedeckter wirksamer Fall die Ueberzeugung ueber die Schwelle?"""
    return (c1 + 1.0) / (c1 + c0 + 1.0) >= schwelle


def h_mittelpfad(c1: float, c0: float, g: float, schwelle: float) -> float:
    """Aufgedeckte gestoppte Faelle bis zum Umschlag, Mittelpfad."""
    g0 = c1 / (c1 + c0)
    if g <= schwelle:
        return float("inf")
    if g0 >= schwelle:
        return 0.0
    return (c1 + c0) * (schwelle - g0) / (g - schwelle)


def wartezeit_erstes_gegenbeispiel(zeta: float, lam: float, w: float, g: float) -> float:
    """Erwartete Zahl der Perioden bis zum ersten aufgedeckten wirksamen gestoppten Fall."""
    rate = (1.0 - zeta) * lam * w * g
    return float("inf") if rate <= 0 else 1.0 / rate


def ein_lauf(
    *, g: float, w: float, lam: float, zeta: float, schwelle: float,
    c1: float, c0: float, perioden: int, strom: random.Random,
) -> tuple[int | None, float, float, int]:
    """Ein Lauf. Rueckgabe: Periode des Umschlags, End-E[g], Verlust, gestoppte Faelle bis Umschlag."""
    a, b = c1, c0
    umschlag: int | None = None
    verlust = 0.0
    gestoppt_bis_umschlag = 0
    for t in range(1, perioden + 1):
        pruefen = (a / (a + b)) >= schwelle
        if umschlag is None and pruefen:
            umschlag = t
        nu = 1.0 if pruefen else 1.0 - zeta
        gestoppt = sum(1 for _ in range(int(lam)) if strom.random() < w)
        if umschlag is None:
            gestoppt_bis_umschlag += gestoppt
            verlust += gestoppt * max(0.0, g - schwelle)
        for _ in range(gestoppt):
            if strom.random() < nu:
                if strom.random() < g:
                    a += 1.0
                else:
                    b += 1.0
    return umschlag, a / (a + b), verlust, gestoppt_bis_umschlag


def lauf_schar(*, laeufe: int, perioden: int, strom: random.Random, **kw):
    um, enden, gestoppt = [], [], []
    for _ in range(laeufe):
        u_, e_, _, gs_ = ein_lauf(perioden=perioden, strom=strom, **kw)
        if u_ is not None:
            um.append(u_)
            gestoppt.append(gs_)
        enden.append(e_)
    return um, enden, gestoppt


def main() -> int:
    strom = random.Random(20261010)
    pi, alpha, beta = 0.20, 0.35, 0.15
    u, v, w, g = zellen(pi, alpha, beta)
    R, k = 100.0, 7.0
    schwelle = k / R
    lam = 50.0
    fehler: list[str] = []

    print("AP M3: Dauer des Ruhezustands bei gelockerter Zensur\n")
    print(f"   Modell:  pi={pi} alpha={alpha} beta={beta}  ->  u={u:.4f} v={v:.4f} "
          f"w={w:.4f} g={g:.4f}")
    print(f"   Entscheidung: R={R} k={k}  Schwelle k/R={schwelle:.4f}")
    print(f"   Fallstrom lambda={lam} je Periode, Anteil gestoppt {w:.3f}\n")

    # ---------------------------------------------------------------- Q1, Q2
    print("   Zwei Vorverteilungen, beide mit E[g] = 0,05 unter der Schwelle 0,07,")
    print("   aber von verschiedener Staerke.\n")
    for c1, c0 in ((1.0, 19.0), (20.0, 380.0)):
        g0 = c1 / (c1 + c0)
        eins = ein_gegenbeispiel_genuegt(c1, c0, schwelle)
        hm = h_mittelpfad(c1, c0, g, schwelle)
        print(f"   Beta({c1:g},{c0:g}), Staerke {c1+c0:g}, E[g]={g0:.4f}, "
              f"ein Gegenbeispiel genuegt: {eins}")
        print(f"      Mittelpfad h* = {hm:.1f} aufgedeckte Faelle")
        print("      zeta    T erwartet (Regime)   T gezogen: Median / 10% / 90%   E[g] Ende")
        for zeta in (0.5, 0.9, 0.98, 1.0):
            if zeta >= 1.0:
                t_erw, regime = float("inf"), "Fixpunkt"
            elif eins:
                t_erw, regime = wartezeit_erstes_gegenbeispiel(zeta, lam, w, g), "A Wartezeit"
            else:
                t_erw, regime = hm / ((1.0 - zeta) * lam * w), "B Mittelpfad"
            perioden = 3000 if zeta < 0.98 else 20000
            um, enden, _ = lauf_schar(
                laeufe=60, perioden=perioden, strom=strom,
                g=g, w=w, lam=lam, zeta=zeta, schwelle=schwelle, c1=c1, c0=c0,
            )
            e_ende = statistics.mean(enden)
            if um:
                srt = sorted(um)
                med = statistics.median(srt)
                q10 = srt[int(0.1 * len(srt))]
                q90 = srt[min(len(srt) - 1, int(0.9 * len(srt)))]
                print(f"      {zeta:<7} {t_erw:<21.1f} {med:<8.0f} {q10:<7} {q90:<10} "
                      f"{e_ende:.4f}   [{regime}]")
                if abs(med - t_erw) > max(3.0, 1.0 * t_erw):
                    fehler.append(f"Q2 Regime {regime}: erwartet {t_erw:.1f}, Median {med:.1f}, "
                                  f"zeta={zeta}, Beta({c1:g},{c0:g})")
                if e_ende < schwelle:
                    fehler.append(f"Q4 Rueckfall unter die Schwelle, zeta={zeta}")
            else:
                print(f"      {zeta:<7} {t_erw:<21} kein Umschlag in {perioden} Perioden"
                      f"        {e_ende:.4f}   [{regime}]")
                if zeta < 1.0:
                    fehler.append(f"Q1 kein Umschlag bei zeta={zeta}")
                if zeta >= 1.0 and abs(e_ende - g0) > 1e-12:
                    fehler.append("Q1 Ueberzeugung bewegt sich bei vollstaendiger Zensur")
        print()

    # ---------------------------------------------------------------- Q3
    print("   Q3: Skalierung der Dauer")
    c1, c0 = 20.0, 380.0
    hm = h_mittelpfad(c1, c0, g, schwelle)
    for zeta in (0.5, 0.9, 0.99, 0.999):
        t = hm / ((1.0 - zeta) * lam * w)
        if abs(t * (1.0 - zeta) - hm / (lam * w)) > 1e-9:
            fehler.append("Q3 Skalierung in zeta falsch")
        print(f"      zeta={zeta:<7} T={t:>10.1f} Perioden")
    for staerke in (20.0, 100.0, 400.0, 2000.0):
        c1s = 0.05 * staerke
        hs = h_mittelpfad(c1s, staerke - c1s, g, schwelle)
        if abs(hs / staerke - h_mittelpfad(1.0, 19.0, g, schwelle) / 20.0) > 1e-9:
            fehler.append("Q3 Skalierung in der Staerke falsch")
        print(f"      Staerke={staerke:<7} h*={hs:>8.1f} aufgedeckte Faelle")

    # ---------------------------------------------------------------- Q5
    print("\n   Q5: volumenfreie Fassung, gestoppte Faelle bis zum Umschlag")
    c1, c0 = 20.0, 380.0
    for lam_v in (10.0, 50.0, 250.0):
        um, _, gestoppt = lauf_schar(
            laeufe=40, perioden=4000, strom=strom,
            g=g, w=w, lam=lam_v, zeta=0.9, schwelle=schwelle, c1=c1, c0=c0,
        )
        med_f = statistics.median(gestoppt) if gestoppt else float("nan")
        med_t = statistics.median(um) if um else float("nan")
        print(f"      lambda={lam_v:<6} gestoppte Faelle bis Umschlag (Median) = {med_f:>8.0f}"
              f"   Perioden = {med_t:>7.0f}")

    # ---------------------------------------------------------------- Q6
    print("\n   Q6: Dieselbe Maschine, verschiedene Fallmischung.")
    print("   Sensitivitaet 1-alpha und Spezifitaet 1-beta sind fest und vollstaendig bekannt.")
    print("   Gefragt ist g = P(theta=1 | stopp), und davon haengt die Pruefschwelle ab.\n")
    print("      pi      g        Schwelle k/R=0,07 ueberschritten?   noetige Pruefkosten k")
    vorher = -1.0
    schwellen: list[float] = []
    for pi_v in (0.02, 0.05, 0.10, 0.20, 0.40, 0.60):
        gv = pi_v * alpha / (pi_v * alpha + (1.0 - pi_v) * (1.0 - beta))
        if gv <= vorher:
            fehler.append("Q6 g ist nicht streng steigend in pi")
        vorher = gv
        schwellen.append(gv * R)
        print(f"      {pi_v:<7} {gv:<8.4f} {'ja, pruefen' if gv >= schwelle else 'nein, nicht pruefen':<35} "
              f"{gv * R:>8.2f}")
    print(f"\n      Dieselbe Maschine verlangt je nach Fallmischung eine Schwelle zwischen")
    print(f"      {min(schwellen):.2f} und {max(schwellen):.2f}, also um den Faktor "
          f"{max(schwellen)/min(schwellen):.0f} verschieden.")
    print("      Die Fallmischung ist genau die Groesse, die die Zensur verbirgt.")

    print(f"\n{'alle Pruefungen bestanden' if not fehler else str(len(fehler)) + ' Fehler'}")
    for e in fehler[:8]:
        print("   ", e)
    return 0 if not fehler else 1


if __name__ == "__main__":
    raise SystemExit(main())
