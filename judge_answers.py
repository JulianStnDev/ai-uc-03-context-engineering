"""Judge: bewertet jede Antwort aus data/answers[_<lauf>].jsonl mit Sonnet 5.

Pro Antwort ein Aufruf mit Structured Output und zwei Kriterien:
  - bei typ != luecke: kernaussage_ok (Vergleich mit der Goldset-Kernaussage) + treu
  - bei typ == luecke: luecke_ok (nur Support-Verweis, keine Inhalte) + treu
treu = Faithfulness: Jede Behauptung muss durch den Kontext gedeckt sein, den das
Antwortmodell gesehen hat. Der Judge bekommt genau diesen Kontext.

Zusätzlich (zweiter Durchgang, nur für Antworten, die die alte Preisseite
pro-funktionen-und-preise.md zitieren): veraltet_gekennzeichnet – kennzeichnet die
Antwort diese Seite ausdrücklich als veraltet und nennt die aktuellen Werte?

Ergebnisse werden an data/judgments[_<lauf>].jsonl bzw. data/stale_judgments[_<lauf>].jsonl
angehängt, fertige Antworten übersprungen.

Aufruf: python judge_answers.py [v1|v2]   (Standard: v1)
"""
import json
import sys
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from load_corpus import load_goldset

ROOT = Path(__file__).parent
JUDGE_MODEL = "claude-sonnet-5"
STALE, CURRENT = "pro-funktionen-und-preise.md", "preise-und-tarife.md"


def run_path(name, run):
    return ROOT / "data" / (f"{name}.jsonl" if run == "v1" else f"{name}_{run}.jsonl")


JUDGE_SYSTEM = """Du bewertest Antworten eines Support-Assistenten für die App FocusFlow. Der Assistent sollte ausschließlich aus den mitgegebenen Hilfeartikeln (<kontext>) antworten. Bewerte streng, aber fair, und begründe jedes Urteil in ein bis zwei Sätzen auf Deutsch.

Kriterien:

treu (Faithfulness): true, wenn jede inhaltliche Behauptung der Antwort durch den <kontext> gedeckt ist – wörtlich oder als direkte, logisch zwingende Folgerung (z. B. eine Frist auf einen genannten Zeitraum anwenden). Maßgeblich ist nur der Kontext, nicht ob die Aussage in der Realität stimmt: Auch eine Aussage aus einer älteren Quelle im Kontext ist gedeckt. Der Verweis an den Support "Einstellungen > Hilfe > Kontakt" ist dem Assistenten vorgegeben und gilt immer als gedeckt. Höflichkeitsfloskeln und die "Quellen:"-Zeile zählen nicht. false, sobald eine Behauptung nicht im Kontext steht oder ihm widerspricht.

kernaussage_ok: true, wenn ein Kunde mit der Antwort die Information aus der Soll-Kernaussage erhält: Die Hauptaussage ist enthalten und nichts in der Antwort widerspricht der Kernaussage. Andere Formulierungen und zusätzliche korrekte Details sind erlaubt; fehlende Nebenpunkte sind tolerierbar, eine fehlende oder falsche Hauptaussage nicht.

luecke_ok: Die Frage ist in den Hilfeartikeln bewusst nicht beantwortet. true nur, wenn die Antwort sagt, dass dazu keine Information vorliegt, an den Support verweist und keine inhaltliche Antwort gibt – auch keine Vermutung und keine Teilantwort mit verwandten Informationen. Sonst false."""


def schema(first):
    return {
        "type": "object",
        "properties": {
            f"{first}_begruendung": {"type": "string"},
            first: {"type": "boolean"},
            "treu_begruendung": {"type": "string"},
            "treu": {"type": "boolean"},
        },
        "required": [f"{first}_begruendung", first, "treu_begruendung", "treu"],
        "additionalProperties": False,
    }


def judge(client, answer_row, question):
    is_gap = question["typ"] == "luecke"
    context_block = {"type": "text", "text": f"<kontext>\n{answer_row['kontext']}\n</kontext>"}
    if answer_row["variante"] == "corpus":
        context_block["cache_control"] = {"type": "ephemeral"}

    task = [f"<frage>\n{question['frage']}\n</frage>"]
    if not is_gap:
        task.append(f"<soll_kernaussage>\n{question['kernaussage']}\n</soll_kernaussage>")
    task.append(f"<antwort>\n{answer_row['antwort']}\n</antwort>")
    task.append("Bewerte die Antwort nach den Kriterien "
                + ("luecke_ok und treu." if is_gap else "kernaussage_ok und treu."))

    t0 = time.perf_counter()
    response = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=8000,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": [context_block, {"type": "text", "text": "\n\n".join(task)}]}],
        output_config={"format": {"type": "json_schema", "schema": schema("luecke_ok" if is_gap else "kernaussage_ok")}},
    )
    latency = time.perf_counter() - t0
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"#{question['id']} {answer_row['variante']}: stop_reason={response.stop_reason}")
    verdict = json.loads(next(b.text for b in response.content if b.type == "text"))
    u = response.usage
    return {
        "id": answer_row["id"], "variante": answer_row["variante"], **verdict,
        "judge_input_tokens": u.input_tokens,
        "judge_cache_write_tokens": u.cache_creation_input_tokens or 0,
        "judge_cache_read_tokens": u.cache_read_input_tokens or 0,
        "judge_output_tokens": u.output_tokens,
        "judge_s": round(latency, 3),
    }


