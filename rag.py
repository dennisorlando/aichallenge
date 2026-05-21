import json, logging, requests
import config

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a document assistant. Answer ONLY using the CONTEXT below.
If the context doesn't contain the answer, say: "I cannot answer this from the provided documents."
Always cite the source filename in your answer, like [filename.txt].
If documents contradict each other on the same fact, flag it with "⚠️ CONTRADICTION:" before answering.
Never answer from general knowledge. Never make up facts."""


def answer(question, history, context_docs):
    if not context_docs:
        return "I cannot answer this from the provided documents."

    context = "\n\n".join(
        f"[{d['filename']}]\n{d['text']}" for d in context_docs
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history[-(10*2):]  # keep last 10 turns
    messages.append({"role": "user", "content":
        f"CONTEXT:\n{context}\n\nQUESTION: {question}"})

    log.info("[rag] calling %s with %d context docs", config.CHAT_MODEL, len(context_docs))
    r = requests.post(f"{config.OLLAMA_BASE_URL}/api/chat",
                      json={"model": config.CHAT_MODEL, "messages": messages,
                            "stream": False, "options": {"temperature": 0.1}},
                      timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"]
