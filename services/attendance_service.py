"""
Attendance Service module to handle all attendance related logic.
"""
from config.db_config import fetch_all, execute_query

def get_assigned_sections(faculty_id):
    """Fetch sections assigned to a specific faculty member."""
    query = '''
        SELECT s.section_id, c.course_code, c.course_name, s.semester, s.academic_year
        FROM Sections s
        JOIN Courses c ON s.course_id = c.course_id
        WHERE s.faculty_id = %s
    '''
    return fetch_all(query, (faculty_id,))

def create_session(section_id, session_date, start_time, end_time, created_by):
    """Create a new attendance session for a class."""
    query = '''
        INSERT INTO AttendanceSessions (section_id, session_date, start_time, end_time, created_by)
        VALUES (%s, %s, %s, %s, %s) RETURNING session_id
    '''
    # We need the returning session id
    import psycopg2
    from config.db_config import get_connection
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query, (section_id, session_date, start_time, end_time, created_by))
                session_id = cur.fetchone()[0]
                conn.commit()
                return session_id
        except Exception as e:
            conn.rollback()
            print(f"Error creating session: {e}")
            return None
        finally:
            conn.close()
    return None

def get_students_for_section(section_id):
    """Fetch all students enrolled in a section."""
    query = '''
        SELECT e.student_id, s.first_name, s.last_name 
        FROM Enrollments e
        JOIN Students s ON e.student_id = s.student_id
        WHERE e.section_id = %s
    '''
    return fetch_all(query, (section_id,))

def submit_attendance(session_id, student_id, status_name, remarks=""):
    """
    Submits attendance calling the DB stored procedure.
    mark_attendance(p_session_id, p_student_id, p_status_name, p_remarks)
    """
    query = "CALL mark_attendance(%s, %s, %s, %s)"
    return execute_query(query, (session_id, student_id, status_name, remarks))

def get_attendance_history(student_id):
    """Get the full log of attendance for a student."""
    query = '''
        SELECT sess.session_date, c.course_code, c.course_name, st.status_name
        FROM StudentAttendance sa
        JOIN AttendanceSessions sess ON sa.session_id = sess.session_id
        JOIN Sections sec ON sess.section_id = sec.section_id
        JOIN Courses c ON sec.course_id = c.course_id
        JOIN AttendanceStatus st ON sa.status_id = st.status_id
        WHERE sa.student_id = %s
        ORDER BY sess.session_date DESC
    '''
    return fetch_all(query, (student_id,))

def get_student_overall_attendance(student_id, section_id):
    """Gets the percentage via the Postgres function created."""
    query = "SELECT calculate_attendance_percentage(%s, %s) AS percentage"
    result = fetch_all(query, (student_id, section_id))
    return result[0]['percentage'] if result else 0.0

def get_student_sections(student_id):
    """Fetch sections enrolled by a student."""
    query = """
        SELECT s.section_id, c.course_code, c.course_name, s.semester, s.academic_year
        FROM Enrollments e
        JOIN Sections s ON e.section_id = s.section_id
        JOIN Courses c ON s.course_id = c.course_id
        WHERE e.student_id = %s
        ORDER BY c.course_code
    """
    return fetch_all(query, (student_id,))

def get_student_attendance_summary(student_id):
    """Fetch attendance percentage for each enrolled section."""
    query = """
        SELECT
            sec.section_id,
            c.course_code,
            c.course_name,
            ROUND(calculate_attendance_percentage(%s, sec.section_id)::numeric, 2) AS attendance_percentage
        FROM Enrollments e
        JOIN Sections sec ON e.section_id = sec.section_id
        JOIN Courses c ON sec.course_id = c.course_id
        WHERE e.student_id = %s
        ORDER BY c.course_code
    """
    return fetch_all(query, (student_id, student_id))

def get_faculty_session_history(faculty_id):
    """Fetch faculty-created attendance sessions."""
    query = """
        SELECT
            sess.session_id,
            sess.session_date,
            sess.start_time,
            sess.end_time,
            sec.section_id,
            c.course_code,
            c.course_name
        FROM AttendanceSessions sess
        JOIN Sections sec ON sess.section_id = sec.section_id
        JOIN Courses c ON sec.course_id = c.course_id
        WHERE sess.created_by = %s
        ORDER BY sess.session_date DESC, sess.start_time DESC
        LIMIT 100
    """
    return fetch_all(query, (faculty_id,))
