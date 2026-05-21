"""Central configuration — tweak these to taste."""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    # ── Paths ────────────────────────────────────────────────────────────────
    DOCUMENTS_DIR: Path = field(default_factory=lambda: Path("documents"))
    CHROMA_DIR:    Path = field(default_factory=lambda: Path("chroma_db"))

    # ── Ollama ───────────────────────────────────────────────────────────────
    OLLAMA_BASE_URL:   str = "http://localhost:11434"
    EMBEDDING_MODEL:   str = "embeddinggemma"   # must be pulled in ollama
    CHAT_MODEL:        str = "granite4.1:3b"    # must be pulled in ollama

    # ── Chunking ─────────────────────────────────────────────────────────────
    CHUNK_SIZE:    int = 512   # characters per chunk
    CHUNK_OVERLAP: int = 64    # overlap between adjacent chunks

    # ── Retrieval ────────────────────────────────────────────────────────────
    DEFAULT_TOP_K: int = 5
    MAX_TOP_K:     int = 10
    # Cosine distance threshold — chunks above this are too far away
    # ChromaDB returns distance (lower = closer); 1.0 = orthogonal, 0 = identical
    DISTANCE_THRESHOLD: float = 0.55

    # ── Safety / limits ──────────────────────────────────────────────────────
    MAX_QUERY_LEN:   int = 2_000   # chars
    MAX_HISTORY_TURNS: int = 10    # pairs kept in context

    # ── Indexer ──────────────────────────────────────────────────────────────
    SCAN_INTERVAL_SECONDS: int = 15   # how often to poll the documents folder

    # ── Server ───────────────────────────────────────────────────────────────
    PORT: int = 5000

    # ── Supported file extensions ────────────────────────────────────────────
    SUPPORTED_EXTENSIONS: tuple = (".txt", ".md", ".rst", ".csv",
                                    ".json", ".html", ".htm", ".xml",
                                    ".py", ".yaml", ".yml", ".toml")

    def __post_init__(self):
        self.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
