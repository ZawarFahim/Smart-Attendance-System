"""
Auth service.
"""
from config.db_config import fetch_all, execute_query
from utils.auth import verify_password, hash_password

def authenticate(login_id, provided_password):
    """Verifies user credentials by email or username and returns user details if valid."""
    query = "SELECT user_id, username, role, password_hash FROM Users WHERE email = %s OR username = %s"
    result = fetch_all(query, (login_id, login_id))
    
    if result:
        user = result[0]
        if verify_password(provided_password, user['password_hash']):
            return user
    return None

def change_password(user_id, new_password):
    """Updates the password for a specific user ID."""
    hashed_pw = hash_password(new_password)
    query = "UPDATE Users SET password_hash = %s WHERE user_id = %s"
    return execute_query(query, (hashed_pw, user_id))

def verify_current_password(user_id, provided_password):
    """Checks whether provided password matches current user password hash."""
    query = "SELECT password_hash FROM Users WHERE user_id = %s"
    result = fetch_all(query, (user_id,))
    if not result:
        return False
    return verify_password(provided_password, result[0]['password_hash'])
