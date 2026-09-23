# Antwort-Eval: Lauf v1 – erster Antwort-Prompt

Stand: 2026-09-23 15:51 · 27 Fragen × 4 Varianten · Antwortmodell `claude-haiku-4-5`, Judge `claude-sonnet-5`, Retrieval `bge-m3`

Varianten: `sections` Top-4 Abschnitte · `contextual` Top-4 Abschnitte mit Kontextsatz · `articles` Top-3 ganze Artikel · `corpus` alle 20 Artikel (Prompt Caching)

Spalten: `quellen_ok` automatisch (Scoring-Regel; bei veraltet ist ein Zitat der alten Preisseite nur ok, wenn der Judge sie als ausdrücklich veraltet gekennzeichnet bewertet (`veraltet_gekennzeichnet`); bei luecke ok, wenn nichts zitiert) · `kernaussage_ok` Judge, ohne luecke · `treu` Judge, Faithfulness gegen den mitgegebenen Kontext · `luecke_ok` Judge, nur luecke · `alles_ok` alle zutreffenden Spalten ok

**Ein Lauf, kleine Stichprobe:** Eine Frage entspricht 4 Prozentpunkten (n=27), in den Typ-Spalten 20–33. Judge-Kalibrierung: `judge_stichprobe.md` und `docs/decisions.md`.

## Gesamt

| Variante | quellen_ok | kernaussage_ok | treu | luecke_ok | **alles_ok** |
|---|---|---|---|---|---|
| sections | 22/27 (81%) | 17/23 (74%) | 24/27 (89%) | 4/4 (100%) | **19/27 (70%)** |
| contextual | 21/27 (78%) | 15/23 (65%) | 25/27 (93%) | 3/4 (75%) | **17/27 (63%)** |
| articles | 26/27 (96%) | 21/23 (91%) | 21/27 (78%) | 4/4 (100%) | **19/27 (70%)** |
| corpus | 27/27 (100%) | 21/23 (91%) | 21/27 (78%) | 4/4 (100%) | **20/27 (74%)** |

## alles_ok nach typ

| Variante | aehnlich (n=4) | einfach (n=12) | luecke (n=4) | mehrquellen (n=4) | veraltet (n=3) |
|---|---|---|---|---|---|
| sections | 3/4 | 8/12 | 4/4 | 1/4 | 3/3 |
| contextual | 3/4 | 9/12 | 3/4 | 1/4 | 1/3 |
| articles | 3/4 | 8/12 | 4/4 | 2/4 | 2/3 |
| corpus | 2/4 | 9/12 | 4/4 | 3/4 | 2/3 |

## kernaussage_ok nach typ

| Variante | aehnlich (n=4) | einfach (n=12) | mehrquellen (n=4) | veraltet (n=3) |
|---|---|---|---|---|
| sections | 4/4 | 9/12 | 1/4 | 3/3 |
| contextual | 3/4 | 10/12 | 1/4 | 1/3 |
| articles | 4/4 | 11/12 | 3/4 | 3/3 |
| corpus | 4/4 | 12/12 | 3/4 | 2/3 |

## quellen_ok nach typ

| Variante | aehnlich (n=4) | einfach (n=12) | luecke (n=4) | mehrquellen (n=4) | veraltet (n=3) |
|---|---|---|---|---|---|
| sections | 4/4 | 9/12 | 4/4 | 2/4 | 3/3 |
| contextual | 4/4 | 11/12 | 4/4 | 1/4 | 1/3 |
| articles | 4/4 | 12/12 | 4/4 | 3/4 | 3/3 |
| corpus | 4/4 | 12/12 | 4/4 | 4/4 | 3/3 |

## treu nach typ

| Variante | aehnlich (n=4) | einfach (n=12) | luecke (n=4) | mehrquellen (n=4) | veraltet (n=3) |
|---|---|---|---|---|---|
| sections | 3/4 | 11/12 | 4/4 | 3/4 | 3/3 |
| contextual | 3/4 | 11/12 | 4/4 | 4/4 | 3/3 |
| articles | 3/4 | 9/12 | 4/4 | 3/4 | 2/3 |
| corpus | 2/4 | 9/12 | 4/4 | 3/4 | 3/3 |

## alles_ok nach herkunft

| Variante | entwurf (n=17) | mensch (n=5) | mensch_korrigiert (n=5) |
|---|---|---|---|
| sections | 12/17 | 4/5 | 3/5 |
| contextual | 12/17 | 3/5 | 2/5 |
| articles | 12/17 | 3/5 | 4/5 |
| corpus | 12/17 | 4/5 | 4/5 |

## kernaussage_ok nach herkunft

