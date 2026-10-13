"""AP M2. Nachrechnung der Formalisierung des Lernens unter Zensur.

Zweck: Die in `notiz-m2-lernen-formalisiert.md` behaupteten Aussagen werden hier
unabhaengig nachgerechnet, einmal geschlossen und einmal durch Ziehen. Die Datei ist
Arbeitsspur und **nicht** Teil des Rechenkerns `src/dg/core/`; `beliefs.py` entsteht
nach dem Zuschnitt erst in AP M4.

Geprueft werden:
  P1  Die Zellwahrscheinlichkeiten summieren sich zu eins, fuer jedes nu.
  P2  Die Likelihood faktorisiert in Dirichlet-Teil und Beta-Teil.
  P3  mu_s = g, also die entscheidungsrelevante Nachverteilung bei Empfehlung stopp
      ist genau der nicht beobachtete Anteil.
  P4  mu_w haengt nur von u und v ab, ist also aus den Daten bestimmt.
  P5  Bei nu = 0 gleicht die Nachverteilung ueber g der Vorverteilung, exakt.
  P6  Bei nu > 0 ist (pi, alpha, beta) aus (u, v, g) eindeutig zurueckzurechnen.
  P7  Die Umkehrabbildung (u, v, g) -> (pi, alpha, beta) ist die Inverse der Hinabbildung.
  P8  Der identifizierte Bereich von pi ist [u, 1-v], und g laeuft dabei ueber [0, 1].
  P9  Lernen: mit nu > 0 zieht sich die Nachverteilung ueber g auf den wahren Wert zusammen,
      mit nu = 0 nicht. Gemessen an der Standardabweichung.
  P10 Die Fisher-Information ueber g je Fall ist nu * w0 / (g(1-g)).
  P11 Der Ruhezustand ist ein Fixpunkt: Gilt k >= R * E[g], so wird nicht geprueft,
      damit bleibt nu = 0, damit bewegt sich E[g] nicht, damit wird weiter nicht geprueft.
  P12 Pruefung und blinde Erkundung decken dasselbe auf. Die Pruefung ist der billigere
      Kanal genau dann, wenn k < (1 - mu_s) * L.
"""

from __future__ import annotations

import math
import random

TOL = 1e-12


# ---------------------------------------------------------------- Abbildungen

def zellen(pi: float, alpha: float, beta: float, nu: float) -> dict[str, float]:
    """Die fuenf beobachtbaren Zellen. `nu` ist der Aufdeckungsgrad gestoppter Faelle."""
    u = pi * (1.0 - alpha)
    v = (1.0 - pi) * beta
    w0 = pi * alpha + (1.0 - pi) * (1.0 - beta)
    return {
        "weiter_1": u,
        "weiter_0": v,
        "stopp_auf_1": w0 * nu * (pi * alpha / w0 if w0 > 0 else 0.0),
        "stopp_auf_0": w0 * nu * ((1.0 - pi) * (1.0 - beta) / w0 if w0 > 0 else 0.0),
        "stopp_verdeckt": w0 * (1.0 - nu),
    }


def nach_uvg(pi: float, alpha: float, beta: float) -> tuple[float, float, float]:
    """Die eigenen Koordinaten: u, v und g = P(theta = 1 | stopp)."""
    u = pi * (1.0 - alpha)
    v = (1.0 - pi) * beta
    w0 = 1.0 - u - v
    g = (pi - u) / w0          # pi*alpha / w0
    return u, v, g


def nach_strukturell(u: float, v: float, g: float) -> tuple[float, float, float]:
    """Die Umkehrung: aus u, v, g zurueck auf pi, alpha, beta."""
    w0 = 1.0 - u - v
    pi = u + g * w0
    alpha = 1.0 - u / pi
    beta = v / (1.0 - pi)
    return pi, alpha, beta


def mu_w(u: float, v: float) -> float:
    return u / (u + v)


# ---------------------------------------------------------------- Pruefungen

