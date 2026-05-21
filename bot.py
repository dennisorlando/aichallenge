import logging
import requests

# ─────────────────────────────────────────────
#  CONFIGURATION — paste your token here
# ─────────────────────────────────────────────
BOT_TOKEN = "8943691629:AAFlOeM3NfiiVhrXk1SuZTqVre1T1NqKuUE"
# ─────────────────────────────────────────────

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Keeps track of the last processed update so we don't handle duplicates
_last_update_id: int = 0

# The chat_id of the most recent sender (used as default target by send_message)
_current_chat_id: int | None = None


# ─────────────────────────────────────────────
#  PUBLIC API
# ─────────────────────────────────────────────

def send_message(message: str, chat_id: int | None = None) -> bool:
    """
    Send a text message to a Telegram chat.

    Args:
        message:  The text to send.
        chat_id:  Target chat / user ID.  When omitted, the message is sent
                  to whoever last wrote to the bot.

    Returns:
        True on success, False otherwise.
    """
    target = chat_id or _current_chat_id
    if target is None:
        logger.warning("send_message called before any user message was received.")
        return False

    payload = {"chat_id": target, "text": message}
    try:
        resp = requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Message sent to chat %s: %s", target, message)
        return True
    except requests.RequestException as exc:
        logger.error("Failed to send message: %s", exc)
        return False


# ─────────────────────────────────────────────
#  INTERNAL HELPERS
# ─────────────────────────────────────────────

def _get_updates(offset: int = 0, timeout: int = 30) -> list[dict]:
    """Long-poll the Telegram getUpdates endpoint."""
    params = {"offset": offset, "timeout": timeout}
    try:
        resp = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=timeout + 5)
        resp.raise_for_status()
        return resp.json().get("result", [])
    except requests.RequestException as exc:
        logger.error("Error fetching updates: %s", exc)
        return []


def _handle_update(update: dict) -> None:
    """Dispatch a single Telegram update to the appropriate handler."""
    global _current_chat_id

    message = update.get("message") or update.get("edited_message")
    if not message:
        return  # Ignore non-message updates (inline queries, etc.)

    chat_id: int = message["chat"]["id"]
    _current_chat_id = chat_id  # remember the sender for send_message()

    text: str = message.get("text", "")
    user: dict = message.get("from", {})
    username: str = user.get("username") or user.get("first_name", "unknown")

    logger.info("Message from %s (chat %s): %s", username, chat_id, text)

    # ──────────────────────────────────────────
    #  YOUR LOGIC GOES HERE
    #  Example: echo every message back
    # ──────────────────────────────────────────
    on_message(chat_id=chat_id, username=username, text=text)


def on_message(chat_id: int, username: str, text: str) -> None:
    """
    Called for every text message the bot receives.
    Replace the body below with your own logic.
    """
    # Simple echo example — remove or replace this:
    reply = f"Hello {username}! You said: {text}"
    send_message(reply, chat_id=chat_id)


# ─────────────────────────────────────────────
#  POLLING LOOP
# ─────────────────────────────────────────────

def run() -> None:
    """Start the bot and poll for updates indefinitely."""
    global _last_update_id

    logger.info("Bot is starting poll loop...")
    while True:
        try:
            updates = _get_updates(offset=_last_update_id + 1)
            for update in updates:
                _last_update_id = update["update_id"]
                _handle_update(update)
        except Exception as e:
            logger.error("Error in bot polling loop: %s", e)
            import time
            time.sleep(5)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    run()