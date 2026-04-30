import pandas as pd
from config.db_config import fetch_all

def export_attendance_to_csv(filepath, section_id=None):
    """
    Export attendance records to a CSV file using Pandas.
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
        df = pd.DataFrame(data)
        df.columns = [
            'Course Code', 'Course Name', 'Semester', 'Academic Year', 
            'Student Name', 'Session Date', 'Start Time', 'Status', 'Remarks'
        ]
        df.to_csv(filepath, index=False)
        return True, f"Successfully exported {len(data)} records."
    except Exception as e:
        return False, f"Failed to export: {e}"
