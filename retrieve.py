"""Lokale Embeddings und Cosinus-Retrieval über die Chunk-Varianten aus chunk.py.

Die Embeddings der Chunks werden unter data/emb/ gecacht (nicht im Git) und nur
neu berechnet, wenn sich Modell oder Chunk-Texte ändern.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).parent
CHUNKS_PATH = ROOT / "data" / "chunks.json"
EMB_DIR = ROOT / "data" / "emb"

# e5 ist asymmetrisch trainiert und erwartet Präfixe für Frage und Passage.
# bge-m3 braucht für Dense-Retrieval keine Präfixe.
MODELS = {
    "e5-base": {"name": "intfloat/multilingual-e5-base", "query_prefix": "query: ", "passage_prefix": "passage: "},
    "bge-m3": {"name": "BAAI/bge-m3", "query_prefix": "", "passage_prefix": ""},
}

_loaded = {}


def load_model(key):
    if key not in _loaded:
        _loaded[key] = SentenceTransformer(MODELS[key]["name"], device="mps")
    return _loaded[key]


def load_chunks():
    return json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))


def count_truncated(model_key, texts):
    """Wie viele Texte sind länger als max_seq_length und werden abgeschnitten?"""
    model = load_model(model_key)
    prefix = MODELS[model_key]["passage_prefix"]
    lengths = [len(model.tokenizer(prefix + t)["input_ids"]) for t in texts]
    return sum(n > model.max_seq_length for n in lengths), max(lengths), model.max_seq_length


def embed_chunks(model_key, variant, chunks):
    cfg = MODELS[model_key]
    texts = [cfg["passage_prefix"] + c["text"] for c in chunks]
    digest = hashlib.sha256((cfg["name"] + "\x00".join(texts)).encode("utf-8")).hexdigest()[:12]
    path = EMB_DIR / f"{model_key}_{variant}_{digest}.npy"
    if path.exists():
        return np.load(path), True
    EMB_DIR.mkdir(parents=True, exist_ok=True)
    emb = load_model(model_key).encode(texts, normalize_embeddings=True, batch_size=16)
    np.save(path, emb)
    return emb, False


def embed_query(model_key, question):
    cfg = MODELS[model_key]
    return load_model(model_key).encode(cfg["query_prefix"] + question, normalize_embeddings=True)


def search(query_emb, chunk_emb, chunks, k=5):
    """Top-k Chunks nach Cosinus-Ähnlichkeit (Vektoren sind normalisiert → Skalarprodukt)."""
    # numpy + Apple Accelerate (macOS) meldet bei matmul fälschlich "divide by
    # zero"/"overflow". Geprüft: Embeddings endlich, Ergebnis = float64-Rechnung.
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        scores = chunk_emb @ query_emb
    order = np.argsort(-scores)[:k]
    return [{**chunks[i], "score": float(scores[i])} for i in order]
