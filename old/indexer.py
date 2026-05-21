"""
Dead-simple indexer.
- Uses `ollama run embeddinggemma` via subprocess (same as CLI)
- One embedding per whole document, no chunking
- Stores embeddings as JSON files in embeddings/
- Background thread rescans every SCAN_INTERVAL_SECONDS
"""

import hashlib
import json
import logging

import threading

from pathlib import Path
from typing import Dict, List, Tuple

from config import Config

log = logging.getLogger(__name__)


def _embed(text: str, model: str, base_url: str) -> List[float]:
    import requests
    url = f"{base_url}/api/embed"
    log.info("[embed] -> POST %s  model=%s  input_len=%d chars", url, model, len(text))
    resp = requests.post(url, json={"model": model, "input": text}, timeout=60)
    log.info("[embed] <- status=%d", resp.status_code)
    resp.raise_for_status()
    emb = resp.json()["embeddings"][0]
    log.info("[embed] ok, dim=%d", len(emb))
    return emb


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")


class DocumentIndexer:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._embeddings_dir = Path("embeddings")
        self._embeddings_dir.mkdir(exist_ok=True)
        self._stop = threading.Event()
        self._thread = None
        # path -> hash, in memory
        self._indexed: Dict[str, str] = {}
        self._load_existing()

    def _load_existing(self):
        """On startup, read all existing embedding JSON files into memory."""
        for f in self._embeddings_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                self._indexed[data["source"]] = data["file_hash"]
            except Exception:
                pass
        log.info("Loaded %d existing embeddings", len(self._indexed))

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True, name="indexer")
        self._thread.start()
        log.info("Indexer started (scan every %ds)", self.cfg.SCAN_INTERVAL_SECONDS)

    def stop(self):
        self._stop.set()

    def scan_now(self) -> Tuple[List[str], List[str]]:
        return self._scan()

    def stats(self) -> dict:
        return {
            "indexed_files": len(self._indexed),
            "documents_dir": str(self.cfg.DOCUMENTS_DIR.resolve()),
        }

    def list_documents(self) -> dict:
        return {"documents": list(self._indexed.keys())}

    def query(self, question: str, top_k: int) -> List[dict]:
        """
        Embed the question, compute cosine similarity against all stored
        embeddings, return top_k results sorted by score.
        """
        import math

        try:
            q_emb = _embed(question, self.cfg.EMBEDDING_MODEL, self.cfg.OLLAMA_BASE_URL)
        except Exception as e:
            log.error("Failed to embed question: %s", e)
            return []

        results = []
        for f in self._embeddings_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                emb = data["embedding"]
                # cosine similarity
                dot = sum(a * b for a, b in zip(q_emb, emb))
                na = math.sqrt(sum(a * a for a in q_emb))
                nb = math.sqrt(sum(b * b for b in emb))
                score = dot / (na * nb) if na and nb else 0.0
                results.append({
                    "text":     data["text"],
                    "filename": data["filename"],
                    "source":   data["source"],
                    "score":    score,
                })
            except Exception as e:
                log.warning("Skipping %s: %s", f, e)

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    # ── Internal ──────────────────────────────────────────────────────────────

    def _run(self):
        self._scan()
        while not self._stop.wait(timeout=self.cfg.SCAN_INTERVAL_SECONDS):
            self._scan()

    def _scan(self) -> Tuple[List[str], List[str]]:
        added, removed = [], []
        docs_dir = self.cfg.DOCUMENTS_DIR
        if not docs_dir.exists():
            return added, removed

        found = {
            str(p.resolve())
            for p in docs_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in self.cfg.SUPPORTED_EXTENSIONS
        }

        # Remove deleted
        for path_str in list(self._indexed):
            if path_str not in found:
                self._remove(path_str)
                removed.append(path_str)

        # Add / update
        for path_str in found:
            path = Path(path_str)
            try:
                h = _file_hash(path)
            except OSError:
                continue
            if self._indexed.get(path_str) == h:
                continue
            log.info("[scan] reading file: %s", path.name)
            try:
                text = _read_file(path)
                log.info("[scan] read %d chars, requesting embedding...", len(text))
                emb = _get_embedding(text, self.cfg.EMBEDDING_MODEL, self.cfg.OLLAMA_BASE_URL)
                log.info("[scan] saving embedding to disk...")
                out = {
                    "source":    path_str,
                    "filename":  path.name,
                    "file_hash": h,
                    "text":      text,
                    "embedding": emb,
                }
                safe_name = h + ".json"
                (self._embeddings_dir / safe_name).write_text(json.dumps(out))
                self._indexed[path_str] = h
                log.info("[scan] done: %s", path.name)
                added.append(path_str)
            except Exception as e:
                log.error("[scan] FAILED to index %s: %s", path.name, e)

        return added, removed

    def _remove(self, path_str: str):
        h = self._indexed.pop(path_str, None)
        if h:
            f = self._embeddings_dir / (h + ".json")
            f.unlink(missing_ok=True)
        log.info("Removed: %s", path_str)
