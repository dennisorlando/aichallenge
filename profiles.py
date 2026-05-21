"""
Profiling module.

POST /profile  ->  receives user identity + full chat conversation,
                   uses the LLM to extract a list of interest topics,
                   saves a profile JSON under profiles/<phone>.json.

When a new document is indexed, compare_and_notify() is called in a
background thread: it loads every profile, asks the LLM whether the
document is relevant to that user's topics, and if so calls _notify().
"""

import json, logging, requests
from pathlib import Path
import config

log = logging.getLogger(__name__)


# ── LLM helpers ───────────────────────────────────────────────────────────────

def _llm(prompt, temperature=0.2):
    """Single-turn LLM call, returns text."""
    r = requests.post(f"{config.OLLAMA_BASE_URL}/api/chat",
                      json={"model": config.CHAT_MODEL,
                            "messages": [{"role": "user", "content": prompt}],
                            "stream": False,
                            "options": {"temperature": temperature}},
                      timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


def _extract_topics(conversation):
    """
    Given a chat conversation, return a list of topic strings and a short
    plain-language description of the user's situation/background.
    Returns (topics: list[str], profile_summary: str).
    """
    # Flatten conversation to readable text
    lines = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in conversation
    )
    prompt = f"""\
Read this conversation between a user and an assistant and extract:
1. A JSON list of short topic strings (max 10) representing what the user
   seems interested in or needs help with. Be specific, e.g.
   ["residence permit renewal", "Italian language courses", "university enrollment"].
2. A one-sentence plain description of the user's apparent situation/background,
   e.g. "Recent immigrant unfamiliar with Italian bureaucracy" or
   "University student looking for housing".

Respond ONLY with valid JSON in this exact shape, no extra text:
{{"topics": ["...", "..."], "summary": "..."}}

CONVERSATION:
{lines}"""

    raw = _llm(prompt)
    # Strip markdown fences if the model added them
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(raw)
    return data.get("topics", []), data.get("summary", "")


# ── Notification mock ─────────────────────────────────────────────────────────

def _notify(phone, name, message):
    """Mock notification — replace with real SMS/push logic later."""
    log.info("──────────────────────────────────────────")
    log.info("📱 NOTIFY  → %s (%s)", phone, name)
    log.info("   MSG: %s", message)
    log.info("──────────────────────────────────────────")
    print(f"\n[MOCK SMS] To {name} ({phone}):\n{message}\n")


# ── Profile storage ───────────────────────────────────────────────────────────

def _profile_path(phone):
    safe = phone.replace("+", "").replace(" ", "")
    return config.PROFILES_DIR / f"{safe}.json"


def save_profile(phone, name, surname, birthdate, fiscal_code, conversation):
    log.info("[profile] extracting topics for %s %s (%s)...", name, surname, phone)
    topics, summary = _extract_topics(conversation)
    log.info("[profile] topics: %s", topics)

    profile = {
        "phone":       phone,
        "name":        name,
        "surname":     surname,
        "birthdate":   birthdate,
        "fiscal_code": fiscal_code,
        "summary":     summary,
        "topics":      topics,
        "conversation": conversation,
    }
    _profile_path(phone).write_text(json.dumps(profile, ensure_ascii=False, indent=2))
    log.info("[profile] saved profile for %s", phone)
    return profile


def load_all_profiles():
    profiles = []
    for f in config.PROFILES_DIR.glob("*.json"):
        try:
            profiles.append(json.loads(f.read_text()))
        except Exception as e:
            log.warning("[profile] could not load %s: %s", f.name, e)
    return profiles


# ── Document → profile matching ───────────────────────────────────────────────

def compare_and_notify(doc_filename, doc_text):
    """
    Called in a background thread after a document is indexed.
    For each saved profile, ask the LLM if this document is relevant
    to the user's topics. If yes, generate a tailored message and notify.
    """
    profiles = load_all_profiles()
    if not profiles:
        log.info("[notify] no profiles to compare against")
        return

    log.info("[notify] comparing '%s' against %d profile(s)...", doc_filename, len(profiles))

    for p in profiles:
        topics = p.get("topics", [])
        if not topics:
            continue

        topics_str = ", ".join(topics)
        prompt = f"""\
A new document called "{doc_filename}" has been added to the knowledge base.
Document content (first 1500 chars):
{doc_text[:1500]}

This user has the following profile:
- Name: {p['name']} {p['surname']}
- Background: {p.get('summary', 'unknown')}
- Topics of interest: {topics_str}

Question: Is this document meaningfully relevant to this user's topics or situation?
If YES, write a short, friendly, personalised notification message (2-3 sentences max)
in the same language the user used in their conversation, tailored to their background.
For example, avoid jargon for someone unfamiliar with bureaucracy; be concise for an
expert user.
If NO, reply with only the word: NO

Reply with either "NO" or the notification message, nothing else."""

        result = _llm(prompt)

        if result.strip().upper() == "NO":
            log.info("[notify] '%s' not relevant for %s %s", doc_filename, p['name'], p['surname'])
            continue

        _notify(p["phone"], f"{p['name']} {p['surname']}", result.strip())
