import hashlib, json, logging, threading, requests
from pathlib import Path
import config

log = logging.getLogger(__name__)


def _embed(text):
    log.info("[embed] sending %d chars to ollama...", len(text))
    r = requests.post(f"{config.OLLAMA_BASE_URL}/api/embed",
                      json={"model": config.EMBEDDING_MODEL, "input": text},
                      timeout=60)
    r.raise_for_status()
    emb = r.json()["embeddings"][0]
    log.info("[embed] got dim=%d", len(emb))
    return emb


def _hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# path_str -> file_hash, populated from disk on startup
_indexed = {}


def _load_existing():
    for f in config.EMBEDDINGS_DIR.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            _indexed[d["source"]] = d["file_hash"]
        except Exception:
            pass
    log.info("Loaded %d existing embeddings", len(_indexed))


def _index_file(path):
    path_str = str(path.resolve())
    log.info("[index] reading %s", path.name)
    text = path.read_text(encoding="utf-8", errors="replace")
    log.info("[index] read %d chars, embedding...", len(text))
    emb = _embed(text)
    h = _hash(path)
    out = {"source": path_str, "filename": path.name,
           "file_hash": h, "text": text, "embedding": emb}
    (config.EMBEDDINGS_DIR / f"{h}.json").write_text(json.dumps(out))
    _indexed[path_str] = h
    log.info("[index] done: %s", path.name)


def _remove_file(path_str):
    h = _indexed.pop(path_str, None)
    if h:
        (config.EMBEDDINGS_DIR / f"{h}.json").unlink(missing_ok=True)
    log.info("[index] removed: %s", path_str)


def scan():
    found = {str(p.resolve()) for p in config.DOCUMENTS_DIR.rglob("*")
             if p.is_file() and p.suffix.lower() in config.SUPPORTED_EXT}

    for path_str in list(_indexed):
        if path_str not in found:
            _remove_file(path_str)

    for path_str in found:
        path = Path(path_str)
        h = _hash(path)
        if _indexed.get(path_str) == h:
            continue
        try:
            _index_file(path)
        except Exception as e:
            log.error("[index] failed %s: %s", path.name, e)


def query(question):
    import math
    log.info("[query] embedding question...")
    q_emb = _embed(question)

    results = []
    for f in config.EMBEDDINGS_DIR.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            emb = d["embedding"]
            dot = sum(a*b for a,b in zip(q_emb, emb))
            score = dot / (math.sqrt(sum(a*a for a in q_emb)) * math.sqrt(sum(b*b for b in emb)))
            results.append({"text": d["text"], "filename": d["filename"], "score": score})
        except Exception:
            pass

    results.sort(key=lambda x: x["score"], reverse=True)
    top = [r for r in results[:config.TOP_K] if r["score"] >= config.SCORE_THRESHOLD]
    log.info("[query] returning %d/%d results above threshold", len(top), len(results))
    return top


def start():
    _load_existing()
    def _loop():
        scan()
        while True:
            threading.Event().wait(config.SCAN_INTERVAL)
            scan()
    threading.Thread(target=_loop, daemon=True, name="indexer").start()
    log.info("Indexer started")
