"""
Department service to handle database queries related to Departments.
"""
from config.db_config import fetch_all

def get_all_departments():
    """Fetch all departments."""
    query = "SELECT dept_id, dept_name FROM Departments ORDER BY dept_name"
    return fetch_all(query)
