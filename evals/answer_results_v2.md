# Antwort-Eval: Lauf v2 – geschärfter Antwort-Prompt (knapp, keine Folgerungen/Beispiele, sachlicher Ton, ältere Quelle als veraltet kennzeichnen)

Stand: 2026-09-23 16:15 · 27 Fragen × 2 Varianten · Antwortmodell `claude-haiku-4-5`, Judge `claude-sonnet-5`, Retrieval `bge-m3`

Varianten: `articles` Top-3 ganze Artikel · `corpus` alle 20 Artikel (Prompt Caching)

Spalten: `quellen_ok` automatisch (Scoring-Regel; bei veraltet ist ein Zitat der alten Preisseite nur ok, wenn der Judge sie als ausdrücklich veraltet gekennzeichnet bewertet (`veraltet_gekennzeichnet`); bei luecke ok, wenn nichts zitiert) · `kernaussage_ok` Judge, ohne luecke · `treu` Judge, Faithfulness gegen den mitgegebenen Kontext · `luecke_ok` Judge, nur luecke · `alles_ok` alle zutreffenden Spalten ok

**Ein Lauf, kleine Stichprobe:** Eine Frage entspricht 4 Prozentpunkten (n=27), in den Typ-Spalten 20–33. Judge-Kalibrierung: `judge_stichprobe.md` und `docs/decisions.md`.

## Gesamt

| Variante | quellen_ok | kernaussage_ok | treu | luecke_ok | **alles_ok** |
|---|---|---|---|---|---|
| articles | 26/27 (96%) | 21/23 (91%) | 25/27 (93%) | 4/4 (100%) | **23/27 (85%)** |
| corpus | 24/27 (89%) | 19/23 (83%) | 21/27 (78%) | 3/4 (75%) | **20/27 (74%)** |

## alles_ok nach typ

| Variante | aehnlich (n=4) | einfach (n=12) | luecke (n=4) | mehrquellen (n=4) | veraltet (n=3) |
|---|---|---|---|---|---|
| articles | 3/4 | 12/12 | 4/4 | 1/4 | 3/3 |
| corpus | 3/4 | 11/12 | 3/4 | 1/4 | 2/3 |

## kernaussage_ok nach typ

| Variante | aehnlich (n=4) | einfach (n=12) | mehrquellen (n=4) | veraltet (n=3) |
|---|---|---|---|---|
| articles | 4/4 | 12/12 | 2/4 | 3/3 |
| corpus | 4/4 | 12/12 | 1/4 | 2/3 |

## quellen_ok nach typ

| Variante | aehnlich (n=4) | einfach (n=12) | luecke (n=4) | mehrquellen (n=4) | veraltet (n=3) |
|---|---|---|---|---|---|
| articles | 4/4 | 12/12 | 4/4 | 3/4 | 3/3 |
| corpus | 4/4 | 12/12 | 4/4 | 2/4 | 2/3 |

## treu nach typ

| Variante | aehnlich (n=4) | einfach (n=12) | luecke (n=4) | mehrquellen (n=4) | veraltet (n=3) |
|---|---|---|---|---|---|
| articles | 3/4 | 12/12 | 4/4 | 3/4 | 3/3 |
| corpus | 3/4 | 11/12 | 3/4 | 2/4 | 2/3 |

## alles_ok nach herkunft

| Variante | entwurf (n=17) | mensch (n=5) | mensch_korrigiert (n=5) |
|---|---|---|---|
| articles | 14/17 | 5/5 | 4/5 |
| corpus | 13/17 | 4/5 | 3/5 |

## kernaussage_ok nach herkunft

| Variante | entwurf (n=17) | mensch (n=5) | mensch_korrigiert (n=5) |
|---|---|---|---|
| articles | 13/15 | 5/5 | 3/3 |
| corpus | 13/15 | 4/5 | 2/3 |

## quellen_ok nach herkunft

| Variante | entwurf (n=17) | mensch (n=5) | mensch_korrigiert (n=5) |
|---|---|---|---|
| articles | 16/17 | 5/5 | 5/5 |
| corpus | 16/17 | 4/5 | 4/5 |

## treu nach herkunft

| Variante | entwurf (n=17) | mensch (n=5) | mensch_korrigiert (n=5) |
|---|---|---|---|
| articles | 16/17 | 5/5 | 4/5 |
| corpus | 14/17 | 4/5 | 3/5 |

## Veraltete Preisseite