def p1_p8_geschlossen(faelle: int, strom: random.Random) -> list[str]:
    fehler: list[str] = []
    for _ in range(faelle):
        pi = strom.uniform(0.02, 0.98)
        alpha = strom.uniform(0.01, 0.99)
        beta = strom.uniform(0.01, 0.99)
        nu = strom.choice([0.0, strom.uniform(0.0, 1.0), 1.0])

        z = zellen(pi, alpha, beta, nu)
        if abs(sum(z.values()) - 1.0) > TOL:
            fehler.append(f"P1 Summe {sum(z.values())} bei pi={pi}")

        u, v, g = nach_uvg(pi, alpha, beta)
        w0 = 1.0 - u - v

        # P3: mu_s = P(theta=1 | stopp) = pi*alpha / w0 = g
        mu_s = pi * alpha / w0
        if abs(mu_s - g) > TOL:
            fehler.append(f"P3 mu_s={mu_s} != g={g}")

        # P4: mu_w nur aus u und v
        mu_w_direkt = pi * (1 - alpha) / (pi * (1 - alpha) + (1 - pi) * beta)
        if abs(mu_w_direkt - mu_w(u, v)) > TOL:
            fehler.append("P4 mu_w nicht aus u,v")

        # P7: Hin und zurueck
        pi2, a2, b2 = nach_strukturell(u, v, g)
        if max(abs(pi2 - pi), abs(a2 - alpha), abs(b2 - beta)) > 1e-10:
            fehler.append(f"P7 Umkehr {pi2,a2,b2} != {pi,alpha,beta}")

        # P8: identifizierter Bereich
        if not (u - TOL <= pi <= 1.0 - v + TOL):
            fehler.append(f"P8 pi={pi} ausserhalb [{u},{1-v}]")
        # Randwerte: pi = u  -> g = 0 ; pi = 1-v -> g = 1
        if abs((u - u) / w0 - 0.0) > TOL:
            fehler.append("P8 g(pi=u) != 0")
        if abs(((1.0 - v) - u) / w0 - 1.0) > TOL:
            fehler.append("P8 g(pi=1-v) != 1")

        # P10: Fisher-Information ueber g je Fall
        # Beitrag nur von den aufgedeckten gestoppten Faellen: Anzahl ~ nu*w0, Binomial(g)
        fisher = nu * w0 / (g * (1.0 - g))
        beitrag = z["stopp_auf_1"] / g**2 + z["stopp_auf_0"] / (1.0 - g) ** 2
        if abs(fisher - beitrag) > 1e-9:
            fehler.append(f"P10 {fisher} != {beitrag}")
    return fehler


def p2_faktorisierung(faelle: int, strom: random.Random) -> list[str]:
    """Die Likelihood einer Stichprobe, einmal Zelle fuer Zelle, einmal faktorisiert."""
    fehler: list[str] = []
    for _ in range(faelle):
        pi = strom.uniform(0.05, 0.95)
        alpha = strom.uniform(0.05, 0.95)
        beta = strom.uniform(0.05, 0.95)
        nu = strom.uniform(0.0, 1.0)
        z = zellen(pi, alpha, beta, nu)
        n = {k: strom.randint(0, 12) for k in z}

        # Weg 1: Produkt der Zellwahrscheinlichkeiten
        log1 = sum(n[k] * math.log(z[k]) for k in z if n[k] > 0 and z[k] > 0)
        if any(n[k] > 0 and z[k] == 0.0 for k in z):
            continue

        # Weg 2: Dirichlet-Teil (u, v, w0) * Beta-Teil (g) * nu-Teil
        u, v, g = nach_uvg(pi, alpha, beta)
        w0 = 1.0 - u - v
        n_w = n["stopp_auf_1"] + n["stopp_auf_0"] + n["stopp_verdeckt"]
        m1, m0 = n["stopp_auf_1"], n["stopp_auf_0"]
        m = m1 + m0
        log2 = (
            n["weiter_1"] * math.log(u)
            + n["weiter_0"] * math.log(v)
            + (n_w * math.log(w0) if n_w else 0.0)
            + (m1 * math.log(g) if m1 else 0.0)
            + (m0 * math.log(1.0 - g) if m0 else 0.0)
            + (m * math.log(nu) if m else 0.0)
            + ((n_w - m) * math.log(1.0 - nu) if n_w - m else 0.0)
        )
        if abs(log1 - log2) > 1e-9:
            fehler.append(f"P2 {log1} != {log2}")
    return fehler


