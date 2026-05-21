import json, logging, requests
import config

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
Sei un assistente per i documenti. Rispondi UNICAMENTE utilizzando il CONTESTO fornito sotto.
Se il contesto non contiene la risposta, dì: "Non posso rispondere a questa domanda basandomi sui documenti forniti."
Cita sempre il nome del file sorgente nella tua risposta, come [filename.txt].
Se i documenti si contraddicono su uno stesso fatto, segnalalo con "⚠️ CONTRADDIZIONE:" prima di rispondere.
Non rispondere mai basandoti sulla conoscenza generale. Non inventare fatti."""


def answer(question, history, context_docs):
    if not context_docs:
        return "Non posso rispondere a questa domanda basandomi sui documenti forniti."

    context = "\n\n".join(f"[{d['filename']}]\n{d['text']}" for d in context_docs)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history[-20:]   # last 10 turns (user+assistant = 2 each)
    messages.append({"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}"})

    log.info("[rag] calling %s with %d context docs, %d history msgs",
             config.CHAT_MODEL, len(context_docs), len(history))
    r = requests.post(f"{config.OLLAMA_BASE_URL}/api/chat",
                      json={"model": config.CHAT_MODEL, "messages": messages,
                            "stream": False, "options": {"temperature": 0.1}},
                      timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"]
