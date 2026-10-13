"""AP M5. Die Feldbefunde als Parameterregionen, und die Pruefung der Vorhersage aus M3.

Zwei Aufgaben nach `zuschnitt-reduziert.md` Stufe 2, Zeile M5:

  1. Feldzahlen fuer die Lage `g_0` und die Staerke `c_1 + c_0` der Vorverteilung
     ueber `g`. Die Literatursichtung traegt dafuer keine Zahl
     (`notiz-m5-feldregionen.md` Abschnitt 1). Belegquelle ist daher die amtliche
     Statistik: Erfolgsquoten von Widerspruch und Klage gegen ablehnende Bescheide.
  2. Die Pruefung der Vorhersage aus `notiz-m3-begriff-und-dauer.md` Abschnitt 5.3:
     Der Ruhezustand ist ein Phaenomen der kleinen Zahl.

**Die Uebersetzung in die Modellsprache** (`symbolverzeichnis.md`):

  gestoppter Fall      ablehnender oder nachteilig festsetzender Bescheid
  `lambda * w`         Zahl dieser Bescheide je Periode
  `1 - zeta`           Anteil der gestoppten Faelle, der **ohne Zutun der
                       Organisation** sichtbar wird. Das ist der eingelegte
                       Widerspruch: Er geht vom Betroffenen aus, nicht von der
                       pruefenden Stelle. Mit `eps = 0` gilt `nu = 1 - zeta`.
  `g = P(theta=1|stopp)` Anteil der wirksamen, also zu Unrecht gestoppten Faelle

**Zwei Schranken statt eines Punktwerts.** Der Anteil der Korrekturen unter den
Widerspruechen ist nach oben verzerrt, weil wer widerspricht eher im Recht ist
(Selbstauswahl). Der Anteil der Korrekturen unter **allen** Bescheiden ist nach
unten verzerrt, weil wer nicht widerspricht nicht geprueft wird. Also:

  g_unten = Korrekturen / alle Bescheide        (untere Schranke)
  g_oben  = Korrekturen / Widersprueche         (obere Schranke)

Jede Zahl hat eine Zeile in `quellen.md` Teil 3. Keine Zahl ohne Beleg.
"""

from __future__ import annotations

from dataclasses import dataclass

# Der Grundfall aus `notiz-m3-begriff-und-dauer.md` Abschnitt 5.1:
# Beta(20, 380), g_0 = 0,05, k/R = 0,07, g = 0,0933 ergibt h* = 342,9 aufgedeckte
# gestoppte Faelle bis zum Umschlag der Ueberzeugung.
H_STERN_GRUNDFALL = 342.9

# Die Staerke des Grundfalls, fuer die Skalierungsprobe.
STAERKE_GRUNDFALL = 400.0


@dataclass(frozen=True)
class Feld:
    """Ein Verwaltungsfeld mit amtlich ausgewiesenen Zahlen.

    `bescheide`      Zahl der Bescheide je Jahr, die ein `stopp` sein koennen
    `widersprueche`  eingelegte Widersprueche je Jahr, also die Aufdeckungen
    `korrekturen`    Widersprueche mit Abhilfe oder Aenderung
    `fehler_eng`     Teilmenge, die der Traeger selbst als eigenen Fehler deutet
    """

    name: str
    jahr: int
    bescheide: float | None
    widersprueche: float | None
    korrekturen: float | None
    fehler_eng: float | None
    quelle: str

    @property
    def rueckfluss(self) -> float | None:
        """Schaetzer fuer `1 - zeta`."""
        if self.bescheide is None or self.widersprueche is None:
            return None
        return self.widersprueche / self.bescheide

    @property
    def zeta(self) -> float | None:
        r = self.rueckfluss
        return None if r is None else 1.0 - r

    @property
    def g_unten(self) -> float | None:
        if self.bescheide is None or self.korrekturen is None:
            return None
        return self.korrekturen / self.bescheide

    @property
    def g_oben(self) -> float | None:
        if self.widersprueche is None or self.korrekturen is None:
            return None
        return self.korrekturen / self.widersprueche

    def haltedauer_jahre(self, h_stern: float = H_STERN_GRUNDFALL) -> float | None:
        """Wie lange der Ruhezustand haelt, in Jahren.

        `N = h* / (1 - zeta)` gestoppte Faelle, geteilt durch den Jahresstrom
        `lambda * w`. Das kuerzt sich zu `h*` geteilt durch die Aufdeckungen je
        Jahr, und die sind die eingelegten Widersprueche.
        """
        if self.widersprueche is None:
            return None
        return h_stern / self.widersprueche

    def zeta_kritisch(self, jahre: float = 1.0,
                      h_stern: float = H_STERN_GRUNDFALL) -> float | None:
        """Welcher Zensurgrad noetig waere, damit der Zustand `jahre` haelt."""
        if self.bescheide is None:
            return None
        return 1.0 - h_stern / (jahre * self.bescheide)


