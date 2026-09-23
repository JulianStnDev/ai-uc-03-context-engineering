"""Erzeugt die drei Chunk-Varianten fürs Retrieval und schreibt data/chunks.json.

  sections    – ein Chunk pro "## "-Abschnitt, ohne Artikeltitel und Datum (Baseline)
  articles    – ein Chunk pro Artikel, kompletter Text inkl. Titel und Datum
  contextual  – Abschnitte wie bei "sections", davor ein von Claude erzeugter
                Kontext-Satz zum Gesamtartikel (Anthropic "Contextual Retrieval")

Die Kontext-Sätze kosten API-Aufrufe und werden deshalb in data/contexts.json
gecacht. Ein erneuter Lauf ruft nur für neue oder geänderte Abschnitte die API auf.
"""
import hashlib
import json
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from load_corpus import load_articles

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
CHUNKS_PATH = DATA_DIR / "chunks.json"
CONTEXTS_PATH = DATA_DIR / "contexts.json"

CONTEXT_MODEL = "claude-haiku-4-5"
PRICE_IN, PRICE_OUT = 1.00, 5.00  # USD pro 1M Tokens, Haiku 4.5

# Übersetzung des Prompts aus Anthropics "Contextual Retrieval"-Beitrag.
CONTEXT_PROMPT = """<document>
{document}
</document>
Hier ist der Abschnitt, den wir innerhalb des Gesamtdokuments verorten wollen:
<chunk>
{chunk}
</chunk>
Gib einen kurzen, prägnanten Kontext auf Deutsch, der diesen Abschnitt im Gesamtdokument verortet, um die Auffindbarkeit des Abschnitts bei einer Suche zu verbessern. Antworte ausschließlich mit dem Kontext, sonst nichts."""


def cache_key(article, section):
    raw = article["text"] + "\x00" + section["text"] + "\x00" + CONTEXT_MODEL + CONTEXT_PROMPT
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def generate_context(client, article, section):
    start = time.perf_counter()
    response = client.messages.create(
        model=CONTEXT_MODEL,
        max_tokens=300,
        temperature=0,
        messages=[{"role": "user", "content": CONTEXT_PROMPT.format(
            document=article["text"], chunk=section["text"])}],
    )
    latency = time.perf_counter() - start
    text = "".join(b.text for b in response.content if b.type == "text").strip()
    return {
        "context": text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "latency_s": round(latency, 3),
        "stop_reason": response.stop_reason,
    }


def main():
    load_dotenv(ROOT / ".env")
    DATA_DIR.mkdir(exist_ok=True)
    articles = load_articles()
    contexts = json.loads(CONTEXTS_PATH.read_text(encoding="utf-8")) if CONTEXTS_PATH.exists() else {}

    client = None
    new_calls = []
    chunks = {"sections": [], "articles": [], "contextual": []}

    for a in articles:
        meta = {"file": a["file"], "title": a["title"], "date": a["date"]}
        chunks["articles"].append({"id": a["file"], **meta, "text": a["text"]})

        for s in a["sections"]:
            chunk_id = f"{a['file']}#{s['index']}"
            chunks["sections"].append({"id": chunk_id, **meta, "heading": s["heading"], "text": s["text"]})

            key = cache_key(a, s)
            if key not in contexts:
                client = client or anthropic.Anthropic()
                contexts[key] = {"chunk_id": chunk_id, **generate_context(client, a, s)}
                new_calls.append(contexts[key])
                if contexts[key]["stop_reason"] != "end_turn":
                    print(f"WARNUNG {chunk_id}: stop_reason={contexts[key]['stop_reason']}")
                # Nach jedem Aufruf speichern, damit ein Abbruch nichts kostet.
                CONTEXTS_PATH.write_text(json.dumps(contexts, ensure_ascii=False, indent=2), encoding="utf-8")

            context = contexts[key]["context"]
            chunks["contextual"].append({
                "id": chunk_id, **meta, "heading": s["heading"], "context": context,
                "text": f"{context}\n\n{s['text']}",
            })

    CHUNKS_PATH.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    for name, items in chunks.items():
        print(f"{name:11} {len(items):4} Chunks")

    if new_calls:
        tin = sum(c["input_tokens"] for c in new_calls)
        tout = sum(c["output_tokens"] for c in new_calls)
        cost = tin / 1e6 * PRICE_IN + tout / 1e6 * PRICE_OUT
        print(f"{len(new_calls)} neue Kontext-Aufrufe: {tin} Input-, {tout} Output-Tokens, {cost:.4f} USD")
    else:
        print("Keine neuen API-Aufrufe (alle Kontexte aus dem Cache)")


if __name__ == "__main__":
    main()
