"""Judge: bewertet jede Antwort aus data/answers.jsonl mit Sonnet 5.

Pro Antwort ein Aufruf mit Structured Output und zwei Kriterien:
  - bei typ != luecke: kernaussage_ok (Vergleich mit der Goldset-Kernaussage) + treu
  - bei typ == luecke: luecke_ok (nur Support-Verweis, keine Inhalte) + treu
treu = Faithfulness: Jede Behauptung muss durch den Kontext gedeckt sein, den das
Antwortmodell gesehen hat. Der Judge bekommt genau diesen Kontext.

Ergebnisse werden an data/judgments.jsonl angehängt, fertige Antworten übersprungen.
"""
import json
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from load_corpus import load_goldset

ROOT = Path(__file__).parent
ANSWERS_PATH = ROOT / "data" / "answers.jsonl"
JUDGMENTS_PATH = ROOT / "data" / "judgments.jsonl"
JUDGE_MODEL = "claude-sonnet-5"

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


def main():
    load_dotenv(ROOT / ".env")
    client = anthropic.Anthropic()
    questions = {q["id"]: q for q in load_goldset()}
    answers = [json.loads(l) for l in ANSWERS_PATH.open(encoding="utf-8")]

    done = set()
    if JUDGMENTS_PATH.exists():
        done = {(r["id"], r["variante"]) for r in map(json.loads, JUDGMENTS_PATH.open(encoding="utf-8"))}

    with JUDGMENTS_PATH.open("a", encoding="utf-8") as out:
        for a in answers:
            if (a["id"], a["variante"]) in done:
                continue
            row = judge(client, a, questions[a["id"]])
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            verdicts = {k: row[k] for k in ("kernaussage_ok", "luecke_ok", "treu") if k in row}
            print(f"{a['variante']:10} #{a['id']:>2}  {row['judge_s']:5.1f}s  {verdicts}")


if __name__ == "__main__":
    main()
