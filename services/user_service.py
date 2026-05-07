from db import fetch_all, execute_query, get_connection

"""
Course, Room, and Section database services for Admin management.
"""

def get_admin_overview_counts():
    """Fetch high-level counts for admin overview cards."""
    query = """
        SELECT
            (SELECT COUNT(*) FROM Students) AS students_count,
            (SELECT COUNT(*) FROM Faculty) AS faculty_count,
            (SELECT COUNT(*) FROM Courses) AS courses_count,
            (SELECT COUNT(*) FROM Sections) AS sections_count,
            (SELECT COUNT(*) FROM Timetable) AS timetable_count
    """
    result = fetch_all(query)
    return result[0] if result else {}

# ─── DEPARTMENTS ─────────────────────────────────────────────────────────────

def get_all_departments():
    """Fetch all departments."""
    return fetch_all("SELECT dept_id, dept_name FROM Departments ORDER BY dept_name")

def add_department(dept_name):
    """Add a new department."""
    return execute_query("INSERT INTO Departments (dept_name) VALUES (%s)", (dept_name,))

def delete_department(dept_id):
    """Delete a department by ID."""
    return execute_query("DELETE FROM Departments WHERE dept_id = %s", (dept_id,))

# ─── COURSES ─────────────────────────────────────────────────────────────────

def get_all_courses():
    """Fetch all courses joined with their department name."""
    query = '''
        SELECT c.course_id, c.course_code, c.course_name, c.credits, d.dept_name
        FROM Courses c
        LEFT JOIN Departments d ON c.dept_id = d.dept_id
        ORDER BY c.course_code
    '''
    return fetch_all(query)

def add_course(course_code, course_name, credits, dept_id):
    """Add a new course."""
    query = "INSERT INTO Courses (course_code, course_name, credits, dept_id) VALUES (%s, %s, %s, %s)"
    return execute_query(query, (course_code, course_name, credits, dept_id))

def delete_course(course_id):
    """Delete a course."""
    return execute_query("DELETE FROM Courses WHERE course_id = %s", (course_id,))

def update_course(course_id, course_code, course_name, credits, dept_id):
    """Update an existing course."""
    query = """
        UPDATE Courses
        SET course_code = %s, course_name = %s, credits = %s, dept_id = %s
        WHERE course_id = %s
    """
    return execute_query(query, (course_code, course_name, credits, dept_id, course_id))

# ─── ROOMS ───────────────────────────────────────────────────────────────────

def get_all_rooms():
    """Fetch all rooms."""
    return fetch_all("SELECT room_id, room_name, capacity FROM Rooms ORDER BY room_name")

def add_room(room_name, capacity):
    """Add a new room."""
    return execute_query("INSERT INTO Rooms (room_name, capacity) VALUES (%s, %s)", (room_name, capacity))

def delete_room(room_id):
    """Delete a room."""
    return execute_query("DELETE FROM Rooms WHERE room_id = %s", (room_id,))

def update_room(room_id, room_name, capacity):
    """Update an existing room."""
    query = """
        UPDATE Rooms
        SET room_name = %s, capacity = %s
        WHERE room_id = %s
    """
    return execute_query(query, (room_name, capacity, room_id))

# ─── SECTIONS ────────────────────────────────────────────────────────────────

def get_all_sections():
    """Fetch all sections with full details."""
    query = '''
        SELECT s.section_id, c.course_code, c.course_name,
               f.first_name || ' ' || f.last_name AS faculty_name,
               r.room_name, s.semester, s.academic_year
        FROM Sections s
        JOIN Courses c ON s.course_id = c.course_id
        LEFT JOIN Faculty f ON s.faculty_id = f.faculty_id
        LEFT JOIN Rooms r ON s.room_id = r.room_id
        ORDER BY s.section_id
    '''
    return fetch_all(query)

def add_section(course_id, faculty_id, room_id, semester, academic_year):
    """Add a new section."""
    query = "INSERT INTO Sections (course_id, faculty_id, room_id, semester, academic_year) VALUES (%s, %s, %s, %s, %s)"
    return execute_query(query, (course_id, faculty_id, room_id, semester, academic_year))

def delete_section(section_id):
    """Delete a section."""
    return execute_query("DELETE FROM Sections WHERE section_id = %s", (section_id,))

def update_section(section_id, course_id, faculty_id, room_id, semester, academic_year):
    """Update an existing section."""
    query = """
        UPDATE Sections
        SET course_id = %s, faculty_id = %s, room_id = %s, semester = %s, academic_year = %s
        WHERE section_id = %s
    """
    return execute_query(query, (course_id, faculty_id, room_id, semester, academic_year, section_id))

# ─── TIMETABLE ───────────────────────────────────────────────────────────────

def get_all_timetable():
    """Fetch full timetable."""
    query = '''
        SELECT t.timetable_id, s.section_id, c.course_code, c.course_name,
               t.day_of_week, t.start_time, t.end_time, r.room_name
        FROM Timetable t
        JOIN Sections s ON t.section_id = s.section_id
        JOIN Courses c ON s.course_id = c.course_id
        LEFT JOIN Rooms r ON t.room_id = r.room_id
        ORDER BY t.day_of_week, t.start_time
    '''
    return fetch_all(query)

def add_timetable_entry(section_id, day_of_week, start_time, end_time, room_id):
    """Add a timetable slot."""
    query = "INSERT INTO Timetable (section_id, day_of_week, start_time, end_time, room_id) VALUES (%s, %s, %s, %s, %s)"
    return execute_query(query, (section_id, day_of_week, start_time, end_time, room_id))

def delete_timetable_entry(timetable_id):
    """Delete a timetable slot."""
    return execute_query("DELETE FROM Timetable WHERE timetable_id = %s", (timetable_id,))

