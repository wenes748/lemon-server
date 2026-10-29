# server/auth.py
import time
import secrets
from mailer import generate_code

CODE_TTL = 600

_pending_codes = {}
_sessions = {}


def create_code(email: str, chat_id: str) -> str:
    code = generate_code()
    _pending_codes[email] = {
        "code": code,
        "expires_at": time.time() + CODE_TTL,
        "chat_id": chat_id,
    }
    return code


def verify_code(email: str, code: str) -> bool:
    entry = _pending_codes.get(email)
    if not entry:
        return False
    if time.time() > entry["expires_at"]:
        del _pending_codes[email]
        return False
    if entry["code"] != code:
        return False
    del _pending_codes[email]
    return True


def create_session(email: str) -> str:
    token = secrets.token_urlsafe(32)
    _sessions[token] = email
    return token


def get_email_by_token(token: str) -> str | None:
    return _sessions.get(token)