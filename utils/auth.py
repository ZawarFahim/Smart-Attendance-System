"""
Password hashing utilities for ATTENDIFY.

Supports two modes:
  - bcrypt (preferred, used by excel_import_service for new students)
  - plaintext fallback (legacy, for seed data & existing users created before migration)

verify_password() accepts BOTH formats transparently so existing logins
are not broken after the migration.
"""

# Try to import bcrypt; graceful fallback if not installed
try:
    import bcrypt as _bcrypt
    _BCRYPT_AVAILABLE = True
except ImportError:
    _BCRYPT_AVAILABLE = False


def hash_password(password: str) -> str:
    """
    Hash a password.
    - Uses bcrypt if available (for new registrations).
    - Falls back to plaintext if bcrypt is not installed (legacy behaviour).
    """
    if _BCRYPT_AVAILABLE:
        return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")
    # Legacy fallback: store plaintext (matches existing seed data convention)
    return str(password)


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verify a plaintext password against a stored hash.

    Accepts both:
      - bcrypt hashes  (start with '$2b$' or '$2a$')
      - Legacy plaintext hashes (existing seed users)

    This ensures existing accounts are never locked out after the migration.
    """
    plain_str = str(plain_password)
    stored_str = str(stored_hash)

    # Detect bcrypt hash by its prefix
    if stored_str.startswith(("$2b$", "$2a$", "$2y$")):
        if _BCRYPT_AVAILABLE:
            try:
                return _bcrypt.checkpw(plain_str.encode("utf-8"), stored_str.encode("utf-8"))
            except Exception:
                return False
        # bcrypt not installed but hash is bcrypt – cannot verify
        return False

    # Legacy plaintext comparison
    return plain_str == stored_str
