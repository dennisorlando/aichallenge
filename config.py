from pathlib import Path

OLLAMA_BASE_URL = "http://localhost:11434"
EMBEDDING_MODEL = "embeddinggemma"
CHAT_MODEL      = "granite4.1:3b"

DOCUMENTS_DIR  = Path("documents")
EMBEDDINGS_DIR = Path("embeddings")
PROFILES_DIR   = Path("profiles")    # one JSON per phone number

SCAN_INTERVAL   = 15   # seconds
TOP_K           = 5
SCORE_THRESHOLD = 0.3
PORT            = 5000

SUPPORTED_EXT = {".txt", ".md", ".rst", ".csv", ".json", ".html", ".xml", ".py", ".yaml", ".toml"}

for _d in (DOCUMENTS_DIR, EMBEDDINGS_DIR, PROFILES_DIR):
    _d.mkdir(exist_ok=True)