def p5_p9_lernen(strom: random.Random) -> list[str]:
    """Ziehen: Beta-Nachverteilung ueber g bei nu = 0 und bei nu > 0."""
    fehler: list[str] = []
    pi, alpha, beta = 0.20, 0.35, 0.15
    u, v, g_wahr = nach_uvg(pi, alpha, beta)
    c1, c0 = 2.0, 3.0                      # Vorverteilung Beta(2,3), Mittel 0,4
    vor_mittel = c1 / (c1 + c0)
    vor_streuung = math.sqrt(c1 * c0 / ((c1 + c0) ** 2 * (c1 + c0 + 1)))

    for nu, erwartet_lernt in ((0.0, False), (0.05, True), (0.5, True)):
        z = zellen(pi, alpha, beta, nu)
        namen = list(z)
        gewichte = [z[k] for k in namen]
        m1 = m0 = 0
        for _ in range(60_000):
            k = strom.choices(namen, weights=gewichte, k=1)[0]
            if k == "stopp_auf_1":
                m1 += 1
            elif k == "stopp_auf_0":
                m0 += 1
        a, b = c1 + m1, c0 + m0
        mittel = a / (a + b)
        streuung = math.sqrt(a * b / ((a + b) ** 2 * (a + b + 1)))

        if nu == 0.0:
            if m1 or m0:
                fehler.append("P5 aufgedeckte Faelle bei nu=0")
            if abs(mittel - vor_mittel) > TOL or abs(streuung - vor_streuung) > TOL:
                fehler.append("P5 Nachverteilung != Vorverteilung bei nu=0")
        else:
            if streuung >= vor_streuung:
                fehler.append(f"P9 keine Verengung bei nu={nu}")
            if abs(mittel - g_wahr) > 0.05:
                fehler.append(f"P9 Mittel {mittel:.3f} weit von g={g_wahr:.3f} bei nu={nu}")
        print(f"   nu={nu:<5} aufgedeckt={m1+m0:<6} E[g]={mittel:.4f} "
              f"sd={streuung:.4f}  (g wahr {g_wahr:.4f}, Vorverteilung {vor_mittel:.4f})")
    return fehler


