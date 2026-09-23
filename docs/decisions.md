# Entscheidungen

<!-- Format:
## YYYY-MM-DD: Kurztitel
Kontext, Optionen, Entscheidung, Begründung
-->

## 2026-09-18: Status-Vokabular für meta.json

Kontext: meta.json legt "status": "planned" fest, ohne definierte erlaubte Werte —
das driftet über mehrere Repos auseinander (planned/in-progress/wip/...).

Optionen: (a) einfach: planned → active → done, (b) zusätzlich mit
parked/abandoned für verworfene Use Cases, (c) feiner: research →
building → evaluating → shipped.

Entscheidung: (a) — planned, active, done. Zusätzlich in CLAUDE.md verankert.

Begründung: Bei einem Solo-Portfolio mit meist einem aktiven Repo lohnt sich
keine feinere Staffelung. CLAUDE.md-Verankerung, damit der Agent das Vokabular
bei jedem neuen Repo automatisch mitliest statt dass ich mich erinnern muss.

## 2026-09-23: Lokales Embedding-Modell statt Embedding-API

Kontext: Für klassisches Chunking und Contextual Retrieval brauchen wir
Embeddings für ~20 Artikel (plus Chunks) und für jede Testfrage.

Optionen: (a) Embedding-API eines Anbieters (z. B. Voyage, OpenAI),
(b) lokales Modell über sentence-transformers.

Entscheidung: (b) — lokales Modell über sentence-transformers.

Begründung:
- Keine laufenden Kosten: Embeddings werden bei jedem Chunking-Experiment neu
  berechnet, lokal kostet das nur Rechenzeit. Die Kosten/1000 Requests im
  README bleiben damit reine LLM-Kosten und lassen sich sauber vergleichen.
- Keine Daten verlassen den Rechner: Bei einem echten Support-Korpus mit
  internen Dokumenten wäre das ein Argument gegenüber Datenschutz/Security.
- Lernbar: Man sieht direkt, was ein Embedding-Modell tut (Vektoren,
  Normalisierung, Cosinus-Ähnlichkeit mit numpy), statt nur einen API-Call
  zu machen.
- Trade-off: Lokale Modelle sind oft schwächer als die besten API-Modelle.
  Genau das soll die Eval sichtbar machen. Wenn das Retrieval am Modell
  scheitert, ist ein API-Modell die nächste Option.

## 2026-09-23: Mehrsprachiges Embedding-Modell

Kontext: Der Korpus (FocusFlow-Hilfe) und die erwarteten Kundenfragen sind
auf Deutsch. Viele verbreitete sentence-transformers-Modelle sind rein
englisch trainiert.

Optionen: (a) englisches Standardmodell, (b) mehrsprachiges Modell,
(c) Korpus und Fragen vorher ins Englische übersetzen.

Entscheidung: (b) — ein mehrsprachiges Modell. Welches konkret, wird im
nächsten Schritt entschieden (Kandidaten vergleichen nach Größe, Qualität
auf Deutsch, Laufzeit auf dem Laptop).

Begründung: Englische Modelle zerlegen deutsche Komposita („Doppelabbuchung“,
„Erstattungsrichtlinie“) in wenig aussagekräftige Tokens, und die Ähnlichkeit
wird unzuverlässig. Übersetzen (c) fügt eine zusätzliche Fehlerquelle und
LLM-Kosten hinzu und verfälscht den Vergleich der Retrieval-Ansätze.

## 2026-09-23: Scoring-Regel für erwartete Quellen

