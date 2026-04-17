"""
Timetable Service module.
"""
from config.db_config import fetch_all, execute_query

def get_timetable_for_section(section_id):
    query = '''
        SELECT t.day_of_week, t.start_time, t.end_time, r.room_name
        FROM Timetable t
        LEFT JOIN Rooms r ON t.room_id = r.room_id
        WHERE t.section_id = %s
        ORDER BY t.day_of_week, t.start_time
    '''
    return fetch_all(query, (section_id,))

def get_timetable_for_student(student_id):
    """Fetches all timetables for sections the student is enrolled in."""
    query = '''
        SELECT c.course_code, t.day_of_week, t.start_time, t.end_time, r.room_name
        FROM Timetable t
        JOIN Sections s ON t.section_id = s.section_id
        JOIN Courses c ON s.course_id = c.course_id
        LEFT JOIN Rooms r ON t.room_id = r.room_id
        JOIN Enrollments e ON s.section_id = e.section_id
        WHERE e.student_id = %s
    '''
    return fetch_all(query, (student_id,))

def get_timetable_for_faculty(faculty_id):
    """Fetch timetable rows for faculty-assigned sections."""
    query = '''
        SELECT s.section_id, c.course_code, c.course_name,
               t.day_of_week, t.start_time, t.end_time, r.room_name
        FROM Timetable t
        JOIN Sections s ON t.section_id = s.section_id
        JOIN Courses c ON s.course_id = c.course_id
        LEFT JOIN Rooms r ON t.room_id = r.room_id
        WHERE s.faculty_id = %s
        ORDER BY t.day_of_week, t.start_time
    '''
    return fetch_all(query, (faculty_id,))