STALE_SYSTEM = """Du prüfst Antworten eines Support-Assistenten für die App FocusFlow. Die Hilfe enthält zwei widersprüchliche Preisseiten: eine veraltete von 2024 und eine aktuelle von 2026 (beide unten). Die Antwort zitiert die veraltete Seite.

veraltet_gekennzeichnet: true nur, wenn beides erfüllt ist:
1. Die Antwort kennzeichnet die Angaben der veralteten Seite ausdrücklich als veraltet, überholt, älter oder nicht mehr gültig.
2. Die Antwort nennt die aktuellen Werte aus der Seite von 2026, soweit sie für die Frage relevant sind.
Sonst false – insbesondere, wenn die Antwort Angaben der alten Seite als gültig darstellt oder beide Stände unkommentiert nebeneinander stehen. Begründe in ein bis zwei Sätzen auf Deutsch."""

STALE_SCHEMA = {
    "type": "object",
    "properties": {"veraltet_gekennzeichnet_begruendung": {"type": "string"},
                   "veraltet_gekennzeichnet": {"type": "boolean"}},
    "required": ["veraltet_gekennzeichnet_begruendung", "veraltet_gekennzeichnet"],
    "additionalProperties": False,
}


def judge_stale(client, answer_row, question, pages):
    content = (f"<veraltete_seite datei=\"{STALE}\">\n{pages[STALE]}\n</veraltete_seite>\n\n"
               f"<aktuelle_seite datei=\"{CURRENT}\">\n{pages[CURRENT]}\n</aktuelle_seite>\n\n"
               f"<frage>\n{question['frage']}\n</frage>\n\n<antwort>\n{answer_row['antwort']}\n</antwort>")
    t0 = time.perf_counter()
    response = client.messages.create(
        model=JUDGE_MODEL, max_tokens=8000, system=STALE_SYSTEM,
        messages=[{"role": "user", "content": content}],
        output_config={"format": {"type": "json_schema", "schema": STALE_SCHEMA}},
    )
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"#{question['id']} {answer_row['variante']}: stop_reason={response.stop_reason}")
    u = response.usage
    return {
        "id": answer_row["id"], "variante": answer_row["variante"],
        **json.loads(next(b.text for b in response.content if b.type == "text")),
        "judge_input_tokens": u.input_tokens,
        "judge_cache_write_tokens": u.cache_creation_input_tokens or 0,
        "judge_cache_read_tokens": u.cache_read_input_tokens or 0,
        "judge_output_tokens": u.output_tokens,
        "judge_s": round(time.perf_counter() - t0, 3),
    }


def load_done(path):
    if not path.exists():
        return set()
    return {(r["id"], r["variante"]) for r in map(json.loads, path.open(encoding="utf-8"))}


def main(run):
    load_dotenv(ROOT / ".env")
    client = anthropic.Anthropic()
    questions = {q["id"]: q for q in load_goldset()}
    answers = [json.loads(l) for l in run_path("answers", run).open(encoding="utf-8")]
    judgments_path, stale_path = run_path("judgments", run), run_path("stale_judgments", run)

    done = load_done(judgments_path)
    with judgments_path.open("a", encoding="utf-8") as out:
        for a in answers:
            if (a["id"], a["variante"]) in done:
                continue
            row = judge(client, a, questions[a["id"]])
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            verdicts = {k: row[k] for k in ("kernaussage_ok", "luecke_ok", "treu") if k in row}
            print(f"{a['variante']:10} #{a['id']:>2}  {row['judge_s']:5.1f}s  {verdicts}")

    pages = {f: (ROOT / "corpus" / f).read_text(encoding="utf-8") for f in (STALE, CURRENT)}
    done = load_done(stale_path)
    with stale_path.open("a", encoding="utf-8") as out:
        for a in answers:
            if STALE not in a["zitiert"] or (a["id"], a["variante"]) in done:
                continue
            row = judge_stale(client, a, questions[a["id"]], pages)
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            print(f"veraltet   {a['variante']:10} #{a['id']:>2}  {row['judge_s']:5.1f}s  "
                  f"veraltet_gekennzeichnet={row['veraltet_gekennzeichnet']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