FELDER = (
    Feld(
        name="Pflegebegutachtung (MD)",
        jahr=2022,
        bescheide=2_541_014,          # 185.494 / 0,073, siehe Notiz Abschnitt 3
        widersprueche=185_494,
        korrekturen=54_839,
        fehler_eng=None,
        quelle="MD-Bund, Meldung vom 22.11.2023",
    ),
    Feld(
        name="Rentenbescheide (DRV)",
        jahr=2024,
        bescheide=2_000_000,
        widersprueche=159_000,
        korrekturen=43_089,           # 27,1 Prozent von 159.000
        fehler_eng=1_272,             # 0,8 Prozent von 159.000
        quelle="DRV Bund, Meldung vom 30.04.2025",
    ),
    Feld(
        name="Buergergeld (SGB II)",
        jahr=2025,
        bescheide=None,               # amtlich nicht ausgewiesen
        widersprueche=476_728,        # erledigte Widersprueche
        korrekturen=147_213,
        fehler_eng=42_303,
        quelle="BA, Meldung vom 13.01.2026",
    ),
    Feld(
        name="Berufskrankheiten (DGUV)",
        jahr=2025,
        bescheide=56_047,             # Ablehnungen
        widersprueche=None,           # Widerspruchszahl nicht veroeffentlicht
        korrekturen=None,
        fehler_eng=None,
        quelle="DGUV, BK-Geschehen 2025",
    ),
)


def _p(x: float | None, stellen: int = 1) -> str:
    return "nicht belegt" if x is None else f"{100 * x:.{stellen}f} %".replace(".", ",")


def _z(x: float | None) -> str:
    return "nicht belegt" if x is None else f"{x:,.0f}".replace(",", ".")


def tafel_regionen() -> None:
    print("S1  Die Felder als Parameterregionen")
    print()
    kopf = f"{'Feld':26} {'Jahr':5} {'Bescheide':>11} {'1-zeta':>10} {'g unten':>10} {'g oben':>10}"
    print(kopf)
    print("-" * len(kopf))
    for f in FELDER:
        print(f"{f.name:26} {f.jahr:5} {_z(f.bescheide):>11} "
              f"{_p(f.rueckfluss):>10} {_p(f.g_unten, 2):>10} {_p(f.g_oben):>10}")
    print()
    print("  Der Rueckfluss liegt, wo er belegt ist, zwischen 7 und 8 Prozent.")
    print("  Er haengt am Rechtsweg und nicht am Volumen.")
    print()


def tafel_dauer() -> None:
    print("S2  Die Vorhersage aus M3 Abschnitt 5.3 an den Feldern")
    print()
    kopf = (f"{'Feld':26} {'Aufdeckungen/Jahr':>18} {'haelt (Grundfall)':>18} "
            f"{'zeta fuer 1 Jahr':>17}")
    print(kopf)
    print("-" * len(kopf))
    for f in FELDER:
        d = f.haltedauer_jahre()
        dauer = "nicht belegt" if d is None else (
            f"{d * 365:.1f} Tage".replace(".", ",") if d < 1 else f"{d:.1f} Jahre".replace(".", ","))
        zk = f.zeta_kritisch()
        zks = "nicht belegt" if zk is None else f"{zk:.5f}".replace(".", ",")
        print(f"{f.name:26} {_z(f.widersprueche):>18} {dauer:>18} {zks:>17}")
    print()
    print("  Gerechnet mit h* = 342,9 aus dem Grundfall, also mit Beta(20, 380) und")
    print("  knappem Irrtum. In den Feldern ist g groesser und h* damit kleiner.")
    print()


def tafel_skalierung() -> None:
    print("S3  Wie fest die Meinung sitzen muesste, damit der Zustand ein Jahr haelt")
    print()
    kopf = f"{'Feld':26} {'noetige Staerke':>16} {'Vielfaches des Grundfalls':>26}"
    print(kopf)
    print("-" * len(kopf))
    for f in FELDER:
        if f.widersprueche is None:
            print(f"{f.name:26} {'nicht belegt':>16} {'nicht belegt':>26}")
            continue
        # h* ist linear in der Staerke. Fuer eine Haltedauer von einem Jahr muss
        # h* so gross sein wie die Aufdeckungen eines Jahres.
        noetig = STAERKE_GRUNDFALL * f.widersprueche / H_STERN_GRUNDFALL
        print(f"{f.name:26} {_z(noetig):>16} "
              f"{str(round(noetig / STAERKE_GRUNDFALL)).replace('.', ','):>26}")
    print()
    print("  Die Staerke ist die Zahl der Beobachtungen, die die Vorverteilung wiegt.")
    print("  Werte dieser Groesse sind keine Meinung mehr, sondern ein Archiv.")
    print()


