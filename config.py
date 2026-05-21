from pathlib import Path

OLLAMA_BASE_URL  = "http://localhost:11434"
EMBEDDING_MODEL  = "embeddinggemma"
CHAT_MODEL       = "granite4.1:3b"

DOCUMENTS_DIR    = Path("documents")
EMBEDDINGS_DIR   = Path("embeddings")

SCAN_INTERVAL    = 1   # seconds
TOP_K            = 5
SCORE_THRESHOLD  = 0.3
PORT             = 5000

SUPPORTED_EXT    = {".txt", ".md", ".rst", ".csv", ".json", ".html", ".xml", ".py", ".yaml", ".toml"}

DOCUMENTS_DIR.mkdir(exist_ok=True)
EMBEDDINGS_DIR.mkdir(exist_ok=True)