Kontext: Im Goldset haben auch einige Fragen vom Typ `einfach` mehrere
erwartete Quellen (#5, #9, #13), weil die Antwort in mehr als einem Artikel
steht. Für die Quellen-Metrik muss klar sein, ob alle oder eine davon nötig sind.

Optionen: (a) eigene Spalte für die Semantik, (b) Semantik aus `typ` ableiten.

Entscheidung: (b). `mehrquellen` gilt als erfüllt, wenn **alle** erwarteten
Quellen gefunden bzw. zitiert wurden. Bei allen anderen Typen reicht **eine**.
`luecke` (Quelle „keine“) wird separat bewertet: Richtig ist es, wenn das
System keine Quelle behauptet und auf den Support verweist.

Begründung: Die CSV-Struktur bleibt unverändert, und die Regel entspricht dem,
was der Typ ohnehin aussagt.

## 2026-09-23: Goldset enthält ungeprüfte Claude-Entwürfe

Kontext: Von 27 Erwartungen im Goldset (`evals/goldset.csv`) stammen 17
(`herkunft = entwurf`) von Claude. Sie wurden nur maschinell gegen den
Korpustext geprüft, nicht von mir abgenommen. Beim Gegencheck ist bereits eine
Überinterpretation aufgefallen: #18 behauptete „volle Belastung deutet auf
Doppelabbuchung hin“. Das ist eine Schlussfolgerung, die so nicht im Korpus
steht. #18 ist korrigiert, weitere Fälle dieser Art sind möglich.

Optionen: (a) alle 17 vor dem ersten Eval-Lauf manuell prüfen,
(b) Entwürfe entfernen und nur mit 10 geprüften Fragen messen,
(c) drin lassen und transparent machen.

Entscheidung: (c). Die Entwurf-Zeilen bleiben bewusst ungeprüft im Goldset.

Gegenmaßnahme: Alle Metriken werden zusätzlich nach `herkunft` aufgeschlüsselt
(mensch / mensch_korrigiert / entwurf). Weichen die Entwurf-Zeilen auffällig
ab, prüfe ich zuerst die Erwartung und erst danach das System.

Begründung: Zehn Fragen reichen für einen Vergleich von drei Ansätzen über fünf
Fallentypen nicht aus. Die Aufschlüsselung macht sichtbar, ob ein Ergebnis an
ungeprüften Erwartungen hängt. Im README später unter „Grenzen“ erwähnen.

## 2026-09-23: Modellwahl für Embeddings, Antworten und Judge

Kontext: Die Kandidaten sind im Plan verglichen worden. Die Hardware ist ein
MacBook mit M5 und 16 GB.

Entscheidung:
- **Embedding:** `intfloat/multilingual-e5-base` als Hauptmodell,
  `BAAI/bge-m3` als kostenlose Gegenprobe. bge-m3 wird nur für den
  Retrieval-Recall genutzt, nicht in der Antwortstufe.
- **Antwortmodell:** `claude-haiku-4-5`, damit die Kosten mit UC1 und UC2
  vergleichbar sind.
- **Kontextsätze für Contextual Retrieval** (beim Indexieren): ebenfalls
  `claude-haiku-4-5`.
- **Judge:** `claude-sonnet-5`. Ein anderes Modell als das bewertete, damit
  Haiku nicht seine eigenen Antworten benotet.

Verworfen: `paraphrase-multilingual-MiniLM-L12-v2`. Es ist auf
Satz-Ähnlichkeit statt auf Retrieval trainiert, und die maximale Länge von
128 Tokens hätte die Chunks abgeschnitten.

## 2026-09-23: Drei Chunking-Varianten, keine festen Fenster

Kontext: Wir brauchen eine Baseline und Vergleichsvarianten für das Retrieval.

Entscheidung:
- (a) `sections`: ein Chunk pro `##`-Abschnitt, ohne Artikeltitel und Datum.
  Das ist die Baseline.
- (b) `articles`: der ganze Artikel als ein Chunk.
- (c) `contextual`: Abschnitte wie in (a), davor ein von Haiku erzeugter
  Kontextsatz zum Gesamtartikel. Der Prompt ist eine wörtliche Übersetzung
  aus Anthropics Beitrag zu Contextual Retrieval. Er fordert bewusst nicht
  auf, Titel oder Datum zu nennen, damit das Verfahren unverändert bleibt.

Feste Fenster mit Überlappung sind **bewusst weggelassen**. Die Hilfe-Doku ist
mit Überschriften strukturiert, und die Artikel sind kurz (etwa 200–260 Wörter,
maximal 456 Tokens). Feste Fenster würden Abschnitte willkürlich zerschneiden,
obwohl die natürlichen Grenzen schon vorhanden sind. Sie wären ein Strohmann,
keine sinnvolle Baseline.

## 2026-09-23: Pipeline geteilt – erst Retrieval, dann Antworten

Kontext: Retrieval-Fehler und Antwortfehler vermischen sich, wenn man nur die
Endqualität misst.

Entscheidung: Der Branch `feat/retrieval-pipeline` umfasst nur Laden,
Chunking, Embedding und Retrieval-Scoring. Einzige API-Kosten sind die
Kontextsätze. Antwortstufe und Judge kommen erst in einem eigenen Branch,
nachdem die Retrieval-Zahlen ausgewertet sind.

Metrik: Recall@k über die Top-k **Chunks**. Eine Quelle gilt als gefunden,
wenn mindestens ein Chunk des Artikels unter den Top-k ist. Das entspricht dem,
was die Antwortstufe später als Kontext bekommt. Fragen vom Typ `luecke` gehen
nicht in den Recall ein, für sie wird die Top-1-Ähnlichkeit berichtet. Für
`mehrquellen` ist Recall@1 strukturell 0.

## 2026-09-23: Wechsel des Embedding-Modells auf bge-m3

Kontext: `multilingual-e5-base` war die ursprüngliche Wahl, `bge-m3` nur als
kostenlose Gegenprobe gedacht. In der Retrieval-Eval
(`evals/retrieval_results.md`) hat bge-m3 e5-base in fast allen Varianten
geschlagen. Recall@3: sections 0.78 gegenüber 0.70, articles 1.00 gegenüber
0.78, contextual gleichauf bei 0.83.

Entscheidung: Ab jetzt ist `BAAI/bge-m3` das Embedding-Modell für die
Antwortstufe.

Begründung: Das Modell ist ein messbarer Hebel. Die höheren Kosten (größeres
Modell, rund 2 ms mehr pro Query) sind lokal vernachlässigbar.

## 2026-09-23: Aufbau der Antwortstufe

Entscheidung:
- **Vier Varianten**, alle mit bge-m3:
  - (a) `sections`: Top-4 Abschnitte
  - (b) `contextual`: Top-4 Abschnitte mit Kontextsatz
  - (c) `articles`: Top-3 ganze Artikel
  - (d) `corpus`: alle 20 Artikel im Kontext, mit Prompt Caching
- **Antwortmodell** `claude-haiku-4-5` mit temperature 0. **Judge**
  `claude-sonnet-5`.
- **Ein gemeinsamer Antwort-Prompt** für alle Varianten:
  - nur aus dem Kontext antworten
  - Dateinamen in einer abschließenden Zeile „Quellen:“ nennen
  - bei fehlender Info auf den Support verweisen, ohne inhaltliche Antwort
  - bei Widerspruch gilt die Quelle mit dem neueren Datum
- **Kontextformat:** Jede Quelle steht als
  `<quelle datei=… titel=… aktualisiert=…>` im Kontext, das Datum ist also
  überall sichtbar. Bei `sections` und `contextual` bekommt das Antwortmodell
  damit Titel und Datum zu sehen, obwohl sie nicht embedded wurden.
- **Bewertung in getrennten Spalten:**
  - `quellen_ok`: automatisch nach der Scoring-Regel. Bei `veraltet` zählt
    ein Zitat von `pro-funktionen-und-preise.md` als Fehler. Bei `luecke` ist
    es ok, wenn nichts zitiert wird.
  - `kernaussage_ok`: Judge, nur bei Typen ungleich `luecke`
  - `treu`: Judge, Faithfulness. Der Judge sieht den Kontext, den das
    Antwortmodell bekommen hat.
  - `luecke_ok`: Judge, nur bei `luecke`. Richtig ist ausschließlich ein
    Support-Verweis ohne inhaltliche Antwort.
  - Dazu `alles_ok` als strenge Gesamtspalte.
- **Judge-Aufruf:** einer pro Antwort mit Structured Output, der zwei Kriterien
  prüft und je eine Begründung liefert. Beim Kriterium `luecke` wird bewusst
  keine `kernaussage_ok` erhoben, weil die Kernaussage dort genau dem
  Support-Verweis entspricht und die Spalte doppelt zählen würde.
- **Kalibrierung:** 10 zufällige Urteile (Seed 42, gestreut über Varianten,
  Typen und Kriterien) in `evals/judge_stichprobe.md`. Julian prüft sie von
  Hand.

## 2026-09-23: quellen_ok bei `veraltet` nach Lauf 1 gelockert

Kontext: Die ursprüngliche Regel lautete: Bei Fragen vom Typ `veraltet` ist
jedes Zitat von `pro-funktionen-und-preise.md` ein Fehler. In Lauf 1 hat das
genau das gewünschte Verhalten bestraft. Bei #3 (sections, articles, corpus)
nannte Haiku die aktuellen Werte, kennzeichnete die alte Seite ausdrücklich als
überholt und zitierte transparent beide Seiten. Dafür gab es `quellen_ok = 0`.

Entscheidung: **Die Regel wurde nach dem Lauf geändert.** Ein Zitat der alten
Seite ist erlaubt, wenn die Antwort sie ausdrücklich als veraltet oder überholt
kennzeichnet und die aktuellen Werte nennt. Das prüft der Judge in einer neuen
Spalte `veraltet_gekennzeichnet`, und zwar nur bei Antworten, die die alte
Seite zitieren. Er sieht dafür beide Preisseiten. Lauf 1 wurde ohne neue
Antworten neu gescored. Die zusätzlichen 11 Judge-Aufrufe kosten 0,09 USD.

Begründung: Die strenge Regel hat Transparenz bestraft. Ein Support-Assistent,
der den Widerspruch offenlegt, ist besser als einer, der die alte Quelle
verschweigt. Weil die Regeländerung nach Ansicht der Ergebnisse kam, stehen hier
beide Stände:

| Variante | quellen_ok vorher → nachher | alles_ok vorher → nachher |
|---|---|---|
| sections | 21/27 → 22/27 | 18/27 → 19/27 |
| contextual | 21/27 → 21/27 | 17/27 → 17/27 |
| articles | 25/27 → 26/27 | 18/27 → 19/27 |
| corpus | 26/27 → 27/27 | 20/27 → 20/27 (#3 scheitert weiter an kernaussage_ok: „Ja, es gibt eine Testphase! … derzeit keine Testphase“) |

Bei contextual #3 und #26 steht die alte Seite als gültig da, dort bleibt es
beim Fehler.

## 2026-09-23: Lauf v2 – geschärfter Antwort-Prompt (nur articles und corpus)

Kontext: In Lauf 1 fielen articles und corpus vor allem bei `treu` ab
(je 21/27). Die Ursachen waren kleine Ausschmückungen („Drittländer wie die
USA“, „vielleicht ein veralteter Browser-Cache“) und ein geschwätziger Ton.

Änderung am Antwort-Prompt, alles andere identisch (Modell, Kontext, Judge,
Goldset):
- knapp antworten
- keine Aussagen, die nicht im Kontext stehen, auch keine naheliegenden
  Folgerungen oder Beispiele
- sachlicher Ton ohne Emojis und ohne Floskeln
- bei Widerspruch die neuere Quelle nennen und die ältere als veraltet
  kennzeichnen

Die Ergebnisse von Lauf 1 bleiben unverändert erhalten
(`data/answers.jsonl`, `evals/answer_results.md`). v2 liegt in `*_v2`.

Ergebnis (`evals/answer_results_v2.md`):

| Variante | alles_ok v1 → v2 | treu v1 → v2 | Kosten / 1000 | Median-Latenz | Ø Wörter |
|---|---|---|---|---|---|
| articles | 19 → **23**/27 | 21 → 25 | 3,45 → 3,29 USD | 3,19 → 2,62 s | 93 → 70 |
| corpus | 20 → 20/27 | 21 → 21 | 3,17 → 2,87 USD | 3,46 → 3,29 s | 101 → 74 |

Beobachtungen:
- Bei `articles` wirkt der Prompt wie beabsichtigt: 4 von 6 Treue-Verstößen
  sind weg, und die Antworten sind rund 25 % kürzer.
- Bei `corpus` verschieben sich die Fehler nur. Neue Fehler entstehen durch
  Kürze: Bei #10 und #27 fehlt die Erstattungsregel aus dem zweiten Artikel.
  Dazu kommen neue Erfindungen:
  - #3 löst den Widerspruch mit einer ausgedachten Regel auf („Testphase nur
    im App Store“).
  - #8 behauptet „keine Importfunktion“.
  - #19 widerspricht sich selbst.
- „Knapp“ und „keine Folgerungen“ stehen im Konflikt mit Mehrquellen-Fragen,
  die genau das Zusammenführen zweier Regeln verlangen.

Einschränkung: Es ist ein Lauf je Stand. Trotz temperature 0 ist Haiku nicht
deterministisch. Unterschiede von 1–4 Fragen lassen sich ohne
Wiederholungsläufe nicht sauber vom Rauschen trennen.

## 2026-09-23: Judge-Kalibrierung abgeschlossen

Stichprobe: 10 zufällige Urteile von Sonnet 5 aus Lauf 1 (Seed 42, gestreut
über Varianten, Typen und Kriterien). Details stehen in
`evals/judge_stichprobe.md`, Julians Urteile in `evals/judge_kalibrierung.csv`.

Ergebnis: Julian stimmt 10 von 10 Urteilen zu. Nr. 8 ist ein Grenzfall (#10
articles, `kernaussage_ok`): Die Kernaussage enthielt zwei Aussagen, ohne dass
gekennzeichnet war, welche davon Pflicht ist. Die Übereinstimmung liegt damit
bei 9–10/10, **die Kalibrierung ist bestanden**. Der Judge wird ohne Änderung
weiterverwendet.

Arbeitsteilung:
- Die Bewertungskriterien (`quellen_ok`, `kernaussage_ok`, `treu`,
  `luecke_ok`, `veraltet_gekennzeichnet`) sind von Julian abgenommen.
- Die fachliche Faktenprüfung gegen den Korpus übernimmt Claude, also die
  Frage, ob eine Aussage zum fiktiven Unternehmen FocusFlow stimmt.
- Julian entscheidet die Methode, Claude prüft die Domänenfakten.

Lektion fürs nächste Goldset: **pro Frage genau eine Pflichtaussage**. Weitere
Punkte nur als ausdrücklich gekennzeichnete optionale Ergänzungen. Mehrteilige
Kernaussagen machen `kernaussage_ok` zur Ermessensfrage (siehe Nr. 8).

## 2026-09-23: Python 3.13 über uv, anthropic-SDK 1.x

Kontext: Das Projekt lief auf Apples System-Python 3.9. Diese Version bekommt
keine Sicherheitsupdates mehr, hält das anthropic-SDK auf 0.x fest und bringt
LibreSSL-Warnungen.

Entscheidung:
- Python 3.13 wird über `uv` installiert und ist der Standard auf Mac-Ebene
  (`~/.local/bin`, Eintrag in `~/.zshenv`). Apples 3.9 bleibt unangetastet.
- Pro Repo gibt es weiterhin ein eigenes `.venv`. Die Version ist über
  `.python-version` festgelegt.
- Das venv ist mit `uv venv` + `uv pip install -r requirements.txt` neu
  gebaut. Neue Versionen: anthropic 1.8, sentence-transformers 6.1,
  transformers 5.17, torch 2.14.
- SDK-Breaking-Change: `temperature` ist nicht mehr in der Signatur von
  `messages.create()`. Haiku 4.5 honoriert den Parameter weiterhin, und
  temperature 0 gehört zum Versuchsaufbau. Deshalb wurde er nach
  `extra_body={"temperature": 0}` verschoben, statt ihn zu löschen
  (`chunk.py`, `run_answers.py`).

Geprüft: Die Auswertung (v1, v2) ist identisch. Die Chunk-Embeddings von
bge-m3 sind identisch (Cosinus 1,0). Je ein API-Aufruf an Haiku und an
Sonnet mit Structured Output funktioniert.

## 2026-09-23: Fund – falsches Query-Embedding bei Frage #7 im alten Stack

Beim Gegencheck nach dem Upgrade wich genau eine Retrieval-Liste ab: Frage #7
(„Gibt es Mengenrabatte“, Typ `luecke`) in allen drei bge-m3-Varianten.
Ursache: **torch 2.8 hat auf MPS (Apple-GPU) für diese 8-Token-Anfrage ein
falsches Embedding berechnet.** Der Cosinus zwischen der MPS- und der
CPU-Berechnung im selben alten Stack liegt bei 0,26. Das habe ich in einem
Wegwerf-venv mit dem alten Stack nachgestellt. Alle anderen geprüften Fragen
und alle Chunk-Embeddings waren korrekt. Der neue Stack rechnet auf MPS und
CPU identisch und stimmt mit der alten CPU-Berechnung überein.

Auswirkung auf die veröffentlichten UC3-Ergebnisse:
- Recall ist nicht betroffen, weil `luecke`-Fragen nicht in den Recall
  eingehen.
- Die Tabelle „Lücken-Fragen: Top-1-Ähnlichkeit“ für bge-m3 ist verzerrt.
  Das Minimum von etwa 0,21 stammt von #7, korrekt wäre etwa 0,45. Die
  Trennbarkeit von Lücken per Schwelle wirkte dadurch besser, als sie ist.
- Die Antworten zu #7 in sections, contextual und articles v1 sowie articles
  v2 bekamen einen falschen Kontext (bekannte Probleme, Passwort usw. statt
  der Preisseiten). Alle vier bestanden `luecke_ok`. Mit dem korrekten,
  preisnahen Kontext wäre die Versuchung größer, doch inhaltlich zu antworten.
  Diese vier Lücken-Ergebnisse sind daher eher optimistisch.
- corpus ist nicht betroffen, weil dort kein Retrieval stattfindet.
- Ob die e5-Query-Embeddings ebenfalls betroffen waren, ist offen. e5 ist
  gelöscht, und eine Prüfung würde 1,1 GB Download kosten.

Entscheidung: dokumentieren, nicht neu messen, weil UC3 abgeschlossen ist und
es keine weiteren API-Läufe geben soll.

**Nachtrag, 2026-09-23: doch nachgemessen.** Julian hat entschieden, die vier
betroffenen Antworten zu #7 mit dem neuen Stack neu zu erzeugen und zu bewerten
(4 Haiku- und 4 Judge-Aufrufe, etwa 2 Cent). Die alten Zeilen sind nach
`data/superseded_q7.jsonl` verschoben. Mit korrektem Embedding enthält der
Kontext jetzt `tarif-wechseln.md` und `erstattungen.md`, bei sections und
contextual zusätzlich die veraltete Preisseite. **Ergebnis:** Alle vier
bestehen weiterhin `luecke_ok` und `treu`. Haiku verweist trotz preisnahem
Kontext sauber an den Support, ohne inhaltlich zu antworten. Die
Qualitätstabellen in `evals/answer_results*.md` und im README bleiben
unverändert. Die Kosten für sections v1 ändern sich im Rundungsbereich
(2,00 → 2,01 USD pro 1000). Der Verdacht „eher optimistisch“ hat sich damit
nicht bestätigt. Die Retrieval-Tabelle zur Top-1-Ähnlichkeit der
Lücken-Fragen ist nicht neu berechnet, weil das den gelöschten e5-Download
erfordern würde. Lektion: **GPU-Ergebnisse
stichprobenartig gegen CPU prüfen**, besonders bei älteren
torch-/MPS-Versionen.