def update_timetable_entry(timetable_id, section_id, day_of_week, start_time, end_time, room_id):
    """Update an existing timetable slot."""
    query = """
        UPDATE Timetable
        SET section_id = %s, day_of_week = %s, start_time = %s, end_time = %s, room_id = %s
        WHERE timetable_id = %s
    """
    return execute_query(query, (section_id, day_of_week, start_time, end_time, room_id, timetable_id))

# ─── ENROLLMENTS ─────────────────────────────────────────────────────────────

def get_all_enrollments():
    """Fetch all enrollments."""
    query = '''
        SELECT e.enrollment_id, s.first_name || ' ' || s.last_name AS student_name,
               c.course_code, c.course_name, sec.semester
        FROM Enrollments e
        JOIN Students s ON e.student_id = s.student_id
        JOIN Sections sec ON e.section_id = sec.section_id
        JOIN Courses c ON sec.course_id = c.course_id
        ORDER BY e.enrollment_id
    '''
    return fetch_all(query)

def add_enrollment(student_id, section_id):
    """
    Enroll a student in a section.
    Uses the stored procedure enroll_student_in_section so that
    prerequisite validation and uniqueness are enforced at the DB level.
    """
    query = "CALL enroll_student_in_section(%s, %s)"
    return execute_query(query, (student_id, section_id))

def delete_enrollment(enrollment_id):
    """Remove an enrollment."""
    return execute_query("DELETE FROM Enrollments WHERE enrollment_id = %s", (enrollment_id,))


def get_eligible_sections_for_student(student_id: int):
    """
    Helper to fetch sections the student is eligible to enroll in,
    backed by the eligible_sections_for_student view.
    """
    query = """
        SELECT *
        FROM eligible_sections_for_student
        WHERE student_id = %s
        ORDER BY course_code, semester, academic_year
    """
    return fetch_all(query, (student_id,))

# ─── AUDIT LOGS ──────────────────────────────────────────────────────────────

def get_audit_logs():
    """Fetch audit logs with username."""
    query = '''
        SELECT a.log_id, COALESCE(u.username, 'System') AS username,
               a.action, a.table_name, a.record_id, a.timestamp
        FROM AuditLogs a
        LEFT JOIN Users u ON a.user_id = u.user_id
        ORDER BY a.timestamp DESC
        LIMIT 200
    '''
    return fetch_all(query)


"""
Faculty Service module to handle database operations related to Faculty.
"""

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
    from db import get_connection
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


"""
Student Service module to handle all database operations related to Students.
"""

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
    from db import get_connection
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


"""
Department service to handle database queries related to Departments.
"""

def get_all_departments():
    """Fetch all departments."""
    query = "SELECT dept_id, dept_name FROM Departments ORDER BY dept_name"
    return fetch_all(query)


from db import fetch_all, execute_query, get_connection

"""
Leave request service module.
Handles submit/view/review workflows for all roles.
"""


def create_leave_request(user_id, start_date, end_date, reason):
    """Create a leave request for a user."""
    query = """
        INSERT INTO LeaveRequests (user_id, start_date, end_date, reason)
        VALUES (%s, %s, %s, %s)
    """
    return execute_query(query, (user_id, start_date, end_date, reason))


def get_leave_requests_for_user(user_id):
    """Fetch leave requests submitted by a user."""
    query = """
        SELECT leave_id, start_date, end_date, reason, status, reviewed_by, created_at
        FROM LeaveRequests
        WHERE user_id = %s
        ORDER BY created_at DESC
    """
    return fetch_all(query, (user_id,))


def get_all_leave_requests():
    """Fetch all leave requests with requester and reviewer usernames."""
    query = """
        SELECT
            lr.leave_id,
            lr.user_id AS requester_user_id,
            requester.username AS requester_username,
            requester.role AS requester_role,
            lr.start_date,
            lr.end_date,
            lr.reason,
            lr.status,
            COALESCE(reviewer.username, '-') AS reviewed_by,
            lr.created_at
        FROM LeaveRequests lr
        JOIN Users requester ON lr.user_id = requester.user_id
        LEFT JOIN Users reviewer ON lr.reviewed_by = reviewer.user_id
        ORDER BY
            CASE lr.status
                WHEN 'Pending' THEN 1
                WHEN 'Approved' THEN 2
                ELSE 3
            END,
            lr.created_at DESC
    """
    return fetch_all(query)


def review_leave_request(leave_id, status, reviewed_by):
    """Approve or reject a pending leave request."""
    query = """
        UPDATE LeaveRequests
        SET status = %s, reviewed_by = %s
        WHERE leave_id = %s
    """
    return execute_query(query, (status, reviewed_by, leave_id))


"""
Notification logic implementation.
"""

def get_notifications(user_id):
    query = "SELECT notification_id, message, is_read, created_at FROM Notifications WHERE user_id = %s ORDER BY created_at DESC"
    return fetch_all(query, (user_id,))

def mark_as_read(notification_id):
    query = "UPDATE Notifications SET is_read = TRUE WHERE notification_id = %s"
    return execute_query(query, (notification_id,))

def create_notification(user_id, message):
    query = "INSERT INTO Notifications (user_id, message) VALUES (%s, %s)"
    return execute_query(query, (user_id, message))

def broadcast_notification(role, message):
    """
    Send a notification to all users of a specific role, or all users if role is 'All'.
    """
    if role == 'All':
        query = "INSERT INTO Notifications (user_id, message) SELECT user_id, %s FROM Users"
        params = (message,)
    else:
        query = "INSERT INTO Notifications (user_id, message) SELECT user_id, %s FROM Users WHERE role = %s"
        params = (message, role)
    return execute_query(query, params)


