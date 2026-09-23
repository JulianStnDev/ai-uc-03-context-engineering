"""Auswertung der Antwortstufe: verbindet Antworten, Judge-Urteile und Goldset.

Spalten je Antwort:
  quellen_ok      automatisch nach Scoring-Regel (mehrquellen: alle, sonst eine
                  erwartete Quelle zitiert). Bei veraltet ist ein Zitat der alten
                  Preisseite nur ok, wenn der Judge veraltet_gekennzeichnet = true
                  vergibt (Regel seit 2026-09-23, siehe docs/decisions.md).
                  Bei luecke: ok, wenn nichts zitiert wurde.
  veraltet_gekennzeichnet  Judge, nur bei Zitat der alten Preisseite
  kernaussage_ok  Judge, nur bei typ != luecke
  treu            Judge (Faithfulness gegen den mitgegebenen Kontext)
  luecke_ok       Judge, nur bei typ == luecke
  alles_ok        alle zutreffenden Spalten ok

Ausgaben (Suffix _v2 usw. für spätere Läufe):
  evals/answers.csv           eine Zeile je (Frage, Variante) inkl. Antwort und Begründungen
  evals/answer_results.md     Tabellen nach Variante × typ × herkunft, Kosten, Latenz;
                              ab v2 zusätzlich Vergleich mit v1
  evals/answer_run_meta.json  Modelle, Preise, Token-Summen
  evals/judge_stichprobe.md   nur v1: 10 zufällige Judge-Urteile zur manuellen Prüfung,
                              Julians Urteile kommen aus evals/judge_kalibrierung.csv

Aufruf: python score_answers.py [v1|v2]   (Standard: v1)
"""
import csv
import json
import random
import statistics
import sys
from datetime import datetime
from pathlib import Path

from load_corpus import load_goldset

ROOT = Path(__file__).parent
EVALS = ROOT / "evals"
VARIANT_ORDER = ("sections", "contextual", "articles", "corpus")
VARIANTS = VARIANT_ORDER  # wird in main() auf die Varianten des Laufs gesetzt
STALE = "pro-funktionen-und-preise.md"

# USD pro 1M Tokens
HAIKU = {"in": 1.00, "cache_write": 1.25, "cache_read": 0.10, "out": 5.00}
SONNET = {"in": 2.00, "cache_write": 2.50, "cache_read": 0.20, "out": 10.00}

SAMPLE_SEED, SAMPLE_SIZE = 42, 10
CALIBRATION_PATH = EVALS / "judge_kalibrierung.csv"

VARIANT_LABELS = {
    "sections": "`sections` Top-4 Abschnitte",
    "contextual": "`contextual` Top-4 Abschnitte mit Kontextsatz",
    "articles": "`articles` Top-3 ganze Artikel",
    "corpus": "`corpus` alle 20 Artikel (Prompt Caching)",
}


def load_jsonl(path):
    return [json.loads(l) for l in path.open(encoding="utf-8")] if path.exists() else []


def data_path(name, run):
    return ROOT / "data" / (f"{name}.jsonl" if run == "v1" else f"{name}_{run}.jsonl")


def eval_path(name, ext, run):
    return EVALS / (f"{name}.{ext}" if run == "v1" else f"{name}_{run}.{ext}")


def quellen_ok(question, cited, stale_marked):
    expected = question["quellen"]
    if question["typ"] == "luecke":
        return not cited
    if question["typ"] == "veraltet" and STALE in cited and not stale_marked:
        return False
    if question["typ"] == "mehrquellen":
        return all(f in cited for f in expected)
    return any(f in cited for f in expected)


def answer_cost(r):
    """Kosten eines Haiku-Aufrufs, aufgeteilt nach Token-Art (USD)."""
    return {
        "in": r["input_tokens"] / 1e6 * HAIKU["in"],
        "cache_write": r["cache_write_tokens"] / 1e6 * HAIKU["cache_write"],
        "cache_read": r["cache_read_tokens"] / 1e6 * HAIKU["cache_read"],
        "out": r["output_tokens"] / 1e6 * HAIKU["out"],
    }


