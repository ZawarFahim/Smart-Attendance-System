"""
Main application entrypoint.
"""
import sys
import tkinter as tk
from tkinter import messagebox
from gui.login_window import LoginWindow
from gui.admin.admin_dashboard import AdminDashboard
from gui.faculty.faculty_dashboard import FacultyDashboard
from gui.student.student_dashboard import StudentDashboard
from config.db_config import get_connection

def check_db_connection():
    """Validates the PostgreSQL connection at startup."""
    conn = get_connection()
    if conn:
        conn.close()
        return True
    return False

def show_dashboard(user_info):
    """Callback to switch from Login Window to respective Dashboard."""
    role = user_info.get('role')
    
    if role == 'Admin':
        app = AdminDashboard(user_info, on_logout=main)
    elif role == 'Faculty':
        app = FacultyDashboard(user_info, on_logout=main)
    elif role == 'Student':
        app = StudentDashboard(user_info, on_logout=main)
    else:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Role Error", "Undefined User Role.")
        sys.exit(1)
        
    app.mainloop()

def main():
    """Initializes the database connection and launches the Login Window."""
    if not check_db_connection():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Database Error", "Failed to connect to the PostgreSQL database.\nPlease check your database.ini parameters and ensure Postgres is running.")
        sys.exit(1)

    login_app = LoginWindow(on_login_success=show_dashboard)
    login_app.mainloop()

if __name__ == "__main__":
    main()
