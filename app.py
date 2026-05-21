import logging
from flask import Flask, request, jsonify
import config, indexer, rag

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

app = Flask(__name__)
indexer.start()


@app.get("/health")
def health():
    return jsonify({"status": "ok", "indexed_files": len(indexer._indexed)})


@app.get("/documents")
def documents():
    return jsonify(list(indexer._indexed.keys()))


@app.post("/index/refresh")
def refresh():
    indexer.scan()
    return jsonify({"indexed_files": len(indexer._indexed)})


@app.post("/chat")
def chat():
    body    = request.get_json() or {}
    message = (body.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    history = body.get("history", [])
    docs    = indexer.query(message)
    reply   = rag.answer(message, history, docs)

    return jsonify({
        "answer":  reply,
        "sources": [d["filename"] for d in docs],
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=False)