| Variante | entwurf (n=17) | mensch (n=5) | mensch_korrigiert (n=5) |
|---|---|---|---|
| sections | 11/15 | 4/5 | 2/3 |
| contextual | 10/15 | 3/5 | 2/3 |
| articles | 14/15 | 5/5 | 2/3 |
| corpus | 15/15 | 4/5 | 2/3 |

## quellen_ok nach herkunft

| Variante | entwurf (n=17) | mensch (n=5) | mensch_korrigiert (n=5) |
|---|---|---|---|
| sections | 14/17 | 4/5 | 4/5 |
| contextual | 14/17 | 3/5 | 4/5 |
| articles | 17/17 | 5/5 | 4/5 |
| corpus | 17/17 | 5/5 | 5/5 |

## treu nach herkunft

| Variante | entwurf (n=17) | mensch (n=5) | mensch_korrigiert (n=5) |
|---|---|---|---|
| sections | 16/17 | 5/5 | 3/5 |
| contextual | 16/17 | 5/5 | 4/5 |
| articles | 13/17 | 3/5 | 5/5 |
| corpus | 12/17 | 5/5 | 4/5 |

## Veraltete Preisseite

| Variante | zitiert alte Seite (alle Fragen) | davon als veraltet gekennzeichnet | veraltet-Fragen: quellen_ok | veraltet-Fragen: kernaussage_ok |
|---|---|---|---|---|
| sections | 3 (#3, #5, #10) | 1 (#3) | 3/3 | 3/3 |
| contextual | 4 (#3, #5, #10, #26) | 0 (–) | 1/3 | 1/3 |
| articles | 2 (#3, #5) | 1 (#3) | 3/3 | 3/3 |
| corpus | 2 (#3, #10) | 1 (#3) | 3/3 | 2/3 |

## Kosten pro 1000 Anfragen (Haiku 4.5, gemessen aus `usage`)

Preise: Input 1,00 · Cache-Write 1,25 · Cache-Read 0,10 · Output 5,00 USD pro 1M Tokens. Retrieval-Embeddings laufen lokal und kosten nichts.

| Variante | Ø Input-Tokens | davon Cache-Read | Ø Output-Tokens | Input | Cache-Write | Cache-Read | Output | **Summe / 1000** |
|---|---|---|---|---|---|---|---|---|
| sections | 1,021 | 0 | 195 | 1.02 | 0.00 | 0.00 | 0.98 | **2.00 USD** |
| contextual | 1,477 | 0 | 201 | 1.48 | 0.00 | 0.00 | 1.00 | **2.48 USD** |
| articles | 2,284 | 0 | 232 | 2.28 | 0.00 | 0.00 | 1.16 | **3.45 USD** |
| corpus | 13,072 | 12,549 | 254 | 0.04 | 0.60 | 1.25 | 1.27 | **3.17 USD** |

Einordnung `corpus`: Im Lauf kam auf 27 Anfragen ein Cache-Write. Ohne Caching wären es **14.34 USD** pro 1000 Anfragen, bei durchgehend warmem Cache (nur Reads) **2.61 USD**. Der Cache hält 5 Minuten; bei weniger Traffic fallen mehr Writes an.

## Latenz (Sekunden, lokales Retrieval + Haiku-Aufruf)

| Variante | Median | p95 | davon Retrieval Median |
|---|---|---|---|
| sections | 2.67 | 3.48 | 99 ms |
| contextual | 2.80 | 3.69 | 92 ms |
| articles | 3.19 | 4.59 | 90 ms |
| corpus | 3.46 | 5.32 | 0 ms |

p95 aus 27 Messungen je Variante ist nur grob belastbar.

## Nicht alles_ok

| Variante | Fragen (fehlgeschlagene Spalten) |
|---|---|
| sections | #4 (quellen_ok, kernaussage_ok), #9 (treu), #10 (quellen_ok, kernaussage_ok, treu), #14 (quellen_ok, kernaussage_ok), #18 (quellen_ok, kernaussage_ok), #19 (quellen_ok, kernaussage_ok), #22 (treu), #27 (kernaussage_ok) |
| contextual | #3 (quellen_ok, kernaussage_ok), #4 (quellen_ok, kernaussage_ok), #8 (luecke_ok), #9 (treu), #10 (quellen_ok, kernaussage_ok), #13 (kernaussage_ok), #19 (quellen_ok, kernaussage_ok), #21 (kernaussage_ok, treu), #26 (quellen_ok, kernaussage_ok), #27 (quellen_ok, kernaussage_ok) |
| articles | #2 (treu), #4 (treu), #10 (quellen_ok, kernaussage_ok), #12 (treu), #15 (treu), #18 (kernaussage_ok), #21 (treu), #27 (treu) |
| corpus | #3 (kernaussage_ok), #10 (kernaussage_ok, treu), #14 (treu), #15 (treu), #18 (treu), #21 (treu), #23 (treu) |
