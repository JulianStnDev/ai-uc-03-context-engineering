"""Lädt die FocusFlow-Hilfeartikel aus corpus/ und das Goldset aus evals/.

Jeder Artikel wird in Titel, Datum und Abschnitte zerlegt. Die Abschnitte sind
die Grundlage für alle Chunking-Varianten in chunk.py.
"""
import csv
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
CORPUS_DIR = ROOT / "corpus"
GOLDSET_PATH = ROOT / "evals" / "goldset.csv"

DATE_RE = re.compile(r"^Zuletzt aktualisiert: (\d{2}\.\d{2}\.\d{4})\s*$", re.MULTILINE)


def parse_article(path):
    text = path.read_text(encoding="utf-8").strip()
    lines = text.split("\n")
    if not lines[0].startswith("# "):
        raise ValueError(f"{path.name}: erste Zeile ist kein Titel")
    title = lines[0][2:].strip()

    date_match = DATE_RE.search(text)
    if not date_match:
        raise ValueError(f"{path.name}: keine Zeile 'Zuletzt aktualisiert'")
    date = datetime.strptime(date_match.group(1), "%d.%m.%Y").date()

    # Alles nach der Datumszeile ist Body. Der Einleitungstext vor dem ersten
    # "## " wird ein eigener Abschnitt ohne Überschrift.
    body = text[date_match.end():].strip()
    sections = []
    for i, part in enumerate(re.split(r"^(?=## )", body, flags=re.MULTILINE)):
        part = part.strip()
        if not part:
            continue
        heading = part.split("\n", 1)[0][3:].strip() if part.startswith("## ") else None
        sections.append({"index": i, "heading": heading, "text": part})

    return {
        "file": path.name,
        "title": title,
        "date": date.isoformat(),
        "text": text,
        "sections": sections,
    }


def load_articles():
    return [parse_article(p) for p in sorted(CORPUS_DIR.glob("*.md"))]


def load_goldset():
    rows = list(csv.DictReader(GOLDSET_PATH.open(encoding="utf-8")))
    for r in rows:
        sources = [s.strip() for s in r["erwartete_quellen"].split(";")]
        r["quellen"] = [] if sources == ["keine"] else sources
    return rows


if __name__ == "__main__":
    articles = load_articles()
    for a in articles:
        print(f"{a['file']:36} {a['date']}  {len(a['sections'])} Abschnitte")
    print(f"{len(articles)} Artikel, {sum(len(a['sections']) for a in articles)} Abschnitte")
    print(f"{len(load_goldset())} Goldset-Fragen")
