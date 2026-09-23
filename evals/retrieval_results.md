# Retrieval-Eval

Stand: 2026-09-23 12:55 · 27 Fragen, davon 23 mit Quelle (luecke nicht im Recall) · Werte: Recall@1 / @3 / @5 über **Chunks**

Scoring-Regel: `mehrquellen` braucht alle erwarteten Quellen in den Top-k Chunks, alle anderen Typen eine. Recall@1 ist für `mehrquellen` daher strukturell 0 (ein Chunk gehört zu genau einem Artikel).

**Kleine Stichprobe:** Eine Frage entspricht 0,04 im Gesamt-Recall (n=23) und 0,25–0,33 in den Typ-Spalten. Die Variante `articles` hat nur 20 Chunks, Top-5 sind dort bereits 25 % des Korpus.

## Gesamt

| Modell | Variante | R@1 / R@3 / R@5 | Ø Artikel in Top-3 | Ø Wörter in Top-3 | abgeschnittene Chunks | Query p95 (ms) |
|---|---|---|---|---|---|---|
| e5-base | sections | 0.30 / 0.70 / 0.87 | 2.3 | 171 | 0/104 (max 219 / 512 Tokens) | 27.1 |
| e5-base | articles | 0.35 / 0.78 / 0.96 | 3.0 | 716 | 0/20 (max 456 / 512 Tokens) | 21.7 |
| e5-base | contextual | 0.43 / 0.83 / 0.96 | 2.4 | 318 | 0/104 (max 287 / 512 Tokens) | 24.7 |
| bge-m3 | sections | 0.39 / 0.78 / 1.00 | 2.5 | 145 | 0/104 (max 217 / 8192 Tokens) | 51.0 |
| bge-m3 | articles | 0.57 / 1.00 / 1.00 | 3.0 | 721 | 0/20 (max 454 / 8192 Tokens) | 22.1 |
| bge-m3 | contextual | 0.48 / 0.83 / 0.96 | 2.3 | 282 | 0/104 (max 285 / 8192 Tokens) | 22.0 |

## Nach typ

| Modell | Variante | aehnlich (n=4) | einfach (n=12) | mehrquellen (n=4) | veraltet (n=3) |
|---|---|---|---|---|---|
| e5-base | sections | 0.00 / 0.50 / 1.00 | 0.58 / 0.92 / 1.00 | 0.00 / 0.25 / 0.50 | 0.00 / 0.67 / 0.67 |
| e5-base | articles | 0.25 / 0.25 / 1.00 | 0.58 / 1.00 / 1.00 | 0.00 / 0.50 / 0.75 | 0.00 / 1.00 / 1.00 |
| e5-base | contextual | 0.25 / 1.00 / 1.00 | 0.67 / 0.92 / 1.00 | 0.00 / 0.25 / 0.75 | 0.33 / 1.00 / 1.00 |
| bge-m3 | sections | 0.25 / 0.50 / 1.00 | 0.67 / 0.92 / 1.00 | 0.00 / 0.75 / 1.00 | 0.00 / 0.67 / 1.00 |
| bge-m3 | articles | 0.75 / 1.00 / 1.00 | 0.83 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 |
| bge-m3 | contextual | 0.50 / 0.75 / 1.00 | 0.75 / 1.00 / 1.00 | 0.00 / 0.75 / 1.00 | 0.00 / 0.33 / 0.67 |

## Nach herkunft

| Modell | Variante | entwurf (n=15) | mensch (n=5) | mensch_korrigiert (n=3) |
|---|---|---|---|---|
| e5-base | sections | 0.33 / 0.67 / 0.87 | 0.20 / 0.80 / 1.00 | 0.33 / 0.67 / 0.67 |
| e5-base | articles | 0.40 / 0.73 / 1.00 | 0.20 / 1.00 / 1.00 | 0.33 / 0.67 / 0.67 |
| e5-base | contextual | 0.40 / 0.87 / 1.00 | 0.40 / 0.80 / 1.00 | 0.67 / 0.67 / 0.67 |
| bge-m3 | sections | 0.33 / 0.67 / 1.00 | 0.40 / 1.00 / 1.00 | 0.67 / 1.00 / 1.00 |
| bge-m3 | articles | 0.67 / 1.00 / 1.00 | 0.40 / 1.00 / 1.00 | 0.33 / 1.00 / 1.00 |
| bge-m3 | contextual | 0.47 / 0.80 / 0.93 | 0.40 / 0.80 / 1.00 | 0.67 / 1.00 / 1.00 |

