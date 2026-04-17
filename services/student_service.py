"""
Student Service module to handle all database operations related to Students.
"""
from config.db_config import fetch_all, execute_query

def get_all_students():
    """Fetch all students with department and username info."""
    query = '''
        SELECT s.student_id, u.username, s.first_name, s.last_name, 
               s.enrollment_date, d.dept_name, d.dept_id
        FROM Students s
        JOIN Users u ON s.student_id = u.user_id
        LEFT JOIN Departments d ON s.dept_id = d.dept_id
    '''
    return fetch_all(query)

def get_student_by_id(student_id):
    """Fetch a single student by standard user id (student_id)."""
    query = '''
        SELECT * FROM Students WHERE student_id = %s
    '''
    result = fetch_all(query, (student_id,))
    return result[0] if result else None

def add_student(username, email, password_hash, first_name, last_name, dept_id):
    """Adds a new student by first creating a User, then a Student record."""
    user_query = '''
        INSERT INTO Users (username, email, password_hash, role)
        VALUES (%s, %s, %s, 'Student') RETURNING user_id
    '''
    # execute_query doesn't return the ID, so we need a custom fetch for RETURNING
    # Actually, we can just use execute_query if we re-fetch the user id.
    # To keep it simple, we do the insert user, then find the max userid or fetch user
    # A better approach: 
    import psycopg2
    from config.db_config import get_connection
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(user_query, (username, email, password_hash))
                user_id = cur.fetchone()[0]
                
                student_query = '''
                    INSERT INTO Students (student_id, first_name, last_name, dept_id)
                    VALUES (%s, %s, %s, %s)
                '''
                cur.execute(student_query, (user_id, first_name, last_name, dept_id))
                conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error adding student: {e}")
            return False
        finally:
            conn.close()
    return False

def update_student(student_id, first_name, last_name, dept_id):
    """Updates basic info for a student."""
    query = '''
        UPDATE Students SET first_name = %s, last_name = %s, dept_id = %s
        WHERE student_id = %s
    '''
    return execute_query(query, (first_name, last_name, dept_id, student_id))

def delete_student(student_id):
    """Deletes a student and cascade deletes from Users table."""
    query = "DELETE FROM Users WHERE user_id = %s AND role = 'Student'"
    return execute_query(query, (student_id,))
