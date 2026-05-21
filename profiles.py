"""
Profiling module.

POST /profile  ->  receives user identity + full chat conversation,
                   uses the LLM to extract a list of interest topics,
                   appends a new entry to profiles/<phone>.json.

When a new document is indexed, compare_and_notify() is called in a
background thread: it loads every profile entry, asks the LLM whether the
document is relevant to that user's topics, and if so calls _notify().
"""

import json, logging, requests
from pathlib import Path
import config
import bot

log = logging.getLogger(__name__)


# ── LLM helpers ───────────────────────────────────────────────────────────────

def _llm(prompt, model=None, temperature=0.2):
    """Single-turn LLM call, returns text."""
    selected_model = model or config.COMPARE_MODEL
    r = requests.post(f"{config.OLLAMA_BASE_URL}/api/chat",
                      json={"model": selected_model,
                            "messages": [{"role": "user", "content": prompt}],
                            "stream": False,
                            "options": {"temperature": temperature}},
                      timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


def _extract_topics(conversation):
    """
    Given a chat conversation, return a list of topic strings and a rich,
    detailed description of the user's situation and background.
    Returns (topics: list[str], detailed_context: str).
    """
    lines = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in conversation
    )
    prompt = f"""\
Analizza attentamente questa conversazione tra un utente e un assistente del Comune di Trento.
Estrai le seguenti informazioni in formato JSON:

1. "topics": Una lista di brevi stringhe che rappresentano gli interessi espliciti dell'utente (es. ["asili nido", "trasporti"]).
2. "detailed_context": Una descrizione approfondita ma concisa della situazione dell'utente, dei suoi bisogni latenti, del suo ruolo (es. genitore, studente, lavoratore) e di qualsiasi dettaglio rilevante emerso (es. "Genitore interessato ai costi degli asili per il figlio", "Studente pendolare che usa la linea 5"). Includi ogni informazione che possa aiutare a capire se un futuro documento potrebbe interessargli.

Rispondi UNICAMENTE con il JSON:
{{
  "topics": ["...", "..."],
  "detailed_context": "..."
}}

CONVERSAZIONE:
{lines}"""

    raw = _llm(prompt)
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(raw)
    return data.get("topics", []), data.get("detailed_context", "")


# ── Notification mock ─────────────────────────────────────────────────────────

def _notify(phone, name, message):
    """Sends a real Telegram notification using bot.py."""
    log.info("──────────────────────────────────────────")
    log.info("📱 NOTIFY  → %s (%s)", phone, name)
    log.info("   MSG: %s", message)
    log.info("──────────────────────────────────────────")
    
    # Try to send the message via Telegram
    success = bot.send_message(message)
    if success:
        log.info("[bot] Message delivered to Telegram")
    else:
        log.warning("[bot] Failed to deliver message to Telegram (maybe no user has messaged the bot yet?)")


# ── Profile storage ───────────────────────────────────────────────────────────

def _profile_path(phone):
    safe = phone.replace("+", "").replace(" ", "")
    return config.PROFILES_DIR / f"{safe}.json"


def save_profile(phone, name, surname, birthdate, fiscal_code, conversation):
    log.info("[profile] extracting detailed profile for %s %s (%s)...", name, surname, phone)
    topics, detailed_context = _extract_topics(conversation)
    log.info("[profile] topics: %s, context: %s", topics, detailed_context)

    path = _profile_path(phone)
    entries = []

    # If the file already exists, read existing entries to avoid overwriting them
    if path.exists():
        try:
            existing_data = json.loads(path.read_text(encoding="utf-8"))
            if "entries" in existing_data:
                entries = existing_data["entries"]
            elif "topics" in existing_data:
                # Backward-compatibility: migrate old single-entry format if encountered
                entries = [{
                    "summary": existing_data.get("summary", ""),
                    "detailed_context": existing_data.get("summary", ""),
                    "topics": existing_data.get("topics", []),
                    "conversation": existing_data.get("conversation", [])
                }]
        except Exception as e:
            log.warning("[profile] could not read existing profile for %s: %s", phone, e)

    # Append the newly extracted topics and context association
    entries.append({
        "summary": detailed_context, # Keep summary for backward compatibility
        "detailed_context": detailed_context,
        "topics": topics,
        "conversation": conversation,
    })

    profile = {
        "phone":       phone,
        "name":        name,
        "surname":     surname,
        "birthdate":   birthdate,
        "fiscal_code": fiscal_code,
        "entries":     entries,
    }
    
    path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("[profile] saved profile for %s (total entries: %d)", phone, len(entries))
    
    return {
        "summary": detailed_context,
        "topics": topics
    }


def load_all_profiles():
    """
    Loads all profiles from disk and flattens their internal entries list.
    """
    flat_profiles = []
    for f in config.PROFILES_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if "entries" in data:
                for entry in data["entries"]:
                    flat_profiles.append({
                        "phone":       data["phone"],
                        "name":        data["name"],
                        "surname":     data["surname"],
                        "birthdate":   data["birthdate"],
                        "fiscal_code": data["fiscal_code"],
                        "summary":     entry.get("summary", ""),
                        "detailed_context": entry.get("detailed_context", entry.get("summary", "")),
                        "topics":      entry.get("topics", []),
                        "conversation": entry.get("conversation", [])
                    })
            elif "topics" in data:
                # Legacy fallback
                data["detailed_context"] = data.get("summary", "")
                flat_profiles.append(data)
        except Exception as e:
            log.warning("[profile] could not load %s: %s", f.name, e)
    return flat_profiles


# ── Document → profile matching ───────────────────────────────────────────────

def compare_and_notify(doc_filename, doc_text):
    """
    Called in a background thread after a document is indexed.
    For each saved profile association, ask the LLM if this document is relevant
    to the user's situation and topics. If yes, generate a tailored message and notify.
    """
    profiles = load_all_profiles()
    if not profiles:
        log.info("[notify] no profiles to compare against")
        return

    log.info("[notify] comparing '%s' against %d profile association(s)...", doc_filename, len(profiles))

    for p in profiles:
        topics = p.get("topics", [])
        context = p.get("detailed_context", "sconosciuto")
        
        topics_str = ", ".join(topics)
        prompt = f"""\
Un nuovo documento chiamato "{doc_filename}" è stato aggiunto alla base di conoscenza.
Contenuto del documento (primi 1500 caratteri):
{doc_text[:1500]}

Questo utente ha il seguente profilo:
- Nome: {p['name']} {p['surname']}
- Situazione/Contesto: {context}
- Argomenti di interesse: {topics_str}

Domanda: Questo documento è significativamente rilevante per la situazione o gli argomenti di questo utente?
Considera sia i bisogni espliciti (topics) che quelli latenti deducibili dal contesto (situazione).

Se SÌ, scrivi un breve messaggio di notifica amichevole e personalizzato (massimo 2-3 frasi)
nella stessa lingua usata dall'utente nella conversazione, adattato al suo background.
Se NO, rispondi solo con la parola: NO

Rispondi o con "NO" o con il messaggio di notifica, nient'altro."""

        result = _llm(prompt)

        if result.strip().upper() == "NO":
            log.info("[notify] '%s' not relevant for %s %s (Context: %s)", doc_filename, p['name'], p['surname'], context)
            continue

        _notify(p["phone"], f"{p['name']} {p['surname']}", result.strip())
