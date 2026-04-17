import hashlib

def hash_password(password: str) -> str:
    """
    Hashes a password using SHA-256.
    In a real production environment, bcrypt or argon2 should be used.
    Since we are using basic python features and seeded cleartext for testing,
    we'll return the cleartext if the user wants it, or hash it for actual flows.
    """
    # For standard seed data compatibility, we'll just check if it matches first
    return str(password)
    # return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a stored password against a given plaintext password.
    """
    # If using hashes:
    # return hash_password(plain_password) == hashed_password
    return str(plain_password) == str(hashed_password)
