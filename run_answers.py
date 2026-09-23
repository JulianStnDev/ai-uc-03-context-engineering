"""Antwortstufe: beantwortet jede Goldset-Frage in vier Varianten mit Haiku 4.5.

  sections    – Top-4 Abschnitte (bge-m3)
  contextual  – Top-4 Abschnitte mit Kontextsatz (bge-m3)
  articles    – Top-3 ganze Artikel (bge-m3)
  corpus      – alle 20 Artikel im Kontext, per Prompt Caching gecacht

Alle Varianten eines Laufs nutzen denselben System-Prompt und dasselbe Kontextformat,
in dem Dateiname, Titel und Datum jeder Quelle sichtbar sind. Ergebnisse werden Zeile
für Zeile an data/answers[_<lauf>].jsonl angehängt; bereits beantwortete
(Frage, Variante)-Paare werden beim erneuten Start übersprungen.

Aufruf: python run_answers.py [v1|v2]   (Standard: v1)
  v1 – erster Lauf, alle vier Varianten
  v2 – geschärfter Prompt, nur articles und corpus
"""
import json
import re
import sys
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from load_corpus import load_articles, load_goldset
from retrieve import embed_chunks, embed_query, load_chunks, search

ROOT = Path(__file__).parent

ANSWER_MODEL = "claude-haiku-4-5"
EMBED_MODEL = "bge-m3"
VARIANTS = {"sections": 4, "contextual": 4, "articles": 3, "corpus": None}

SYSTEM_PROMPT_V1 = """Du bist der Support-Assistent von FocusFlow, einer Habit-Tracker-App. Du beantwortest Kundenfragen ausschließlich anhand der Hilfeartikel im Block <kontext>.

Regeln:
- Verwende nur Informationen aus dem Kontext. Kein Vorwissen, keine Vermutungen.
- Wenn der Kontext die Frage nicht beantwortet, sag das offen und verweise an den Support (in der App unter Einstellungen > Hilfe > Kontakt). Gib in diesem Fall keine inhaltliche Antwort.
- Widersprechen sich Quellen, gilt die Quelle mit dem neueren Datum (Attribut "aktualisiert").
- Antworte auf Deutsch, kurz und freundlich, in der Du-Form.
- Schließe deine Antwort immer mit einer eigenen letzten Zeile ab: "Quellen: " gefolgt von den Dateinamen der Artikel, auf die du dich stützt, getrennt durch Semikolon. Wenn du dich auf keinen Artikel stützt: "Quellen: keine"."""

SYSTEM_PROMPT_V2 = """Du bist der Support-Assistent von FocusFlow, einer Habit-Tracker-App. Du beantwortest Kundenfragen ausschließlich anhand der Hilfeartikel im Block <kontext>.

Regeln:
- Antworte knapp: nur das, was zur Beantwortung der Frage nötig ist.
- Triff keine Aussage, die nicht im Kontext steht – auch keine naheliegenden Folgerungen, Vermutungen, Beispiele oder Erklärungen, die über den Text hinausgehen.
- Wenn der Kontext die Frage nicht beantwortet, sag das offen und verweise an den Support (in der App unter Einstellungen > Hilfe > Kontakt). Gib in diesem Fall keine inhaltliche Antwort.
- Widersprechen sich Quellen, nenne die Angaben der Quelle mit dem neueren Datum (Attribut "aktualisiert") und kennzeichne die ältere Quelle ausdrücklich als veraltet.
- Sachlicher Support-Ton, auf Deutsch, in der Du-Form. Keine Emojis, keine Floskeln wie "Ich verstehe deine Frustration" oder "Gute Frage".
- Schließe deine Antwort immer mit einer eigenen letzten Zeile ab: "Quellen: " gefolgt von den Dateinamen der Artikel, auf die du dich stützt, getrennt durch Semikolon. Wenn du dich auf keinen Artikel stützt: "Quellen: keine"."""

RUNS = {
    "v1": {"prompt": SYSTEM_PROMPT_V1, "variants": ("sections", "contextual", "articles", "corpus")},
    "v2": {"prompt": SYSTEM_PROMPT_V2, "variants": ("articles", "corpus")},
}


def answers_path(run):
    return ROOT / "data" / ("answers.jsonl" if run == "v1" else f"answers_{run}.jsonl")


