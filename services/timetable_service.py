"""
Timetable Service module.
"""
from db import fetch_all, execute_query

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
    '''
    return fetch_all(query, (faculty_id,))

def check_timetable_clash(room_id: int, faculty_id: int, day_of_week: str, start_time: str, end_time: str, semester: str, academic_year: str) -> dict:
    """
    Checks for room or faculty clashes for a given time slot.
    Returns a dictionary with 'has_clash' (bool) and 'reason' (str).
    """
    # Check Room Clash
    room_query = '''
        SELECT t.timetable_id 
        FROM Timetable t
        JOIN Sections s ON t.section_id = s.section_id
        WHERE t.room_id = %s AND t.day_of_week = %s 
          AND s.semester = %s AND s.academic_year = %s
          AND (t.start_time < %s AND t.end_time > %s)
    '''
    room_clash = fetch_all(room_query, (room_id, day_of_week, semester, academic_year, end_time, start_time))
    
    if room_clash:
        return {'has_clash': True, 'reason': 'Room is already occupied during this time slot.'}
        
    # Check Faculty Clash
    faculty_query = '''
        SELECT t.timetable_id 
        FROM Timetable t
        JOIN Sections s ON t.section_id = s.section_id
        WHERE s.faculty_id = %s AND t.day_of_week = %s 
          AND s.semester = %s AND s.academic_year = %s
          AND (t.start_time < %s AND t.end_time > %s)
    '''
    faculty_clash = fetch_all(faculty_query, (faculty_id, day_of_week, semester, academic_year, end_time, start_time))
    
    if faculty_clash:
        return {'has_clash': True, 'reason': 'Faculty is already teaching another section during this time slot.'}
        
    return {'has_clash': False, 'reason': ''}

def get_timetable_by_semester(semester: str, academic_year: str):
    """Fetch timetable for a specific semester."""
    query = '''
        SELECT s.section_id, c.course_code, t.day_of_week, t.start_time, t.end_time, r.room_name
        FROM Timetable t
        JOIN Sections s ON t.section_id = s.section_id
        JOIN Courses c ON s.course_id = c.course_id
        LEFT JOIN Rooms r ON t.room_id = r.room_id
        WHERE s.semester = %s AND s.academic_year = %s
        ORDER BY t.day_of_week, t.start_time
    '''
    return fetch_all(query, (semester, academic_year))
