"""Retrieval-Eval: Recall@1/3/5 je Embedding-Modell × Chunk-Variante.

Scoring-Regel (docs/decisions.md): typ "mehrquellen" braucht alle erwarteten
Quellen in den Top-k Chunks, alle anderen Typen mindestens eine. Fragen vom Typ
"luecke" haben keine Quelle und gehen nicht in den Recall ein; für sie wird nur
die Top-1-Ähnlichkeit berichtet (Hinweis, ob sich Lücken per Schwelle erkennen lassen).

Ausgaben:
  evals/retrieval_results.md        Tabellen (gesamt, nach typ, nach herkunft, veraltete Seite)
  evals/retrieval_per_question.csv  Treffer je Frage und Konfiguration
  evals/retrieval_top3.csv          Top-3 Chunks je Frage und Konfiguration
  evals/retrieval_run_meta.json     Modelle, Versionen, Chunk-Zahlen, Laufzeiten
"""
import csv
import json
import platform
import statistics
import time
from datetime import datetime
from importlib.metadata import version
from pathlib import Path


from load_corpus import load_goldset
from retrieve import MODELS, count_truncated, embed_chunks, embed_query, load_chunks, search

ROOT = Path(__file__).parent
EVALS = ROOT / "evals"
KS = (1, 3, 5)
VARIANTS = ("sections", "articles", "contextual")
STALE, CURRENT = "pro-funktionen-und-preise.md", "preise-und-tarife.md"


def is_hit(question, files_in_topk):
    expected = question["quellen"]
    if question["typ"] == "mehrquellen":
        return all(f in files_in_topk for f in expected)
    return any(f in files_in_topk for f in expected)


def first_rank(results, file):
    return next((i + 1 for i, r in enumerate(results) if r["file"] == file), None)


def recall(rows, k):
    rows = [r for r in rows if r["typ"] != "luecke"]
    return (sum(r[f"hit@{k}"] for r in rows) / len(rows), len(rows)) if rows else (None, 0)


def fmt_recall(rows):
    parts = []
    for k in KS:
        value, n = recall(rows, k)
        parts.append("–" if value is None else f"{value:.2f}")
    return " / ".join(parts)