def format_source(file, title, date, text):
    return f'<quelle datei="{file}" titel="{title}" aktualisiert="{date}">\n{text}\n</quelle>'


def build_context(variant, question, articles, chunks, chunk_emb):
    """Gibt (Kontext-String, Liste der Dateien im Kontext, Retrieval-Zeit in s) zurück."""
    if variant == "corpus":
        sources = [format_source(a["file"], a["title"], a["date"], a["text"]) for a in articles]
        return "\n\n".join(sources), [a["file"] for a in articles], 0.0
    t0 = time.perf_counter()
    hits = search(embed_query(EMBED_MODEL, question), chunk_emb, chunks, k=VARIANTS[variant])
    retrieval_s = time.perf_counter() - t0
    sources = [format_source(h["file"], h["title"], h["date"], h["text"]) for h in hits]
    return "\n\n".join(sources), [h["file"] for h in hits], retrieval_s


def parse_cited(answer):
    """Liest die Dateinamen aus der letzten "Quellen:"-Zeile."""
    lines = [l for l in answer.strip().splitlines() if l.strip().lower().startswith("quellen:")]
    if not lines:
        return [], False
    cited = re.findall(r"[\w\-]+\.md", lines[-1])
    return [f for f in dict.fromkeys(cited)], True


def main(run):
    cfg = RUNS[run]
    out_path = answers_path(run)
    load_dotenv(ROOT / ".env")
    client = anthropic.Anthropic()
    articles = load_articles()
    goldset = load_goldset()
    chunks_by_variant = load_chunks()
    embeddings = {v: embed_chunks(EMBED_MODEL, v, chunks_by_variant[v])[0] for v in ("sections", "contextual", "articles")}

    done = set()
    if out_path.exists():
        done = {(r["id"], r["variante"]) for r in map(json.loads, out_path.open(encoding="utf-8"))}

    # Warm-up, damit das Laden von bge-m3 nicht in die Latenz der ersten Frage fällt.
    embed_query(EMBED_MODEL, "Warm-up")

    with out_path.open("a", encoding="utf-8") as out:
        # Varianten außen, Fragen innen: Die corpus-Aufrufe laufen direkt
        # hintereinander, damit der 5-Minuten-Cache warm bleibt.
        for variant in cfg["variants"]:
            for q in goldset:
                if (q["id"], variant) in done:
                    continue
                context, context_files, retrieval_s = build_context(
                    variant, q["frage"], articles,
                    chunks_by_variant.get(variant), embeddings.get(variant))

                context_block = {"type": "text", "text": f"<kontext>\n{context}\n</kontext>"}
                if variant == "corpus":
                    context_block["cache_control"] = {"type": "ephemeral"}

                t0 = time.perf_counter()
                response = client.messages.create(
                    model=ANSWER_MODEL,
                    max_tokens=1024,
                    temperature=0,
                    system=cfg["prompt"],
                    messages=[{"role": "user", "content": [
                        context_block,
                        {"type": "text", "text": f"<frage>\n{q['frage']}\n</frage>"},
                    ]}],
                )
                llm_s = time.perf_counter() - t0

                answer = "".join(b.text for b in response.content if b.type == "text").strip()
                cited, has_sources_line = parse_cited(answer)
                u = response.usage
                row = {
                    "lauf": run, "id": q["id"], "variante": variant, "frage": q["frage"], "antwort": answer,
                    "zitiert": cited, "quellenzeile_gefunden": has_sources_line,
                    "kontext_dateien": context_files, "kontext": context,
                    "stop_reason": response.stop_reason,
                    "input_tokens": u.input_tokens,
                    "cache_write_tokens": u.cache_creation_input_tokens or 0,
                    "cache_read_tokens": u.cache_read_input_tokens or 0,
                    "output_tokens": u.output_tokens,
                    "retrieval_s": round(retrieval_s, 4), "llm_s": round(llm_s, 3),
                    "gesamt_s": round(retrieval_s + llm_s, 3),
                }
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
                out.flush()
                print(f"{variant:10} #{q['id']:>2}  {llm_s:5.2f}s  in={u.input_tokens} "
                      f"cw={row['cache_write_tokens']} cr={row['cache_read_tokens']} out={u.output_tokens}  zitiert={cited}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
