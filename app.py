import logging
from threading import Thread
from flask import Flask, request, jsonify
from flask_cors import CORS
import config, indexer, rag, profiles, bot

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # Enable CORS for all routes

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Start the indexer
indexer.start()

# Start the Telegram bot in a background thread
Thread(target=bot.run, daemon=True).start()
log = logging.getLogger("app")
log.info("Telegram bot started in background thread")


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
    """
    Body: {
        "session_id": "any-string",   // used to track history server-side
        "message": "user text",
        "history": [                  // optional: pass previous turns from client
            {"role": "user",      "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }
    Response includes the updated history so the client can pass it back next turn.
    """
    body    = request.get_json() or {}
    message = (body.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    history = body.get("history", [])
    docs    = indexer.query(message)
    reply   = rag.answer(message, history, docs)

    # Append this turn to history and return it
    updated_history = history + [
        {"role": "user",      "content": message},
        {"role": "assistant", "content": reply},
    ]

    return jsonify({
        "answer":  reply,
        "sources": [d["filename"] for d in docs],
        "history": updated_history,
    })


@app.post("/profile")
def register_profile():
    """
    Body: {
        "phone":       "+39 333 1234567",
        "name":        "Mario",
        "surname":     "Rossi",
        "birthdate":   "1990-01-15",
        "fiscal_code": "RSSMRA90A15H501Z",
        "conversation": [
            {"role": "user",      "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }
    The conversation is the full chat session from /chat (i.e. the `history` field).
    """
    body = request.get_json() or {}

    required = ["phone", "name", "surname", "birthdate", "fiscal_code", "conversation"]
    missing  = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({"error": f"missing fields: {', '.join(missing)}"}), 400

    if not isinstance(body["conversation"], list) or len(body["conversation"]) == 0:
        return jsonify({"error": "conversation must be a non-empty list of messages"}), 400

    try:
        profile = profiles.save_profile(
            phone       = body["phone"],
            name        = body["name"],
            surname     = body["surname"],
            birthdate   = body["birthdate"],
            fiscal_code = body["fiscal_code"],
            conversation= body["conversation"],
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "status":  "ok",
        "summary": profile["summary"],
        "topics":  profile["topics"],
    })


@app.get("/profiles")
def list_profiles():
    """List all registered profiles (without fiscal codes for safety)."""
    all_p = profiles.load_all_profiles()
    return jsonify([
        {"phone": p["phone"], "name": p["name"], "surname": p["surname"],
         "summary": p.get("summary"), "topics": p.get("topics", [])}
        for p in all_p
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=False)