def tafel_lage() -> None:
    """Die Lage `g_0` ist belegbar, und zwar aus der Eigendeutung des Traegers.

    Das ist der eigentliche Fund dieses Arbeitspakets. `g_0` ist die **Meinung**
    der Organisation ueber `g` und keine Eigenschaft der Welt, also aus einer
    Fehlerquote nicht ablesbar. Zwei Traeger trennen die aufgedeckten Faelle
    aber selbst in zwei Toepfe: eigener Fehler, und Abhilfe wegen Umstaenden,
    die man sich nicht zurechnet. **Diese Trennung ist die Meinung.** Der eng
    gefasste Topf ist der Schaetzer fuer `g_0`, der weite fuer `g`.
    """
    print("S2a Die Lage g_0 aus der Eigendeutung, gegen das aufgedeckte g")
    print()
    kopf = (f"{'Feld':26} {'g_0 (Eigendeutung)':>19} {'g (aufgedeckt)':>15} "
            f"{'Faktor':>8} {'Fenster fuer k/R':>22}")
    print(kopf)
    print("-" * len(kopf))
    for f in FELDER:
        if f.fehler_eng is None or f.korrekturen is None or f.widersprueche is None:
            print(f"{f.name:26} {'nicht belegt':>19} {'nicht belegt':>15} "
                  f"{'':>8} {'':>22}")
            continue
        g0 = f.fehler_eng / f.widersprueche
        g = f.korrekturen / f.widersprueche
        fenster = f"({_p(g0, 1)} ; {_p(g, 1)})".replace(" %", "%")
        faktor = f"{g / g0:.1f}".replace(".", ",")
        print(f"{f.name:26} {_p(g0, 1):>19} {_p(g, 1):>15} "
              f"{faktor:>8} {fenster:>22}")
    print()
    print("  Ein Ruhezustand besteht genau dann, wenn k/R in diesem Fenster liegt.")
    print("  Die Fenster sind weit und nicht knapp. Der Irrtum ist also nicht die")
    print("  Ausnahme eines schmalen Parameterbereichs, sondern der Regelfall fuer")
    print("  jedes mittlere Pruefkostenverhaeltnis.")
    print()
    print("  Gegenprobe mit grosser Irrtumstiefe, k/R knapp unter g:")
    for f in FELDER:
        if f.fehler_eng is None or f.korrekturen is None or f.widersprueche is None:
            continue
        g0 = f.fehler_eng / f.widersprueche
        g = f.korrekturen / f.widersprueche
        kr = g0 + 0.92 * (g - g0)
        tiefe = (kr - g0) / (g - kr)
        h = STAERKE_GRUNDFALL * tiefe
        tage = 365 * h / f.widersprueche
        print(f"    {f.name:26} Tiefe {tiefe:5.1f}, h* {h:8.0f}, "
              f"haelt {tage:5.1f} Tage".replace(".", ","))
    print()


def befund() -> None:
    print("S4  Der Befund")
    print()
    print("  In keinem der vier Felder ist der Ruhezustand nach dem Dauergesetz zu")
    print("  erwarten. Nicht weil das Volumen hoch ist, sondern weil der Rechtsweg")
    print("  einen Rueckfluss von 7 bis 8 Prozent erzwingt. Die Vorhersage aus 5.3")
    print("  bestaetigt sich in der Richtung und benennt die falsche Groesse: nicht")
    print("  die Fallzahl entscheidet, sondern das Produkt lambda * w * (1 - zeta).")
    print()
    print("  Der Ruhezustand ist danach kein Phaenomen der Verwaltung, sondern der")
    print("  Felder ohne institutionellen Rueckfluss: Bewerbungs- und")
    print("  Kreditablehnung, Inhaltsmoderation, Lieferantenauswahl. Genau dort")
    print("  gibt es keine amtliche Zahl. Das ist die Belegasymmetrie des Papiers.")
    print()


if __name__ == "__main__":
    tafel_regionen()
    tafel_lage()
    tafel_dauer()
    tafel_skalierung()
    befund()
