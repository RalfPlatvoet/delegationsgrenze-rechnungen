"""AP S3: Die Transparenzberichte nach dem Digital Services Act, in die Modellsprache übersetzt.

Herkunft des Auftrags: Beschluss M5 vom 11.10.2026 (`messpunkt-vorlage.md`), ein
Arbeitstag mit Abbruchregel im Wortlaut: Liegen keine zwei vergleichbaren Quoten
fuer Beschwerden gegen Entfernungen und deren Erfolg vor, wird abgebrochen und
die Luecke in Kapitel 11 als Grenze notiert.

**Die Abbruchregel greift nicht.** Zwei Anbieter berichten beide Quoten, und
beide Berichte liegen als Primaerdokument vor:

  volltexte/dsa/TikTok-DSA-H1-2025.pdf        Annex G, Abschnitt 5, Tabellen S. 10 und 12
  volltexte/dsa/Meta-Facebook-DSA-Q4-2024.pdf Tabellen 15.1.c.(1) und 15.1.d.(1)

Alle Eingangszahlen unten sind aus diesen beiden Dateien abgelesen. Die Quoten
sind daraus gerechnet, nicht berichtet. Vorbehalte stehen in Abschnitt 3 der
Ausgabe und im Papier.

Arbeitsspur, **nicht** Teil von `src/dg/core/`.
"""

from __future__ import annotations

# --- Teil 1: die abgelesenen Primaerzahlen -----------------------------------

TIKTOK = {
    "quelle": "TikTok DSA Transparency Report, 1. Januar bis 30. Juni 2025, EU",
    # Tabelle S. 10, Spalte "Content Removed", drei Politikarten
    "entfernungen": 24_534_707 + 2_470_592 + 829_861,
    # Tabelle S. 10, Spalten "Content Restricted" und "Service Restricted"
    "weitere_massnahmen": 169_527_678 + 2_781_470 + 3_239,
    # Annex G, "Total number of appeals received", nur Hochladende
    "beschwerden": 3_075_758,
    # Annex G, "Decisions taken in respect of the complaints"
    "wiederherstellungen": 1_359_823,
    "monate": 6,
}

FACEBOOK = {
    "quelle": "Facebook DSA VLOP Transparency Report, 1. Oktober bis 31. Dezember 2024, EU",
    # Tabelle 15.1.c.(1), Zeile "Total (including other violations)"
    "entfernungen": 38_801_156,
    "weitere_massnahmen": None,   # Herabstufungen getrennt gefuehrt, nicht addierbar
    # Tabelle 15.1.d.(1), Zeile "Total (including other violations)"
    "beschwerden": 2_012_836,
    "wiederherstellungen": 650_158,
    "monate": 3,
}

# --- Teil 2: Umrechnung in die Modellgroessen --------------------------------
#
# Uebersetzung nach `notiz-m5-feldregionen.md` Abschnitt 2:
#   gestoppter Fall  = entfernter Inhalt
#   1 - zeta         = Anteil der gestoppten Faelle, der ohne Zutun der
#                      Organisation sichtbar wird, hier die eingelegte Beschwerde
#   g oben           = Erfolgsquote je Beschwerde (Selbstauswahl, nach oben verzerrt)
#   g unten          = Wiederherstellungen je Entfernung (nach unten verzerrt)

H_STERN = 342.9      # Grundfall aus `notiz-m3-begriff-und-dauer.md` Abschnitt 5.1
TAGE_JE_MONAT = 365.0 / 12.0


def quoten(feld: dict) -> dict:
    e, b, w = feld["entfernungen"], feld["beschwerden"], feld["wiederherstellungen"]
    aufdeckungen_je_tag = b / (feld["monate"] * TAGE_JE_MONAT)
    entfernungen_je_jahr = e * 12.0 / feld["monate"]
    return {
        "1-zeta auf Entfernungen": b / e,
        "1-zeta auf alle Massnahmen": (
            b / (e + feld["weitere_massnahmen"]) if feld["weitere_massnahmen"] else None
        ),
        "g oben": w / b,
        "g unten": w / e,
        "Aufdeckungen je Tag": aufdeckungen_je_tag,
        "Haltedauer in Tagen": H_STERN / aufdeckungen_je_tag,
        "1-zeta fuer ein Jahr": H_STERN / entfernungen_je_jahr,
    }


def main() -> int:
    print("AP S3: Transparenzberichte nach dem Digital Services Act")
    print()
    for feld in (TIKTOK, FACEBOOK):
        q = quoten(feld)
        print(feld["quelle"])
        print(f"  Entfernungen        {feld['entfernungen']:>12,}")
        print(f"  Beschwerden         {feld['beschwerden']:>12,}")
        print(f"  Wiederherstellungen {feld['wiederherstellungen']:>12,}")
        print(f"  1 - zeta, auf Entfernungen bezogen   {q['1-zeta auf Entfernungen']:7.4f}")
        if q["1-zeta auf alle Massnahmen"] is not None:
            print(f"  1 - zeta, auf alle Massnahmen bezogen {q['1-zeta auf alle Massnahmen']:7.4f}")
        print(f"  g, obere Schranke                    {q['g oben']:7.4f}")
        print(f"  g, untere Schranke                   {q['g unten']:7.4f}")
        print(f"  Aufdeckungen je Tag                  {q['Aufdeckungen je Tag']:12,.0f}")
        print(f"  Haltedauer des Ruhezustands in Tagen {q['Haltedauer in Tagen']:7.4f}")
        print(f"  zeta, das ein Jahr Haltedauer braeuchte  {1 - q['1-zeta fuer ein Jahr']:.8f}")
        print()

    print("Vergleich mit den Verwaltungsfeldern aus AP M5:")
    print("  dort 1 - zeta = 0,073 bis 0,080, g oben = 0,271 bis 0,309, g unten = 0,0215 bis 0,0216")
    print("  hier 1 - zeta = 0,052 bis 0,111, g oben = 0,323 bis 0,442, g unten = 0,0168 bis 0,0489")
    print("  Beide Felderarten fallen damit auf dieselbe Region.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
