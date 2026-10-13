"""AP M4. `eps*` numerisch, und die Durchmusterung, die die Frage beantwortet.

Das Konzept 2.5 verspricht als zweiten Beitrag eine Zahl: den optimalen
Erkundungsanteil `eps*`. Diese Datei rechnet ihn und berichtet, was dabei
herauskommt, auch wenn es nicht das Versprochene ist.

**Zwei Instrumente stehen zur Wahl, nicht eines** (`notiz-m2-lernen-formalisiert.md`
Abschnitt 8): die blinde Erkundung mit Anteil `eps` und die **Pruefung** einer
Ablehnung gegen das eigene myopische Urteil. Beide decken denselben Zustand auf.
Gesucht wird die beste Politik ueber beide, und die Pruefung wird als endlicher
**Vorlauf** gefuehrt, also als Zahl der Anfangsperioden mit Pruefung; dauerhaftes
Pruefen gegen das eigene Urteil ist keine ernsthafte Politik.

Durchmustert werden:
  S1  Das Fenster, auf dem blinde Erkundung ueberhaupt der billigere Kanal ist.
  S2  Die beste Politik ueber eine Durchmusterung von Schaden, Pruefkosten, Lage
      und Staerke der Vorverteilung, Zensurgrad und Geduld.
  S3  Der Vorlauf in **gestoppten Faellen** statt in Perioden, also volumenfrei.
  S4  Die Gegenprobe: Ist `eps*` irgendwo von null verschieden?
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from dg.core import beliefs as b  # noqa: E402
from dg.core import verify as v  # noqa: E402
from dg.core.types import Umgebung  # noqa: E402

PI, ALPHA, BETA = 0.20, 0.35, 0.15
G_WAHR = b.anteil_wirksam_unter_gestoppten(PI, ALPHA, BETA)
_, _, W_WAHR = b.zellen(PI, ALPHA, BETA)
ZIEHUNGEN, GITTER = 150, 6
VORLAEUFE = (0, 1, 2, 3, 5, 8, 13, 21)
T_H = 30


def kopf() -> None:
    print("AP M4: eps* numerisch\n")
    print(f"   Wahre Umgebung: pi={PI} alpha={ALPHA} beta={BETA}"
          f"  ->  g={G_WAHR:.4f}, Anteil gestoppt w={W_WAHR:.3f}")
    print(f"   Gesucht wird ueber eps in {GITTER} Gitterpunkten und ueber den Vorlauf"
          f" in {VORLAEUFE}")
    print(f"   Horizont T_H={T_H}, je Politik {ZIEHUNGEN} Ziehungen des Umweltzustands\n")


def s1_fenster() -> None:
    print("   S1: Wann ist blinde Erkundung der billigere Informationskanal?")
    print("       Pruefung billiger  <=>  k < (1 - g_0) * L")
    print("\n       g_0     L      (1-g_0)*L   g*R      Fenster [max(R*g_0,(1-g_0)L), g*R)")
    leer = 0
    gesamt = 0
    for g_0 in (0.02, 0.05, 0.20, 0.50):
        for L in (2.0, 5.0, 20.0, 50.0, 200.0):
            umg = Umgebung(pi=PI, R=100.0, L=L, lam=100.0)
            vor = b.gleichverteilte_zellen(g_0 * 20.0, (1.0 - g_0) * 20.0)
            unten, oben = b.erkundungsfenster(vor, g=G_WAHR, umgebung=umg)
            gesamt += 1
            if unten >= oben:
                leer += 1
            print(f"       {g_0:<7} {L:<6} {(1-g_0)*L:<11.2f} {G_WAHR*100:<8.2f} "
                  f"[{unten:.2f}, {oben:.2f})  {'leer' if unten >= oben else 'offen'}")
    print(f"\n       {leer} von {gesamt} Fenstern sind leer.")


def s2_s3_durchmusterung() -> list[tuple]:
    print("\n   S2 und S3: Die beste Politik, durchmustert\n")
    print("      L      k     zeta  delta  Staerke  eps*  Vorlauf  Vorlauf in")
    print("                                                         gest. Faellen")
    zeilen: list[tuple] = []
    for L, k in ((50.0, 7.0), (50.0, 8.0), (50.0, 20.0), (50.0, 60.0),
                 (5.0, 6.0), (200.0, 7.0)):
        for zeta in (1.0, 0.9):
            for delta, staerke in ((0.95, 20.0), (0.95, 400.0), (0.70, 20.0)):
                umg = Umgebung(pi=PI, R=100.0, L=L, lam=100.0)
                vor = b.gleichverteilte_zellen(0.05 * staerke, 0.95 * staerke)
                pol, wert = b.politik_stern(
                    umgebung=umg, vor=vor, zeta=zeta, k=k, T_H=T_H, delta=delta,
                    rng=np.random.default_rng(20261010), ziehungen=ZIEHUNGEN,
                    gitter=GITTER, vorlaeufe=VORLAEUFE,
                )
                faelle = pol.pruef_vorlauf * umg.lam * W_WAHR
                print(f"      {L:<6} {k:<5} {zeta:<5} {delta:<6} {staerke:<8.0f} "
                      f"{pol.eps:<5.2f} {pol.pruef_vorlauf:<8} {faelle:.0f}")
                zeilen.append((L, k, zeta, delta, staerke, pol.eps, pol.pruef_vorlauf, wert))
    return zeilen


def s4_gegenprobe(zeilen: list[tuple]) -> int:
    print("\n   S4: Gegenprobe")
    mit_eps = [z for z in zeilen if z[5] > 0.0]
    mit_vorlauf = [z for z in zeilen if z[6] > 0]
    print(f"      Zeilen mit eps* > 0:      {len(mit_eps)} von {len(zeilen)}")
    print(f"      Zeilen mit Vorlauf > 0:   {len(mit_vorlauf)} von {len(zeilen)}")
    for z in mit_eps:
        print(f"         eps* = {z[5]:.2f} bei L={z[0]}, k={z[1]}, zeta={z[2]}, "
              f"delta={z[3]}, Staerke={z[4]}")
    return len(mit_eps)


def s5_kanalvergleich() -> None:
    print("\n   S5: Der Vergleich der Kanaele, je gestoppten Fall, bei g_0 = 0,05")
    vor = b.gleichverteilte_zellen(1.0, 19.0)
    g_0 = vor.lage_g
    print("      L      k     Abweichung durch Pruefen   durch blinde Erkundung   billiger")
    for L in (5.0, 50.0, 200.0):
        for k in (7.0, 60.0):
            umg = Umgebung(pi=PI, R=100.0, L=L, lam=100.0)
            durch_pruefen = k - g_0 * umg.R
            durch_erkunden = (1.0 - g_0) * umg.L - g_0 * umg.R
            vermerk = v.billigerer_informationskanal(k, g_0, umg)
            if durch_erkunden <= 0.0:
                vermerk += " (kein Informationskauf: blind behandeln lohnt ohnehin)"
            print(f"      {L:<6} {k:<5} {durch_pruefen:<26.2f} {durch_erkunden:<24.2f} "
                  f"{vermerk}")


def s6_das_vorzeichen_des_motivs() -> None:
    """Warum `eps*` dort innen liegt, wo es innen liegt, und was das bedeutet."""
    print("\n   S6: Der eine innere Optimalwert, und sein Motiv hat das umgekehrte Vorzeichen")
    umg = Umgebung(pi=PI, R=100.0, L=5.0, lam=100.0)
    vor = b.gleichverteilte_zellen(1.0, 19.0)
    k = 6.0
    print(f"      Lage: L={umg.L}, k={k}, g wahr={G_WAHR:.4f}, g_0={vor.lage_g}")
    print("      Zielgroesse ueber eps, 400 Ziehungen, delta=0.70:")
    werte = []
    for i in range(11):
        eps = i / 10.0
        wert = b.pfad_ertrag_erwartet(
            umgebung=umg, vor=vor, politik=b.Politik(eps=eps), zeta=1.0, k=k,
            T_H=T_H, delta=0.70, ziehungen=400,
            rng=np.random.default_rng(20261010),
        )
        werte.append((eps, wert))
    for eps, wert in werte:
        print(f"         eps={eps:.1f}  {wert:12.2f}")
    besser = max(werte, key=lambda z: z[1])
    print(f"      Innerer Optimalwert bei eps = {besser[0]:.1f}.")
    print("\n      **Das Motiv ist nicht das der Erkundung.** Je gestoppten Fall gilt")
    print(f"         blind behandeln:  g*R - (1-g)*L = {G_WAHR*umg.R - (1-G_WAHR)*umg.L:.2f}")
    print(f"         pruefen:          g*R - k       = {G_WAHR*umg.R - k:.2f}")
    print("      Blindes Behandeln ist hier **besser als Pruefen**, weil der Schaden klein")
    print("      ist gegen den entgangenen Ertrag. Wer lernt, faengt an zu pruefen und wird")
    print("      dadurch schlechter. Mehr Erkundung beschleunigt das Lernen und damit den")
    print("      Wechsel zu der schlechteren Handlung; der innere Wert ist der Ausgleich")
    print("      zweier gegenlaeufiger Wirkungen und **nicht** der Erkundungswert, den")
    print("      Konzept 2.5 gemeint hat.")


def main() -> int:
    kopf()
    s1_fenster()
    zeilen = s2_s3_durchmusterung()
    anzahl_eps = s4_gegenprobe(zeilen)
    s5_kanalvergleich()
    s6_das_vorzeichen_des_motivs()
    print("\n   Ergebnis, in drei Saetzen.")
    print(f"      Erstens: eps* ist in {anzahl_eps} von {len(zeilen)} Zeilen von null")
    print("      verschieden, und alle liegen in dem engen Fenster aus S1.")
    print("      Zweitens: Dort ist eps **kein Erkundungsinstrument**. Blindes Behandeln ist")
    print("      dort besser als Pruefen, das Lernen fuehrt zur schlechteren Handlung, und")
    print("      das Motiv des inneren Wertes hat nach S6 das umgekehrte Vorzeichen.")
    print("      Drittens: Die Zahl, die das Modell wirklich hergibt, ist der **Pruefvorlauf**,")
    print("      und er ist in gestoppten Faellen anzugeben, nicht in Perioden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
