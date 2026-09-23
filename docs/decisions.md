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