def build_rows(run):
    questions = {q["id"]: q for q in load_goldset()}
    judgments = {(j["id"], j["variante"]): j for j in load_jsonl(data_path("judgments", run))}
    stale = {(j["id"], j["variante"]): j for j in load_jsonl(data_path("stale_judgments", run))}
    rows = []
    for a in load_jsonl(data_path("answers", run)):
        q = questions[a["id"]]
        j = judgments[(a["id"], a["variante"])]
        sj = stale.get((a["id"], a["variante"]))
        if STALE in a["zitiert"] and sj is None:
            raise RuntimeError(f"#{a['id']} {a['variante']}: Zitat der alten Seite, aber kein veraltet-Urteil")
        is_gap = q["typ"] == "luecke"
        row = {
            "id": a["id"], "typ": q["typ"], "herkunft": q["herkunft"], "variante": a["variante"],
            "frage": q["frage"], "kernaussage": q["kernaussage"], "erwartete_quellen": q["erwartete_quellen"],
            "antwort": a["antwort"], "zitiert": "; ".join(a["zitiert"]) or "keine",
            "kontext_dateien": "; ".join(dict.fromkeys(a["kontext_dateien"])) if a["variante"] != "corpus" else "alle",
            "quellen_ok": int(quellen_ok(q, a["zitiert"], bool(sj and sj["veraltet_gekennzeichnet"]))),
            "kernaussage_ok": "" if is_gap else int(j["kernaussage_ok"]),
            "treu": int(j["treu"]),
            "luecke_ok": int(j["luecke_ok"]) if is_gap else "",
            "kernaussage_begruendung": "" if is_gap else j["kernaussage_ok_begruendung"],
            "treu_begruendung": j["treu_begruendung"],
            "luecke_begruendung": j["luecke_ok_begruendung"] if is_gap else "",
            "zitiert_veraltet": int(STALE in a["zitiert"]),
            "veraltet_gekennzeichnet": int(sj["veraltet_gekennzeichnet"]) if sj else "",
            "veraltet_begruendung": sj["veraltet_gekennzeichnet_begruendung"] if sj else "",
            **{f"kosten_{k}_usd": round(v, 7) for k, v in answer_cost(a).items()},
            "input_tokens": a["input_tokens"], "cache_write_tokens": a["cache_write_tokens"],
            "cache_read_tokens": a["cache_read_tokens"], "output_tokens": a["output_tokens"],
            "retrieval_s": a["retrieval_s"], "llm_s": a["llm_s"], "gesamt_s": a["gesamt_s"],
            "_judge": j, "_stale_judge": sj,
        }
        checks = [row["quellen_ok"], row["treu"]] + ([row["luecke_ok"]] if is_gap else [row["kernaussage_ok"]])
        row["alles_ok"] = int(all(checks))
        rows.append(row)
    return rows


def rate(rows, col):
    vals = [r[col] for r in rows if r[col] != ""]
    return f"{sum(vals)}/{len(vals)}" if vals else "–"


def pct(rows, col):
    vals = [r[col] for r in rows if r[col] != ""]
    return f"{sum(vals) / len(vals):.0%}" if vals else "–"


def percentile(values, p):
    values = sorted(values)
    return values[round(p * (len(values) - 1))]


RUN_TITLES = {
    "v1": "Lauf v1 – erster Antwort-Prompt",
    "v2": "Lauf v2 – geschärfter Antwort-Prompt (knapp, keine Folgerungen/Beispiele, sachlicher Ton, "
          "ältere Quelle als veraltet kennzeichnen)",
}


