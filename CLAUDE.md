# Projekt-Kontext

## Problem
Ein Support-Assistent beantwortet Kundenfragen zur fiktiven Habit-Tracker-App
**FocusFlow** ausschließlich aus der Hilfe-Doku in `corpus/` – mit Quellenangabe
(welcher Artikel). Verglichen werden drei Ansätze, dem Modell den richtigen
Kontext zu geben:

1. **Klassisches Chunking** – Artikel in Chunks zerlegen, embedden, Top-k per Ähnlichkeit
2. **Contextual Retrieval** – jeder Chunk bekommt vor dem Embedding einen vom LLM
   erzeugten Kontext-Satz zum Gesamtdokument
3. **Ganzer Korpus im Kontextfenster** – kein Retrieval, alle Artikel im Prompt

Der Korpus enthält absichtlich Fallen (veraltete Seite, Lücken, Mehrquellen-Fragen,
ähnlich klingende Artikel) – Details in `corpus/CORPUS_NOTES.md`. Die Datei ist
Dokumentation für Menschen und darf **nie** Teil des Retrieval-Korpus oder Prompts sein.

## Erwartete Artefakte
- README.md nach Schema (Problem, PM-Entscheidung, Architektur, Eval, Kosten/Latenz, Learnings)
- meta.json gepflegt (status ausschließlich: planned | active | done)
- evals/ mit Datensatz + Ergebnissen
- docs/decisions.md mit datierten Entscheidungen

## Erlaubte Libraries
- anthropic, sentence-transformers, numpy, python-dotenv
- Direkt gegen das SDK, kein LangChain/LlamaIndex
- Keine Vektor-Datenbank – Embeddings als numpy-Arrays reichen bei ~20 Artikeln

## Stil
- Python, einfache Skripte statt Frameworks
- Drei Zahlen im README Pflicht: Kosten/1000 Requests, p95-Latenz, Qualitätsmetrik

## Arbeitsweise
- Nie direkt auf `main` committen. Pro Arbeitspaket ein Feature-Branch
  (`feat/...`, `fix/...`), am Ende Pull Request öffnen (per `gh`, falls
  installiert, sonst Branch pushen und Link zum PR-Anlegen ausgeben).
- Merge macht Julian selbst nach Review.
- `.env` (ANTHROPIC_API_KEY) ist gitignored und wird nie committet.
