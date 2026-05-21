"""
Local RAG Flask API using Ollama + ChromaDB
- Embeddings: embeddinggemma via Ollama
- Chat: granite4.1:3b via Ollama
- Vector DB: ChromaDB (local, persistent)
- Document folder: ./documents (auto-scanned)
"""

import os
import logging
from flask import Flask, request, jsonify, Response, stream_with_context
from flask.logging import default_handler

from config import Config
from indexer import DocumentIndexer
from rag import RAGEngine

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────────────────────────
app = Flask(__name__)
cfg = Config()

indexer = DocumentIndexer(cfg)
rag     = RAGEngine(cfg)

# Start background folder watcher
indexer.start()


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    """Quick liveness check."""
    stats = indexer.stats()
    return jsonify({"status": "ok", **stats})


# ── Index status ──────────────────────────────────────────────────────────────
@app.get("/index/status")
def index_status():
    """Returns current indexing state and known documents."""
    return jsonify(indexer.stats())


@app.post("/index/refresh")
def index_refresh():
    """Force an immediate re-scan of the documents folder."""
    added, removed = indexer.scan_now()
    return jsonify({"added": added, "removed": removed})


# ── Chat ──────────────────────────────────────────────────────────────────────
@app.post("/chat")
def chat():
    """
    RAG-grounded chat endpoint.

    Body:
      {
        "message": "your question",
        "history": [                   # optional, list of prior turns
          {"role": "user",      "content": "..."},
          {"role": "assistant", "content": "..."}
        ],
        "top_k": 5,                    # optional, default 5
        "stream": false                # optional, set true for SSE stream
      }

    The model is instructed to answer ONLY from retrieved context.
    If context is insufficient it will say so explicitly.
    """
    body = request.get_json(silent=True) or {}

    message = (body.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Field 'message' is required and must not be empty."}), 400

    if len(message) > cfg.MAX_QUERY_LEN:
        return jsonify({
            "error": f"Message too long (max {cfg.MAX_QUERY_LEN} chars)."
        }), 400

    history  = body.get("history", [])
    top_k    = min(int(body.get("top_k", cfg.DEFAULT_TOP_K)), cfg.MAX_TOP_K)
    do_stream = bool(body.get("stream", False))

    # Validate history format
    for turn in history:
        if not isinstance(turn, dict) or turn.get("role") not in ("user", "assistant"):
            return jsonify({"error": "history items must have role 'user' or 'assistant'."}), 400

    # Check index is non-empty
    stats = indexer.stats()
    if stats["total_chunks"] == 0:
        return jsonify({
            "error": "No documents have been indexed yet. "
                     "Add files to the 'documents/' folder and wait for indexing."
        }), 503

    if do_stream:
        def generate():
            for chunk in rag.stream_answer(message, history, top_k):
                yield chunk
        return Response(stream_with_context(generate()),
                        content_type="text/event-stream")

    result = rag.answer(message, history, top_k)
    return jsonify(result)


# ── Documents list ────────────────────────────────────────────────────────────
@app.get("/documents")
def list_documents():
    """Lists all currently indexed source documents."""
    return jsonify(indexer.list_documents())


# ── Error handlers ────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found."}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed."}), 405

@app.errorhandler(500)
def internal(e):
    log.exception("Unhandled exception")
    return jsonify({"error": "Internal server error."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=cfg.PORT, debug=False)