def write_report(rows, run, v1_rows=None):
    by = lambda **f: [r for r in rows if all(r[k] == v for k, v in f.items())]
    cols = ("quellen_ok", "kernaussage_ok", "treu", "luecke_ok", "alles_ok")
    typs = sorted({r["typ"] for r in rows})
    herkuenfte = sorted({r["herkunft"] for r in rows})
    n_q = len({r["id"] for r in rows})

    lines = [
        f"# Antwort-Eval: {RUN_TITLES[run]}",
        "",
        f"Stand: {datetime.now():%Y-%m-%d %H:%M} · {n_q} Fragen × {len(VARIANTS)} Varianten · "
        "Antwortmodell `claude-haiku-4-5`, Judge `claude-sonnet-5`, Retrieval `bge-m3`",
        "",
        "Varianten: " + " · ".join(VARIANT_LABELS[v] for v in VARIANTS),
        "",
        "Spalten: `quellen_ok` automatisch (Scoring-Regel; bei veraltet ist ein Zitat der alten Preisseite nur ok, wenn "
        "der Judge sie als ausdrücklich veraltet gekennzeichnet bewertet (`veraltet_gekennzeichnet`); "
        "bei luecke ok, wenn nichts zitiert) · `kernaussage_ok` Judge, ohne luecke · `treu` Judge, Faithfulness gegen den "
        "mitgegebenen Kontext · `luecke_ok` Judge, nur luecke · `alles_ok` alle zutreffenden Spalten ok",
        "",
        "**Ein Lauf, kleine Stichprobe:** Eine Frage entspricht 4 Prozentpunkten (n=27), in den Typ-Spalten 20–33. "
        "Judge-Kalibrierung: `judge_stichprobe.md` und `docs/decisions.md`.",
        "",
        "## Gesamt",
        "",
        "| Variante | quellen_ok | kernaussage_ok | treu | luecke_ok | **alles_ok** |",
        "|---|---|---|---|---|---|",
    ]
    for v in VARIANTS:
        rs = by(variante=v)
        lines.append(f"| {v} | " + " | ".join(f"{rate(rs, c)} ({pct(rs, c)})" for c in cols[:-1])
                     + f" | **{rate(rs, 'alles_ok')} ({pct(rs, 'alles_ok')})** |")

    for field, values in (("typ", typs), ("herkunft", herkuenfte)):
        for col in ("alles_ok", "kernaussage_ok", "quellen_ok", "treu"):
            shown = [val for val in values if any(r[col] != "" for r in by(**{field: val}))]
            n = {val: len({r["id"] for r in by(**{field: val})}) for val in shown}
            lines += ["", f"## {col} nach {field}", "",
                      "| Variante | " + " | ".join(f"{val} (n={n[val]})" for val in shown) + " |",
                      "|---|" + "---|" * len(shown)]
            for v in VARIANTS:
                lines.append(f"| {v} | " + " | ".join(rate(by(variante=v, **{field: val}), col) for val in shown) + " |")

    lines += ["", "## Veraltete Preisseite", "",
              "| Variante | zitiert alte Seite (alle Fragen) | davon als veraltet gekennzeichnet | veraltet-Fragen: quellen_ok | veraltet-Fragen: kernaussage_ok |",
              "|---|---|---|---|---|"]
    for v in VARIANTS:
        cited = [f"#{r['id']}" for r in by(variante=v) if r["zitiert_veraltet"]]
        marked = [f"#{r['id']}" for r in by(variante=v) if r["veraltet_gekennzeichnet"] == 1]
        lines.append(f"| {v} | {len(cited)} ({', '.join(cited) or '–'}) | {len(marked)} ({', '.join(marked) or '–'}) | "
                     f"{rate(by(variante=v, typ='veraltet'), 'quellen_ok')} | {rate(by(variante=v, typ='veraltet'), 'kernaussage_ok')} |")

    lines += ["", "## Kosten pro 1000 Anfragen (Haiku 4.5, gemessen aus `usage`)", "",
              "Preise: Input 1,00 · Cache-Write 1,25 · Cache-Read 0,10 · Output 5,00 USD pro 1M Tokens. "
              "Retrieval-Embeddings laufen lokal und kosten nichts.", "",
              "| Variante | Ø Input-Tokens | davon Cache-Read | Ø Output-Tokens | Input | Cache-Write | Cache-Read | Output | **Summe / 1000** |",
              "|---|---|---|---|---|---|---|---|---|"]
    for v in VARIANTS:
        rs = by(variante=v)
        mean = lambda k: statistics.mean(r[k] for r in rs)
        parts = {k: mean(f"kosten_{k}_usd") * 1000 for k in ("in", "cache_write", "cache_read", "out")}
        total_in = mean("input_tokens") + mean("cache_write_tokens") + mean("cache_read_tokens")
        lines.append(f"| {v} | {total_in:,.0f} | {mean('cache_read_tokens'):,.0f} | {mean('output_tokens'):,.0f} | "
                     + " | ".join(f"{parts[k]:.2f}" for k in ("in", "cache_write", "cache_read", "out"))
                     + f" | **{sum(parts.values()):.2f} USD** |")
    corpus = by(variante="corpus")
    prefix = statistics.mean(r["cache_write_tokens"] + r["cache_read_tokens"] for r in corpus)
    rest_in = statistics.mean(r["input_tokens"] for r in corpus)
    out_cost = statistics.mean(r["kosten_out_usd"] for r in corpus) * 1000
    no_cache = (prefix + rest_in) / 1e6 * HAIKU["in"] * 1000 + out_cost
    all_reads = (prefix / 1e6 * HAIKU["cache_read"] + rest_in / 1e6 * HAIKU["in"]) * 1000 + out_cost
    lines += ["",
              f"Einordnung `corpus`: Im Lauf kam auf 27 Anfragen ein Cache-Write. Ohne Caching wären es **{no_cache:.2f} USD** "
              f"pro 1000 Anfragen, bei durchgehend warmem Cache (nur Reads) **{all_reads:.2f} USD**. "
              "Der Cache hält 5 Minuten; bei weniger Traffic fallen mehr Writes an."]

    lines += ["", "## Latenz (Sekunden, lokales Retrieval + Haiku-Aufruf)", "",
              "| Variante | Median | p95 | davon Retrieval Median |", "|---|---|---|---|"]
    for v in VARIANTS:
        rs = by(variante=v)
        lines.append(f"| {v} | {statistics.median(r['gesamt_s'] for r in rs):.2f} | "
                     f"{percentile([r['gesamt_s'] for r in rs], 0.95):.2f} | "
                     f"{statistics.median(r['retrieval_s'] for r in rs) * 1000:.0f} ms |")
    lines += ["", "p95 aus 27 Messungen je Variante ist nur grob belastbar."]

    lines += ["", "## Nicht alles_ok", "", "| Variante | Fragen (fehlgeschlagene Spalten) |", "|---|---|"]
    for v in VARIANTS:
        fails = []
        for r in by(variante=v):
            bad = [c for c in cols[:-1] if r[c] == 0]
            if bad:
                fails.append(f"#{r['id']} ({', '.join(bad)})")
        lines.append(f"| {v} | {', '.join(fails) or '–'} |")

    if v1_rows:
        lines += compare_section(rows, v1_rows)
    eval_path("answer_results", "md", run).write_text("\n".join(lines) + "\n", encoding="utf-8")


