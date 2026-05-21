"""
DocumentIndexer
===============
- Watches the `documents/` folder in a background thread.
- Reads supported file types, splits them into overlapping chunks.
- Generates embeddings via Ollama (/api/embeddings).
- Stores chunks + embeddings in ChromaDB (persistent, local).
- Detects file additions, modifications (mtime/hash), and deletions.
"""

import hashlib
import logging
import threading
import time
from pathlib import Path
from typing import Dict, List, Tuple

import chromadb
import requests
from chromadb.config import Settings

from config import Config

log = logging.getLogger(__name__)


# ── Text splitter (simple recursive char splitter, no extra deps) ────────────

def _split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Split text into overlapping chunks on sentence/paragraph boundaries."""
    if not text.strip():
        return []

    chunks: List[str] = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)
        # Try to break on a newline or sentence boundary within the last 20%
        if end < length:
            search_from = max(start, end - chunk_size // 5)
            # prefer paragraph break
            nl = text.rfind("\n\n", search_from, end)
            if nl != -1:
                end = nl + 2
            else:
                # fallback: sentence end
                for sep in (". ", "! ", "? ", "\n"):
                    pos = text.rfind(sep, search_from, end)
                    if pos != -1:
                        end = pos + len(sep)
                        break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap

    return chunks


# ── File reading ──────────────────────────────────────────────────────────────

def _read_file(path: Path) -> str:
    """Best-effort UTF-8 read; falls back to latin-1."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


# ── Embeddings via Ollama ─────────────────────────────────────────────────────

def _embed(text: str, model: str, base_url: str) -> List[float]:
    resp = requests.post(
        f"{base_url}/api/embeddings",
        json={"model": model, "prompt": text},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]


# ── Indexer ───────────────────────────────────────────────────────────────────

class DocumentIndexer:
    """Persistent ChromaDB-backed document indexer with background scanner."""

    COLLECTION_NAME = "documents"

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

        # file_path → sha256 hash (tracks what we've indexed)
        self._indexed: Dict[str, str] = {}

        # ChromaDB — persistent, stored at cfg.CHROMA_DIR
        self._client = chromadb.PersistentClient(
            path=str(cfg.CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self._col = self._client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        # Restore known hashes from existing metadata
        self._restore_state()

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self):
        """Start background scanning thread."""
        self._thread = threading.Thread(target=self._run, daemon=True, name="indexer")
        self._thread.start()
        log.info("Indexer thread started (scan every %ds)", self.cfg.SCAN_INTERVAL_SECONDS)

    def stop(self):
        self._stop_event.set()

    def scan_now(self) -> Tuple[List[str], List[str]]:
        """Force an immediate scan. Returns (added_files, removed_files)."""
        with self._lock:
            return self._scan()

    def stats(self) -> dict:
        with self._lock:
            return {
                "total_chunks": self._col.count(),
                "indexed_files": len(self._indexed),
                "documents_dir": str(self.cfg.DOCUMENTS_DIR.resolve()),
            }

    def list_documents(self) -> dict:
        with self._lock:
            return {
                "documents": [
                    {"path": p, "hash": h}
                    for p, h in self._indexed.items()
                ]
            }

    def query(self, embedding: List[float], top_k: int) -> dict:
        """Query ChromaDB; returns raw results dict."""
        with self._lock:
            return self._col.query(
                query_embeddings=[embedding],
                n_results=min(top_k, max(self._col.count(), 1)),
                include=["documents", "metadatas", "distances"],
            )

    # ── Internal ─────────────────────────────────────────────────────────────

    def _run(self):
        # Initial scan
        with self._lock:
            self._scan()
        while not self._stop_event.wait(timeout=self.cfg.SCAN_INTERVAL_SECONDS):
            with self._lock:
                self._scan()

    def _scan(self) -> Tuple[List[str], List[str]]:
        """Detect new/changed/deleted files and update ChromaDB."""
        added: List[str] = []
        removed: List[str] = []

        docs_dir = self.cfg.DOCUMENTS_DIR
        if not docs_dir.exists():
            return added, removed

        # Discover all supported files (recursive)
        found_paths = {
            str(p.resolve())
            for p in docs_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in self.cfg.SUPPORTED_EXTENSIONS
        }

        # Remove deleted files
        for path_str in list(self._indexed.keys()):
            if path_str not in found_paths:
                self._remove_file(path_str)
                removed.append(path_str)

        # Add / update changed files
        for path_str in found_paths:
            path = Path(path_str)
            try:
                file_hash = _file_hash(path)
            except OSError:
                continue

            if self._indexed.get(path_str) == file_hash:
                continue  # unchanged

            if path_str in self._indexed:
                log.info("Re-indexing changed file: %s", path_str)
                self._remove_file(path_str)
            else:
                log.info("Indexing new file: %s", path_str)

            success = self._index_file(path, path_str, file_hash)
            if success:
                added.append(path_str)

        return added, removed

    def _index_file(self, path: Path, path_str: str, file_hash: str) -> bool:
        """Read, chunk, embed, and store a file. Returns True on success."""
        try:
            text = _read_file(path)
        except Exception as e:
            log.error("Cannot read %s: %s", path_str, e)
            return False

        chunks = _split_text(text, self.cfg.CHUNK_SIZE, self.cfg.CHUNK_OVERLAP)
        if not chunks:
            log.warning("No text extracted from %s", path_str)
            return False

        ids, embeddings, documents, metadatas = [], [], [], []

        for i, chunk in enumerate(chunks):
            try:
                emb = _embed(chunk, self.cfg.EMBEDDING_MODEL, self.cfg.OLLAMA_BASE_URL)
            except Exception as e:
                log.error("Embedding error for chunk %d of %s: %s", i, path_str, e)
                continue

            chunk_id = f"{file_hash}_{i}"
            ids.append(chunk_id)
            embeddings.append(emb)
            documents.append(chunk)
            metadatas.append({
                "source":    path_str,
                "filename":  path.name,
                "chunk_idx": i,
                "file_hash": file_hash,
            })

        if not ids:
            return False

        # Upsert in batches of 50 to avoid memory spikes
        batch = 50
        for start in range(0, len(ids), batch):
            self._col.upsert(
                ids=ids[start:start+batch],
                embeddings=embeddings[start:start+batch],
                documents=documents[start:start+batch],
                metadatas=metadatas[start:start+batch],
            )

        self._indexed[path_str] = file_hash
        log.info("Indexed %d chunks from %s", len(ids), path.name)
        return True

    def _remove_file(self, path_str: str):
        """Delete all chunks belonging to this file from ChromaDB."""
        try:
            self._col.delete(where={"source": path_str})
        except Exception as e:
            log.error("Failed to delete chunks for %s: %s", path_str, e)
        self._indexed.pop(path_str, None)
        log.info("Removed index for: %s", path_str)

    def _restore_state(self):
        """Rebuild in-memory hash map from ChromaDB metadata on startup."""
        try:
            result = self._col.get(include=["metadatas"])
            for meta in result.get("metadatas") or []:
                if meta and "source" in meta and "file_hash" in meta:
                    self._indexed[meta["source"]] = meta["file_hash"]
            log.info("Restored %d known files from ChromaDB", len(self._indexed))
        except Exception as e:
            log.warning("Could not restore state from ChromaDB: %s", e)
