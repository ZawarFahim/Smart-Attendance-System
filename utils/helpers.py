"""
Helper functions for UI management.
"""

def center_window(window, width: int, height: int):
    """
    Centers a Tkinter window on the screen.
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))

    window.geometry(f"{width}x{height}+{x}+{y}")

def clear_frame(frame):
    """
    Destroys all child widgets inside a given tkinter frame.
    """
    for child in frame.winfo_children():
        child.destroy()

import hashlib

# ── bcrypt support (optional, graceful fallback) ──────────────────────────────
try:
    import bcrypt as _bcrypt
    _BCRYPT_AVAILABLE = True
except ImportError:
    _BCRYPT_AVAILABLE = False

def hash_password(password: str) -> str:
    """
    Hash a password.

    Uses bcrypt when available (new default for Excel-imported students).
    Falls back to returning plaintext so existing seed-data accounts
    that store passwords in cleartext continue to work.
    """
    if _BCRYPT_AVAILABLE:
        return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")
    # Legacy: store plaintext (matches original seed data convention)
    return str(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a stored password against a plaintext attempt.

    Supports three storage formats:
      1. bcrypt hash  (starts with '$2b$' or '$2a$')  -> use bcrypt.checkpw
      2. SHA-256 hex  (64 hex chars)                  -> compare hex digests
      3. Plaintext                                    -> direct string compare
    """
    if not plain_password or not hashed_password:
        return False

    hashed_str = str(hashed_password)

    # bcrypt detection
    if _BCRYPT_AVAILABLE and hashed_str.startswith("$2"):
        try:
            return _bcrypt.checkpw(plain_password.encode("utf-8"),
                                   hashed_str.encode("utf-8"))
        except Exception:
            return False

    # SHA-256 detection (64 lowercase hex chars)
    if len(hashed_str) == 64 and all(c in "0123456789abcdef" for c in hashed_str.lower()):
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_str.lower()

    # Legacy plaintext comparison
    return str(plain_password) == hashed_str