def main():
    goldset = load_goldset()
    chunks_by_variant = load_chunks()
    per_question, top3_rows, meta = [], [], {"configs": {}}

    for model_key in MODELS:
        for variant in VARIANTS:
            chunks = chunks_by_variant[variant]
            t0 = time.perf_counter()
            chunk_emb, from_cache = embed_chunks(model_key, variant, chunks)
            index_s = None if from_cache else round(time.perf_counter() - t0, 2)
            truncated, max_len, max_seq = count_truncated(model_key, [c["text"] for c in chunks])

            query_ms = []
            for q in goldset:
                t0 = time.perf_counter()
                q_emb = embed_query(model_key, q["frage"])
                query_ms.append((time.perf_counter() - t0) * 1000)
                results = search(q_emb, chunk_emb, chunks, k=len(chunks))
                top5 = results[:5]

                row = {"id": q["id"], "typ": q["typ"], "herkunft": q["herkunft"],
                       "modell": model_key, "variante": variant}
                for k in KS:
                    row[f"hit@{k}"] = int(is_hit(q, {r["file"] for r in results[:k]})) if q["quellen"] else ""
                ranks = [first_rank(results, f) for f in q["quellen"]]
                row["rang_erste_erwartete"] = min(ranks) if ranks else ""
                row["rang_alle_erwarteten"] = max(ranks) if ranks else ""
                stale, current = first_rank(results, STALE), first_rank(results, CURRENT)
                row["rang_veraltet"], row["rang_aktuell"] = stale, current
                row["veraltet_vor_aktuell"] = int(stale < current)
                row["veraltet_in_top3"] = int(stale <= 3)
                row["top1_score"] = round(top5[0]["score"], 4)
                row["top3_distinct_artikel"] = len({r["file"] for r in results[:3]})
                row["top3_woerter"] = sum(len(r["text"].split()) for r in results[:3])
                per_question.append(row)

                for rank, r in enumerate(results[:3], 1):
                    top3_rows.append({
                        "id": q["id"], "typ": q["typ"], "herkunft": q["herkunft"], "frage": q["frage"],
                        "modell": model_key, "variante": variant, "rang": rank, "chunk_id": r["id"],
                        "datei": r["file"], "score": round(r["score"], 4),
                        "erwartet": int(r["file"] in q["quellen"]),
                    })

            query_ms.sort()
            meta["configs"][f"{model_key}/{variant}"] = {
                "chunks": len(chunks),
                "abgeschnittene_chunks": truncated,
                "max_tokens_chunk": max_len,
                "max_seq_length": max_seq,
                "index_zeit_s": index_s,  # None = Embeddings aus Cache
                "query_ms_p50": round(statistics.median(query_ms), 1),
                "query_ms_p95": round(query_ms[int(0.95 * (len(query_ms) - 1))], 1),
            }
            print(f"{model_key:8} {variant:11} R@1/3/5 = {fmt_recall([r for r in per_question if r['modell'] == model_key and r['variante'] == variant])}"
                  f"  (abgeschnitten: {truncated}/{len(chunks)})")

    write_csv(EVALS / "retrieval_per_question.csv", per_question)
    write_csv(EVALS / "retrieval_top3.csv", top3_rows)
    write_report(goldset, per_question, meta)

    contexts = json.loads((ROOT / "data" / "contexts.json").read_text(encoding="utf-8")).values()
    meta.update({
        "zeitpunkt": datetime.now().isoformat(timespec="seconds"),
        "modelle": {k: v["name"] for k, v in MODELS.items()},
        "kontext_modell": "claude-haiku-4-5",
        "kontext_kosten_usd": round(sum(c["input_tokens"] for c in contexts) / 1e6 * 1.0
                                    + sum(c["output_tokens"] for c in contexts) / 1e6 * 5.0, 4),
        "versionen": {p: version(p) for p in ("sentence-transformers", "torch", "anthropic", "numpy")},
        "python": platform.python_version(),
        "goldset_fragen": len(goldset),
    })
    (EVALS / "retrieval_run_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(goldset, per_question, meta):
    configs = [(m, v) for m in MODELS for v in VARIANTS]
    sel = lambda m, v, **f: [r for r in per_question if r["modell"] == m and r["variante"] == v
                             and all(r[key] == val for key, val in f.items())]
    n_scored = sum(1 for q in goldset if q["typ"] != "luecke")
    lines = [
        "# Retrieval-Eval",
        "",
        f"Stand: {datetime.now():%Y-%m-%d %H:%M} · {len(goldset)} Fragen, davon {n_scored} mit Quelle "
        f"(luecke nicht im Recall) · Werte: Recall@1 / @3 / @5 über **Chunks**",
        "",
        "Scoring-Regel: `mehrquellen` braucht alle erwarteten Quellen in den Top-k Chunks, alle anderen Typen eine. "
        "Recall@1 ist für `mehrquellen` daher strukturell 0 (ein Chunk gehört zu genau einem Artikel).",
        "",
        "**Kleine Stichprobe:** Eine Frage entspricht 0,04 im Gesamt-Recall (n=23) und 0,25–0,33 in den Typ-Spalten. "
        "Die Variante `articles` hat nur 20 Chunks, Top-5 sind dort bereits 25 % des Korpus.",
        "",
        "## Gesamt",
        "",
        "| Modell | Variante | R@1 / R@3 / R@5 | Ø Artikel in Top-3 | Ø Wörter in Top-3 | abgeschnittene Chunks | Query p95 (ms) |",
        "|---|---|---|---|---|---|---|",
    ]
    for m, v in configs:
        rows = sel(m, v)
        c = meta["configs"][f"{m}/{v}"]
        lines.append(f"| {m} | {v} | {fmt_recall(rows)} | "
                     f"{statistics.mean(r['top3_distinct_artikel'] for r in rows):.1f} | "
                     f"{statistics.mean(r['top3_woerter'] for r in rows):.0f} | "
                     f"{c['abgeschnittene_chunks']}/{c['chunks']} (max {c['max_tokens_chunk']} / {c['max_seq_length']} Tokens) | "
                     f"{c['query_ms_p95']} |")

    for field in ("typ", "herkunft"):
        values = sorted({q[field] for q in goldset if q["typ"] != "luecke"})
        counts = {val: sum(1 for q in goldset if q[field] == val and q["typ"] != "luecke") for val in values}
        lines += ["", f"## Nach {field}", "",
                  "| Modell | Variante | " + " | ".join(f"{val} (n={counts[val]})" for val in values) + " |",
                  "|---|---|" + "---|" * len(values)]
        for m, v in configs:
            lines.append(f"| {m} | {v} | " + " | ".join(fmt_recall(sel(m, v, **{field: val})) for val in values) + " |")

    lines += ["", "## Veraltete Preisseite", "",
              f"Rang des ersten Chunks von `{STALE}` (2024) vs. `{CURRENT}` (2026). "
              "Spalte „veraltet in Top-3“ zählt über alle 27 Fragen.", "",
              "| Modell | Variante | " + " | ".join(f"#{q['id']}" for q in goldset if q["typ"] == "veraltet")
              + " | veraltet vor aktuell (veraltet-Fragen) | veraltet in Top-3 (alle Fragen) |",
              "|---|---|" + "---|" * (sum(q["typ"] == "veraltet" for q in goldset) + 2)]
    for m, v in configs:
        stale_rows = sel(m, v, typ="veraltet")
        cells = [f"{r['rang_veraltet']} vs {r['rang_aktuell']}" for r in stale_rows]
        in_top3 = [r["id"] for r in sel(m, v) if r["veraltet_in_top3"]]
        lines.append(f"| {m} | {v} | " + " | ".join(cells)
                     + f" | {sum(r['veraltet_vor_aktuell'] for r in stale_rows)}/{len(stale_rows)}"
                     + f" | {len(in_top3)} ({', '.join('#' + i for i in in_top3)}) |")

    lines += ["", "## Lücken-Fragen: Top-1-Ähnlichkeit", "",
              "Lässt sich „keine passende Quelle“ an einer niedrigen Top-1-Ähnlichkeit erkennen?", "",
              "| Modell | Variante | luecke Ø (min–max) | mit Quelle Ø (min–max) |", "|---|---|---|---|"]
    for m, v in configs:
        gap = [r["top1_score"] for r in sel(m, v, typ="luecke")]
        rest = [r["top1_score"] for r in sel(m, v) if r["typ"] != "luecke"]
        lines.append(f"| {m} | {v} | {statistics.mean(gap):.3f} ({min(gap):.3f}–{max(gap):.3f}) | "
                     f"{statistics.mean(rest):.3f} ({min(rest):.3f}–{max(rest):.3f}) |")

    lines += ["", "## Verfehlt bei Recall@3", "",
              "| Modell | Variante | Fragen (Rang aller erwarteten Quellen) |", "|---|---|---|"]
    for m, v in configs:
        missed = [f"#{r['id']} ({r['typ']}, Rang {r['rang_alle_erwarteten']})"
                  for r in sel(m, v) if r["typ"] != "luecke" and not r["hit@3"]]
        lines.append(f"| {m} | {v} | {', '.join(missed) or '–'} |")

    (EVALS / "retrieval_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