| Variante | zitiert alte Seite (alle Fragen) | davon als veraltet gekennzeichnet | veraltet-Fragen: quellen_ok | veraltet-Fragen: kernaussage_ok |
|---|---|---|---|---|
| articles | 2 (#3, #5) | 1 (#3) | 3/3 | 3/3 |
| corpus | 2 (#2, #3) | 1 (#2) | 2/3 | 2/3 |

## Kosten pro 1000 Anfragen (Haiku 4.5, gemessen aus `usage`)

Preise: Input 1,00 · Cache-Write 1,25 · Cache-Read 0,10 · Output 5,00 USD pro 1M Tokens. Retrieval-Embeddings laufen lokal und kosten nichts.

| Variante | Ø Input-Tokens | davon Cache-Read | Ø Output-Tokens | Input | Cache-Write | Cache-Read | Output | **Summe / 1000** |
|---|---|---|---|---|---|---|---|---|
| articles | 2,396 | 0 | 180 | 2.40 | 0.00 | 0.00 | 0.90 | **3.29 USD** |
| corpus | 13,181 | 12,654 | 191 | 0.04 | 0.61 | 1.27 | 0.96 | **2.87 USD** |

Einordnung `corpus`: Im Lauf kam auf 27 Anfragen ein Cache-Write. Ohne Caching wären es **14.14 USD** pro 1000 Anfragen, bei durchgehend warmem Cache (nur Reads) **2.31 USD**. Der Cache hält 5 Minuten; bei weniger Traffic fallen mehr Writes an.

## Latenz (Sekunden, lokales Retrieval + Haiku-Aufruf)

| Variante | Median | p95 | davon Retrieval Median |
|---|---|---|---|
| articles | 2.62 | 4.50 | 102 ms |
| corpus | 3.29 | 6.35 | 0 ms |

p95 aus 27 Messungen je Variante ist nur grob belastbar.

## Nicht alles_ok

| Variante | Fragen (fehlgeschlagene Spalten) |
|---|---|
| articles | #10 (treu), #19 (kernaussage_ok), #21 (treu), #27 (quellen_ok, kernaussage_ok) |
| corpus | #3 (quellen_ok, kernaussage_ok, treu), #8 (treu, luecke_ok), #10 (quellen_ok, kernaussage_ok, treu), #15 (treu), #19 (kernaussage_ok, treu), #21 (treu), #27 (quellen_ok, kernaussage_ok) |

## Vergleich v1 → v2

Gleiche Fragen, gleiches Modell, gleicher Kontext, gleicher Judge – nur der Antwort-Prompt ist anders. v1-Werte nach der angepassten `quellen_ok`-Regel.

| Variante | Lauf | quellen_ok | kernaussage_ok | treu | luecke_ok | **alles_ok** | Kosten / 1000 | Median | p95 | Ø Output-Tokens | Ø Wörter |
|---|---|---|---|---|---|---|---|---|---|---|---|
| articles | v1 | 26/27 | 21/23 | 21/27 | 4/4 | **19/27** | 3.45 USD | 3.19 s | 4.59 s | 233 | 93 |
| articles | v2 | 26/27 | 21/23 | 25/27 | 4/4 | **23/27** | 3.29 USD | 2.62 s | 4.50 s | 180 | 70 |
| corpus | v1 | 27/27 | 21/23 | 21/27 | 4/4 | **20/27** | 3.17 USD | 3.46 s | 5.32 s | 254 | 101 |
| corpus | v2 | 24/27 | 19/23 | 21/27 | 3/4 | **20/27** | 2.87 USD | 3.29 s | 6.35 s | 191 | 74 |

### Änderungen je Frage (v1 → v2)

| Variante | Frage | Typ | Kriterium | v1 | v2 |
|---|---|---|---|---|---|
| articles | #2 | veraltet | treu | ❌ | ✅ |
| articles | #4 | einfach | treu | ❌ | ✅ |
| articles | #10 | mehrquellen | quellen_ok | ❌ | ✅ |
| articles | #10 | mehrquellen | kernaussage_ok | ❌ | ✅ |
| articles | #10 | mehrquellen | treu | ✅ | ❌ |
| articles | #12 | einfach | treu | ❌ | ✅ |
| articles | #15 | einfach | treu | ❌ | ✅ |
| articles | #18 | einfach | kernaussage_ok | ❌ | ✅ |
| articles | #19 | mehrquellen | kernaussage_ok | ✅ | ❌ |
| articles | #27 | mehrquellen | quellen_ok | ✅ | ❌ |
| articles | #27 | mehrquellen | kernaussage_ok | ✅ | ❌ |
| articles | #27 | mehrquellen | treu | ❌ | ✅ |
| corpus | #3 | veraltet | quellen_ok | ✅ | ❌ |
| corpus | #3 | veraltet | treu | ✅ | ❌ |
| corpus | #8 | luecke | treu | ✅ | ❌ |
| corpus | #8 | luecke | luecke_ok | ✅ | ❌ |
| corpus | #10 | mehrquellen | quellen_ok | ✅ | ❌ |
| corpus | #14 | einfach | treu | ❌ | ✅ |
| corpus | #18 | einfach | treu | ❌ | ✅ |
| corpus | #19 | mehrquellen | kernaussage_ok | ✅ | ❌ |
| corpus | #19 | mehrquellen | treu | ✅ | ❌ |
| corpus | #23 | aehnlich | treu | ❌ | ✅ |
| corpus | #27 | mehrquellen | quellen_ok | ✅ | ❌ |
| corpus | #27 | mehrquellen | kernaussage_ok | ✅ | ❌ |
