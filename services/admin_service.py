"""
Course, Room, and Section database services for Admin management.
"""
from config.db_config import fetch_all, execute_query, get_connection

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
    """Enroll a student in a section."""
    return execute_query("INSERT INTO Enrollments (student_id, section_id) VALUES (%s, %s)", (student_id, section_id))

def delete_enrollment(enrollment_id):
    """Remove an enrollment."""
    return execute_query("DELETE FROM Enrollments WHERE enrollment_id = %s", (enrollment_id,))

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
