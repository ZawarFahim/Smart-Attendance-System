"""
Faculty Service module to handle database operations related to Faculty.
"""
from config.db_config import fetch_all, execute_query

def get_all_faculty():
    query = '''
        SELECT f.faculty_id, u.username, f.first_name, f.last_name, 
               f.hire_date, d.dept_name
        FROM Faculty f
        JOIN Users u ON f.faculty_id = u.user_id
        LEFT JOIN Departments d ON f.dept_id = d.dept_id
    '''
    return fetch_all(query)

def add_faculty(username, email, password_hash, first_name, last_name, dept_id):
    """Adds a new faculty by inserting into Users then Faculty."""
    user_query = '''
        INSERT INTO Users (username, email, password_hash, role)
        VALUES (%s, %s, %s, 'Faculty') RETURNING user_id
    '''
    import psycopg2
    from config.db_config import get_connection
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(user_query, (username, email, password_hash))
                user_id = cur.fetchone()[0]
                
                faculty_query = '''
                    INSERT INTO Faculty (faculty_id, first_name, last_name, dept_id)
                    VALUES (%s, %s, %s, %s)
                '''
                cur.execute(faculty_query, (user_id, first_name, last_name, dept_id))
                conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error adding faculty: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_faculty(faculty_id):
    """Deletes faculty via cascade on user delete."""
    query = "DELETE FROM Users WHERE user_id = %s AND role = 'Faculty'"
    return execute_query(query, (faculty_id,))
