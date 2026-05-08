# ==================================================
# ATTENDIFY - Global Settings
# ==================================================

APP_NAME = "ATTENDIFY - Smart Attendance Management System"
VERSION = "1.0.0"

# Theme Colors
COLORS = {
    "primary": "#2C3E50",     # Dark Blue/Grey
    "secondary": "#18BC9C",   # Teal/Green
    "accent": "#E74C3C",      # Red
    "background": "#F5F7FA",  # Light Grey
    "text_dark": "#2C3E50",
    "text_light": "#FFFFFF",
    "danger": "#E74C3C",
    "success": "#2ECC71",
    "warning": "#F1C40F"
}

# Fonts
FONTS = {
    "h1": ("Arial", 24, "bold"),
    "h2": ("Arial", 18, "bold"),
    "body": ("Arial", 12),
    "body_bold": ("Arial", 12, "bold"),
    "small": ("Arial", 10)
}

# Window Dimensions
WINDOW_GEOMETRY = "1024x768"

# ==================================================
# Excel Bulk Import Configuration
# ==================================================
# Set this to the absolute or relative path of the Excel file
# containing student records to import.
# The admin can also override this from the UI at runtime.
# Expected Excel columns:
#   Column B (index 1) → reg_no
#   Column C (index 2) → name
#   Column E (index 4) → email (auto-generated from reg_no if empty)
EXCEL_IMPORT_PATH = ""  # e.g. "C:/data/students.xlsx" or leave blank to use UI picker
