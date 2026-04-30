from config.db_config import fetch_all

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