def summarize(rows):
    """Kennzahlen einer Variante: Raten je Kriterium, Kosten/1000, Latenz, Output-Tokens."""
    out = {c: (sum(r[c] for r in rows if r[c] != ""), sum(1 for r in rows if r[c] != ""))
           for c in ("quellen_ok", "kernaussage_ok", "treu", "luecke_ok", "alles_ok")}
    out["kosten"] = statistics.mean(sum(r[f"kosten_{k}_usd"] for k in ("in", "cache_write", "cache_read", "out"))
                                    for r in rows) * 1000
    out["median_s"] = statistics.median(r["gesamt_s"] for r in rows)
    out["p95_s"] = percentile([r["gesamt_s"] for r in rows], 0.95)
    out["output_tokens"] = statistics.mean(r["output_tokens"] for r in rows)
    out["woerter"] = statistics.mean(len(r["antwort"].split()) for r in rows)
    return out


def compare_section(rows, v1_rows):
    lines = ["", "## Vergleich v1 → v2", "",
             "Gleiche Fragen, gleiches Modell, gleicher Kontext, gleicher Judge – nur der Antwort-Prompt ist anders. "
             "v1-Werte nach der angepassten `quellen_ok`-Regel.", "",
             "| Variante | Lauf | quellen_ok | kernaussage_ok | treu | luecke_ok | **alles_ok** | Kosten / 1000 | Median | p95 | Ø Output-Tokens | Ø Wörter |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for v in VARIANTS:
        for label, rs in (("v1", [r for r in v1_rows if r["variante"] == v]), ("v2", [r for r in rows if r["variante"] == v])):
            s = summarize(rs)
            cell = lambda c: f"{s[c][0]}/{s[c][1]}"
            lines.append(f"| {v} | {label} | {cell('quellen_ok')} | {cell('kernaussage_ok')} | {cell('treu')} | "
                         f"{cell('luecke_ok')} | **{cell('alles_ok')}** | {s['kosten']:.2f} USD | {s['median_s']:.2f} s | "
                         f"{s['p95_s']:.2f} s | {s['output_tokens']:.0f} | {s['woerter']:.0f} |")

    lines += ["", "### Änderungen je Frage (v1 → v2)", "",
              "| Variante | Frage | Typ | Kriterium | v1 | v2 |", "|---|---|---|---|---|---|"]
    v1_by = {(r["id"], r["variante"]): r for r in v1_rows}
    changes = 0
    for r in rows:
        old = v1_by[(r["id"], r["variante"])]
        for c in ("quellen_ok", "kernaussage_ok", "treu", "luecke_ok"):
            if r[c] != "" and r[c] != old[c]:
                changes += 1
                lines.append(f"| {r['variante']} | #{r['id']} | {r['typ']} | {c} | {'✅' if old[c] else '❌'} | {'✅' if r[c] else '❌'} |")
    if not changes:
        lines.append("| – | – | – | – | – | – |")
    return lines


def write_sample(rows):
    """10 Judge-Urteile, zufällig (fester Seed), gestreut über Varianten, Typen und Kriterien."""
    verdicts = []
    for r in rows:
        crits = ["luecke_ok", "treu"] if r["typ"] == "luecke" else ["kernaussage_ok", "treu"]
        verdicts += [(r, c) for c in crits]
    rng = random.Random(SAMPLE_SEED)
    rng.shuffle(verdicts)

    picked, seen_answers = [], set()
    count = lambda key, val: sum(1 for p in picked if key(p) == val)
    for r, crit in verdicts:
        if len(picked) == SAMPLE_SIZE:
            break
        if ((r["id"], r["variante"]) in seen_answers or count(lambda p: p[0]["variante"], r["variante"]) >= 3
                or count(lambda p: p[0]["typ"], r["typ"]) >= 3 or count(lambda p: p[1], crit) >= 5):
            continue
        picked.append((r, crit))
        seen_answers.add((r["id"], r["variante"]))

    calibration = {}
    if CALIBRATION_PATH.exists():
        for c in csv.DictReader(CALIBRATION_PATH.open(encoding="utf-8")):
            calibration[int(c["nr"])] = c
    for i, (r, crit) in enumerate(picked, 1):
        c = calibration.get(i)
        if c and (c["id"], c["variante"], c["kriterium"]) != (r["id"], r["variante"], crit):
            raise RuntimeError(f"Kalibrierung Nr {i} passt nicht zur Stichprobe: {c} vs #{r['id']} {r['variante']} {crit}")
    agree = lambda i: calibration[i]["julian_stimmt_zu"] if i in calibration else ""
    comment = lambda i: calibration[i].get("kommentar", "") if i in calibration else ""

    reason_key = {"kernaussage_ok": "kernaussage_begruendung", "treu": "treu_begruendung", "luecke_ok": "luecke_begruendung"}
    lines = [
        "# Judge-Stichprobe zur Kalibrierung",
        "",
        f"{SAMPLE_SIZE} zufällig gezogene Urteile von `claude-sonnet-5` (Seed {SAMPLE_SEED}, gestreut über Varianten, "
        "Typen und Kriterien).",
        "",
        "**Aufgabe:** Je Urteil eintragen, ob du dem **Urteil des Judges** zustimmst – nicht, ob die Antwort gut ist. "
        "Beispiel: Judge sagt `kernaussage_ok: ❌ nein` und du findest die Kernaussage auch verfehlt → „ja“.",
        "",
        "Bei `treu` prüft der Judge, ob jede Behauptung durch den Kontext gedeckt ist, den das Antwortmodell gesehen hat. "
        "Die Kontext-Dateien stehen dabei; der volle Kontext steht in `data/answers.jsonl`.",
        "",
        "| Nr | Frage | Variante | Typ | Kriterium | Urteil des Judges | Julian stimmt dem Judge zu? ja/nein | Kommentar |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i, (r, crit) in enumerate(picked, 1):
        lines.append(f"| {i} | #{r['id']} | {r['variante']} | {r['typ']} | {crit} | {'✅ ja' if r[crit] else '❌ nein'} | "
                     f"{agree(i)} | {comment(i)} |")
    if len(calibration) == len(picked):
        yes = sum(agree(i) == "ja" for i in range(1, len(picked) + 1))
        lines += ["", f"**Ergebnis:** Julian stimmt {yes} von {len(picked)} Judge-Urteilen zu "
                      f"(Quelle: `evals/judge_kalibrierung.csv`, Bewertung in `docs/decisions.md`)."]

    for i, (r, crit) in enumerate(picked, 1):
        quote = lambda text: "\n".join("> " + l if l else ">" for l in text.splitlines())
        lines += [
            "", "---", "",
            f"## {i}. Frage #{r['id']} · {r['variante']} · {r['typ']} · Kriterium `{crit}`",
            "",
            f"**Frage:** {r['frage']}",
            "",
            "**Antwort (Haiku 4.5):**",
            "",
            quote(r["antwort"]),
            "",
            f"**Kernaussage (Goldset):** {r['kernaussage']}",
            "",
            f"**Kontext-Dateien:** {r['kontext_dateien']}",
            "",
            f"**Urteil des Judges `{crit}`:** {'✅ ja' if r[crit] else '❌ nein'}",
            "",
            f"**Begründung:** {r[reason_key[crit]]}",
            "",
            f"**Julian stimmt dem Urteil des Judges zu? (ja/nein):** {agree(i)}"
            + (f" – {comment(i)}" if comment(i) else ""),
        ]
    (EVALS / "judge_stichprobe.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_meta(rows, run):
    judgments = [r["_judge"] for r in rows] + [r["_stale_judge"] for r in rows if r["_stale_judge"]]
    judge_cost = sum(j["judge_input_tokens"] / 1e6 * SONNET["in"]
                     + j["judge_cache_write_tokens"] / 1e6 * SONNET["cache_write"]
                     + j["judge_cache_read_tokens"] / 1e6 * SONNET["cache_read"]
                     + j["judge_output_tokens"] / 1e6 * SONNET["out"] for j in judgments)
    answer_cost_total = sum(sum(answer_cost({k: r[k] for k in ("input_tokens", "cache_write_tokens",
                                                                "cache_read_tokens", "output_tokens")}).values()) for r in rows)
    meta = {
        "lauf": run,
        "zeitpunkt": datetime.now().isoformat(timespec="seconds"),
        "antwortmodell": "claude-haiku-4-5", "judge": "claude-sonnet-5", "embedding": "BAAI/bge-m3",
        "varianten": list(VARIANTS),
        "top_k": {"sections": 4, "contextual": 4, "articles": 3, "corpus": "alle"},
        "preise_usd_pro_mtok": {"haiku": HAIKU, "sonnet": SONNET},
        "antworten": len(rows),
        "kosten_antworten_usd": round(answer_cost_total, 4),
        "kosten_judge_usd": round(judge_cost, 4),  # inkl. veraltet_gekennzeichnet-Durchgang
        "judge_aufrufe": len(judgments),
        "judge_output_tokens_summe": sum(j["judge_output_tokens"] for j in judgments),
        "judge_latenz_median_s": round(statistics.median(j["judge_s"] for j in judgments), 2),
    }
    if run == "v1":
        meta["stichprobe_seed"] = SAMPLE_SEED
    eval_path("answer_run_meta", "json", run).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def main(run):
    global VARIANTS
    rows = build_rows(run)
    VARIANTS = tuple(v for v in VARIANT_ORDER if any(r["variante"] == v for r in rows))
    with eval_path("answers", "csv", run).open("w", encoding="utf-8", newline="") as f:
        fields = [k for k in rows[0] if not k.startswith("_")]
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    v1_rows = None
    if run != "v1":
        v1_rows = [r for r in build_rows("v1") if r["variante"] in VARIANTS]
    write_report(rows, run, v1_rows)
    if run == "v1":
        write_sample(rows)
    meta = write_meta(rows, run)
    print(f"{len(rows)} Antworten ausgewertet · Antworten {meta['kosten_antworten_usd']} USD · Judge {meta['kosten_judge_usd']} USD")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
