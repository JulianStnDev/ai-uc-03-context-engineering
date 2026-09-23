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