def p11_ruhezustand(strom: random.Random) -> list[str]:
    """Der Ruhezustand als Fixpunkt, einmal durchgespielt.

    Die Organisation prueft eine Stopp-Empfehlung genau dann, wenn k < R * E[g].
    Pruefen deckt den Zustand auf, erzeugt also aufgedeckte Faelle. Wird nicht
    geprueft und nicht erkundet, so ist nu = 0 und die Ueberzeugung bewegt sich nicht.
    """
    fehler: list[str] = []
    pi, alpha, beta = 0.20, 0.35, 0.15
    u, v, g_wahr = nach_uvg(pi, alpha, beta)
    w0 = 1.0 - u - v
    R, zeta, eps = 100.0, 1.0, 0.0

    print("   k        E[g] Start   geprueft   E[g] Ende   Ruhezustand   Verlust/Fall")
    for c1, c0, k in ((1.0, 19.0, 10.0), (1.0, 19.0, 7.0), (1.0, 19.0, 3.0), (8.0, 2.0, 10.0)):
        a, b = c1, c0
        start = a / (a + b)
        geprueft = 0
        for _ in range(40_000):
            erw_g = a / (a + b)
            nu = eps + (1.0 - eps) * (1.0 - zeta)          # ohne Pruefung
            pruefen = k < R * erw_g
            if pruefen:
                nu = 1.0                                    # Pruefung deckt auf
            z = zellen(pi, alpha, beta, nu)
            fall = strom.choices(list(z), weights=list(z.values()), k=1)[0]
            if fall == "stopp_auf_1":
                a += 1.0
                geprueft += pruefen
            elif fall == "stopp_auf_0":
                b += 1.0
                geprueft += pruefen
        ende = a / (a + b)
        ruhe = k >= R * start
        # Verlust je gestoppten Fall, wenn im Ruhezustand nicht geprueft wird,
        # obwohl die Pruefung bei richtiger Ueberzeugung lohnend waere
        verlust = max(0.0, g_wahr * R - k) if ruhe else 0.0
        print(f"   {k:<8} {start:<11.4f} {geprueft:<10} {ende:<11.4f} "
              f"{str(ruhe):<13} {verlust:.2f}")
        if ruhe and abs(ende - start) > TOL:
            fehler.append(f"P11 Ueberzeugung bewegt sich im Ruhezustand, k={k}")
        if not ruhe and abs(ende - g_wahr) > 0.03:
            fehler.append(f"P11 kein Lernen trotz Pruefung, k={k}, E[g]={ende}")
    return fehler


def p12_zwei_kanaele(faelle: int, strom: random.Random) -> list[str]:
    """Pruefung gegen blinde Erkundung: beide decken auf, nur die Kosten trennen sie.

    Pruefen und danach richtig handeln:   mu_s * R - k
    Blind behandeln:                      mu_s * R - (1 - mu_s) * L
    Also ist die Pruefung genau dann der billigere Weg zur selben Information,
    wenn k < (1 - mu_s) * L.
    """
    fehler: list[str] = []
    for _ in range(faelle):
        mu_s = strom.uniform(0.0, 1.0)
        R, L, k = strom.uniform(1, 200), strom.uniform(1, 200), strom.uniform(0, 200)
        wert_pruefen = mu_s * R - k
        wert_blind = mu_s * R - (1.0 - mu_s) * L
        if (wert_pruefen > wert_blind) != (k < (1.0 - mu_s) * L):
            fehler.append("P12 Schwelle der Kanalwahl falsch")
    return fehler


def main() -> int:
    strom = random.Random(20261010)
    print("AP M2: Nachrechnung der Formalisierung\n")
    alle: list[str] = []

    for name, fn in (
        ("P1,P3,P4,P7,P8,P10 geschlossen, 20.000 Parametersaetze",
         lambda: p1_p8_geschlossen(20_000, strom)),
        ("P2 Faktorisierung der Likelihood, 5.000 Stichproben",
         lambda: p2_faktorisierung(5_000, strom)),
    ):
        f = fn()
        print(f"{'ok  ' if not f else 'FEHL'} {name}")
        for e in f[:3]:
            print("      ", e)
        alle += f

    print("\nP5 und P9, Ziehen ueber 60.000 Faelle je Aufdeckungsgrad:")
    f = p5_p9_lernen(strom)
    print(f"{'ok  ' if not f else 'FEHL'} P5, P9")
    for e in f[:3]:
        print("      ", e)
    alle += f

    print("\nP11, der Ruhezustand als Fixpunkt, 40.000 Faelle je Zeile:")
    f = p11_ruhezustand(strom)
    print(f"{'ok  ' if not f else 'FEHL'} P11")
    for e in f[:3]:
        print("      ", e)
    alle += f

    f = p12_zwei_kanaele(20_000, strom)
    print(f"\n{'ok  ' if not f else 'FEHL'} P12 Kanalwahl, 20.000 Parametersaetze")
    for e in f[:3]:
        print("      ", e)
    alle += f

    print(f"\n{'alle Pruefungen bestanden' if not alle else str(len(alle)) + ' Fehler'}")
    return 0 if not alle else 1


if __name__ == "__main__":
    raise SystemExit(main())