## Veraltete Preisseite

Rang des ersten Chunks von `pro-funktionen-und-preise.md` (2024) vs. `preise-und-tarife.md` (2026). Spalte „veraltet in Top-3“ zählt über alle 27 Fragen.

| Modell | Variante | #2 | #3 | #26 | veraltet vor aktuell (veraltet-Fragen) | veraltet in Top-3 (alle Fragen) |
|---|---|---|---|---|---|---|
| e5-base | sections | 1 vs 2 | 1 vs 2 | 6 vs 7 | 3/3 | 5 (#2, #3, #5, #10, #23) |
| e5-base | articles | 1 vs 2 | 1 vs 2 | 3 vs 2 | 2/3 | 5 (#2, #3, #5, #10, #26) |
| e5-base | contextual | 2 vs 1 | 1 vs 3 | 12 vs 2 | 1/3 | 5 (#2, #3, #5, #10, #23) |
| bge-m3 | sections | 1 vs 2 | 1 vs 3 | 1 vs 4 | 3/3 | 5 (#2, #3, #5, #10, #26) |
| bge-m3 | articles | 1 vs 2 | 1 vs 2 | 4 vs 3 | 2/3 | 4 (#2, #3, #5, #6) |
| bge-m3 | contextual | 1 vs 2 | 1 vs 5 | 2 vs 7 | 3/3 | 5 (#2, #3, #5, #10, #26) |

## Lücken-Fragen: Top-1-Ähnlichkeit

Lässt sich „keine passende Quelle“ an einer niedrigen Top-1-Ähnlichkeit erkennen?

| Modell | Variante | luecke Ø (min–max) | mit Quelle Ø (min–max) |
|---|---|---|---|
| e5-base | sections | 0.831 (0.809–0.844) | 0.870 (0.845–0.897) |
| e5-base | articles | 0.813 (0.792–0.822) | 0.855 (0.827–0.875) |
| e5-base | contextual | 0.817 (0.802–0.830) | 0.866 (0.834–0.898) |
| bge-m3 | sections | 0.459 (0.230–0.559) | 0.647 (0.496–0.734) |
| bge-m3 | articles | 0.422 (0.211–0.541) | 0.604 (0.506–0.691) |
| bge-m3 | contextual | 0.429 (0.208–0.513) | 0.630 (0.538–0.721) |

## Verfehlt bei Recall@3

| Modell | Variante | Fragen (Rang aller erwarteten Quellen) |
|---|---|---|
| e5-base | sections | #4 (einfach, Rang 4), #10 (mehrquellen, Rang 9), #19 (mehrquellen, Rang 5), #21 (aehnlich, Rang 4), #22 (aehnlich, Rang 4), #26 (veraltet, Rang 7), #27 (mehrquellen, Rang 8) |
| e5-base | articles | #10 (mehrquellen, Rang 7), #21 (aehnlich, Rang 4), #22 (aehnlich, Rang 4), #23 (aehnlich, Rang 4), #27 (mehrquellen, Rang 4) |
| e5-base | contextual | #4 (einfach, Rang 4), #10 (mehrquellen, Rang 7), #19 (mehrquellen, Rang 4), #27 (mehrquellen, Rang 4) |
| bge-m3 | sections | #14 (einfach, Rang 5), #19 (mehrquellen, Rang 5), #20 (aehnlich, Rang 4), #22 (aehnlich, Rang 4), #26 (veraltet, Rang 4) |
| bge-m3 | articles | – |
| bge-m3 | contextual | #3 (veraltet, Rang 5), #19 (mehrquellen, Rang 5), #22 (aehnlich, Rang 4), #26 (veraltet, Rang 7) |
