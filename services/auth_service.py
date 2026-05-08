"""
Auth service.
"""
from db import fetch_all, execute_query
from utils.helpers import verify_password, hash_password

def authenticate(login_id, provided_password):
    """Verifies user credentials by email or username and returns user details if valid.
    
    Returned dict keys:
        user_id, username, role, password_hash, display_name
    display_name is fetched from Students.name / Faculty.name if available,
    otherwise falls back to first_name+last_name, then username.
    """
    query = "SELECT user_id, username, role, password_hash FROM Users WHERE email = %s OR username = %s"
    result = fetch_all(query, (login_id, login_id))
    
    if result:
        user = dict(result[0])
        if verify_password(provided_password, user['password_hash']):
            # Fetch display name based on role
            display_name = user['username']  # safe default
            role = user.get('role', '')
            if role == 'Student':
                name_result = fetch_all(
                    "SELECT name, first_name, last_name FROM Students WHERE student_id = %s",
                    (user['user_id'],)
                )
                if name_result:
                    r = name_result[0]
                    if r.get('name'):
                        display_name = r['name']
                    elif r.get('first_name'):
                        display_name = f"{r['first_name']} {r.get('last_name', '')}".strip()
            elif role == 'Faculty':
                name_result = fetch_all(
                    "SELECT name, first_name, last_name FROM Faculty WHERE faculty_id = %s",
                    (user['user_id'],)
                )
                if name_result:
                    r = name_result[0]
                    if r.get('name'):
                        display_name = r['name']
                    elif r.get('first_name'):
                        display_name = f"{r['first_name']} {r.get('last_name', '')}".strip()
            user['display_name'] = display_name
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
