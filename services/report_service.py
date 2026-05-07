"""
Report Service module to fetch aggregated data.
"""
from db import fetch_all

def get_full_attendance_report():
    """Fetches the complete student attendance report using standard SQL."""
    query = "SELECT * FROM student_attendance_report"
    return fetch_all(query)

def get_low_attendance():
    """Fetches students with critically low attendance (< 75%)."""
    query = "SELECT * FROM low_attendance_students"
    return fetch_all(query)

def get_course_report(course_code):
    """Filter report by specific course code."""
    query = "SELECT * FROM student_attendance_report WHERE course_code = %s"
    return fetch_all(query, (course_code,))

def get_faculty_workload_report():
    """Fetches faculty workload with ranking using window functions."""
    query = "SELECT * FROM faculty_workload_report"
    return fetch_all(query)


def get_faculty_workload_semester_summary():
    """Fetches semester-based workload summary per faculty."""
    query = "SELECT * FROM faculty_workload_semester_summary"
    return fetch_all(query)


def get_faculty_monthly_sessions():
    """Fetches monthly class sessions per faculty."""
    query = "SELECT * FROM faculty_monthly_class_sessions_summary"
    return fetch_all(query)

def get_department_ranking():
    """Fetches department attendance ranking using window functions."""
    query = "SELECT * FROM department_attendance_ranking"
    return fetch_all(query)

def get_student_trends():
    """Fetches student attendance trends using window functions (LAG)."""
    query = "SELECT * FROM student_attendance_trends LIMIT 100"
    return fetch_all(query)
from db import fetch_all, execute_query, get_connection


def get_overall_attendance_stats():
    """
    Fetch the total count of each attendance status across all records.
    Returns a list of dicts: [{'status_name': 'Present', 'count': 150}, ...]
    """
    query = """
        SELECT 
            ast.status_name, 
            COUNT(sa.attendance_id) as count
        FROM StudentAttendance sa
        JOIN AttendanceStatus ast ON sa.status_id = ast.status_id
        GROUP BY ast.status_name
    """
    return fetch_all(query)

def get_department_attendance_rates():
    """
    Fetch the percentage of 'Present' attendance records per department.
    Returns a list of dicts: [{'dept_name': 'Computer Science', 'present_rate': 85.5}, ...]
    """
    query = """
        SELECT 
            d.dept_name,
            ROUND(
                (COUNT(CASE WHEN ast.status_name = 'Present' THEN 1 END)::numeric / 
                NULLIF(COUNT(sa.attendance_id), 0)) * 100, 2
            ) as present_rate
        FROM Departments d
        JOIN Students s ON d.dept_id = s.dept_id
        JOIN StudentAttendance sa ON s.student_id = sa.student_id
        JOIN AttendanceStatus ast ON sa.status_id = ast.status_id
        GROUP BY d.dept_name
        HAVING COUNT(sa.attendance_id) > 0
    """
    return fetch_all(query)


# ─── PREREQUISITE / ENROLLMENT REPORTS ────────────────────────────────────────

def get_course_prerequisite_map():
    """Return mapping of courses to their prerequisite courses."""
    query = "SELECT * FROM course_prerequisite_map ORDER BY course_code, prereq_course_code"
    return fetch_all(query)


def get_student_prerequisite_status(student_id: int):
    """Return prerequisite completion/eligibility per course for a given student."""
    query = """
        SELECT *
        FROM student_course_prerequisite_status
        WHERE student_id = %s
        ORDER BY course_code
    """
    return fetch_all(query, (student_id,))


def get_eligible_sections_for_student(student_id: int):
    """Return sections the student is currently eligible to enroll in."""
    query = """
        SELECT *
        FROM eligible_sections_for_student
        WHERE student_id = %s
        ORDER BY course_code, semester, academic_year
    """
    return fetch_all(query, (student_id,))


def get_blocked_enrollments_for_student(student_id: int):
    """Return sections blocked by unmet prerequisites for a given student."""
    query = """
        SELECT *
        FROM blocked_enrollments_for_student
        WHERE student_id = %s
        ORDER BY course_code, semester, academic_year
    """
    return fetch_all(query, (student_id,))


import csv

def export_attendance_to_csv(filepath, section_id=None):
    """
    Export attendance records to a CSV file using standard csv module.
    If section_id is provided, filters the records for that section.
    """
    query = """
        SELECT 
            c.course_code,
            c.course_name,
            sec.semester,
            sec.academic_year,
            s.first_name || ' ' || s.last_name as student_name,
            sess.session_date,
            sess.start_time,
            ast.status_name,
            sa.remarks
        FROM StudentAttendance sa
        JOIN Students s ON sa.student_id = s.student_id
        JOIN AttendanceSessions sess ON sa.session_id = sess.session_id
        JOIN Sections sec ON sess.section_id = sec.section_id
        JOIN Courses c ON sec.course_id = c.course_id
        JOIN AttendanceStatus ast ON sa.status_id = ast.status_id
    """
    
    params = ()
    if section_id:
        query += " WHERE sec.section_id = %s"
        params = (section_id,)
        
    query += " ORDER BY sess.session_date DESC, s.last_name ASC"
    
    data = fetch_all(query, params)
    
    if not data:
        return False, "No attendance records found to export."
        
    try:
        import csv
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Course Code', 'Course Name', 'Semester', 'Academic Year', 
                'Student Name', 'Session Date', 'Start Time', 'Status', 'Remarks'
            ])
            for row in data:
                writer.writerow([
                    row['course_code'], row['course_name'], row['semester'], row['academic_year'],
                    row['student_name'], row['session_date'], row['start_time'], row['status_name'], row['remarks']
                ])
        return True, f"Successfully exported {len(data)} records."
    except Exception as e:
        return False, f"Failed to export: {e}"


