# Delegationsgrenze: die Rechnungen zum Papier

Arbeitsspur zum Working Paper „Die Delegationsgrenze. Maschinelle Bewertung, reale Autorität und
die Architektur betrieblicher Entscheidungsketten" (PPI Working Paper 09/2026, Ralf Platvoet).

## Was das ist

Die Skripte, die die gerechneten Zahlen des Papiers erzeugt haben, in dem Stand, in dem sie sie
erzeugt haben. Jede gerechnete Zahl des Papiers nennt eines dieser Skripte. Dieses Archiv macht
sie nachlesbar und nachrechenbar.

Der Rechenkern, auf dem sie aufbauen, liegt getrennt im Repositorium
[delegationsgrenze-rechenkern](https://github.com/RalfPlatvoet/delegationsgrenze-rechenkern)
(DOI 10.5281/zenodo.23336889). **`src/dg/` ist hier die unveränderte Kopie der Fassung 0.1.0 dieses
Kerns**, damit die Skripte ohne Installation laufen. Wer den Kern nutzen will, nimmt das andere
Repositorium.

Das ist eine Arbeitsspur und keine Software. Die Skripte sind für das Papier geschrieben, nicht
für eine Wiederverwendung. Jedes Ergebnis steht unter den Annahmen des Kapitels 5.

## Die Skripte

| Skript | Rechnet | Papier | Dauer |
|---|---|---|---|
| `k6_entwurf.py` | Entwurfsproblem für zwei und drei Stellen, geschlossene Schranke für den Vorfilter | Kapitel 6 | 1 s |
| `m2_identifikation.py` | Lernen unter Zensur, zwölf Prüfpunkte, geschlossen und durch Ziehen | Kapitel 5, 7, 8 | 1 s |
| `m3_dauer.py` | Dauer des Ruhezustands bei gelockerter Zensur, sechs Prüfpunkte | Kapitel 8 | 1 min |
| `m4_eps_stern.py` | Optimaler Erkundungsanteil `eps*` numerisch, mit Durchmusterung | Kapitel 8, 9 | 2 min |
| `m5_feldregionen.py` | Feldbefunde als Parameterregionen, Prüfung der Vorhersage aus M3 | Kapitel 8, Anhang C | 1 s |
| `s3_dsa.py` | Transparenzberichte nach dem Digital Services Act in Modellgrößen | Kapitel 11, Anhang C | 1 s |
| `s8_abbildung.py` | Gitterlauf und Abbildung des Prüfvorlaufs | Kapitel 8.4, Abbildung 1 | 2 min |

Die Zuordnung zu den Kapiteln folgt den Verweisen des Papiers auf die zugehörigen Notizen. Die
Zeiten stammen von einem Rechner mit Intel-Prozessor.

## Benutzung

```
python3 -m pip install numpy
python3 k6_entwurf.py
```

Jedes Skript läuft aus dem Hauptordner und schreibt auf die Standardausgabe. Die Ausgaben der
geltenden Läufe liegen unter `ausgaben/`, jeweils als `<skript>.txt`. `m2` bis `m4` ziehen aus
einem festgelegten Zufallsstrom und liefern bei gleicher Python- und NumPy-Fassung dieselbe
Ausgabe.

`s8_abbildung.py` legt einen Lauf unter `runs/<kennung>/` ab und schreibt `figures/`. Die
Kennung enthält den Stand des Quelltextes aus Git. **In diesem Repositorium lautet sie darum
anders als im Papier**, die Zahlen in `ergebnis.csv` sind byteweise dieselben. Der Lauf aus dem
Papier liegt unter `runs/aff73a7643fa-8d44d5b-20261011/`, die Abbildung unter `figures/`.

## Was fehlt

Die beiden Transparenzberichte, aus denen `s3_dsa.py` seine Eingangszahlen abliest, liegen nicht
bei. Sie sind Dokumente der Anbieter. Das Skript trägt die abgelesenen Zahlen mit Seiten- und
Tabellenangabe im Kopf, die Berichte sind bei den Anbietern abrufbar:

- TikTok, DSA Transparency Report, 1. Januar bis 30. Juni 2025 (EU), Annex G, Abschnitt 5
- Meta, Facebook, DSA Transparency Report, 4. Quartal 2024, Tabellen 15.1.c.(1) und 15.1.d.(1)

Ebenfalls nicht enthalten sind das Suchprotokoll, die Volltext- und Kernsetnotizen und das
Zahlenprotokoll des Papiers. Sie sind beim Verfasser zu haben.

## Zitieren

Siehe `CITATION.cff`. Wer eine Rechnung nachvollzieht, zitiert das Working Paper, dieses Archiv
und den Rechenkern.

## Lizenz

MIT, wie der Rechenkern. Siehe `LICENSE`.
