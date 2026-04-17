"""
Report Service module to fetch aggregated data.
"""
from config.db_config import fetch_all

def get_full_attendance_report():
    """Fetches the complete student attendance report using the view."""
    query = "SELECT * FROM student_attendance_report"
    return fetch_all(query)

def get_low_attendance():
    """Fetches students with critically low attendance."""
    query = "SELECT * FROM low_attendance_students"
    return fetch_all(query)

def get_course_report(course_code):
    """Filter report by specific course code."""
    query = "SELECT * FROM student_attendance_report WHERE course_code = %s"
    return fetch_all(query, (course_code,))
