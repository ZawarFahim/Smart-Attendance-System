"""
admin_service.py — Compatibility shim.
All admin-related logic lives in user_service.py.
This file re-exports every symbol required by admin_dashboard.py.
"""
from services.user_service import (
    get_all_courses,
    add_course,
    update_course,
    delete_course,
    get_all_rooms,
    add_room,
    update_room,
    delete_room,
    get_all_sections,
    add_section,
    update_section,
    delete_section,
    get_all_timetable,
    add_timetable_entry,
    update_timetable_entry,
    delete_timetable_entry,
    get_admin_overview_counts,
    get_all_departments,
    get_audit_logs,
    get_all_enrollments,
    add_enrollment,
)

__all__ = [
    "get_all_courses",
    "add_course",
    "update_course",
    "delete_course",
    "get_all_rooms",
    "add_room",
    "update_room",
    "delete_room",
    "get_all_sections",
    "add_section",
    "update_section",
    "delete_section",
    "get_all_timetable",
    "add_timetable_entry",
    "update_timetable_entry",
    "delete_timetable_entry",
    "get_admin_overview_counts",
    "get_all_departments",
    "get_audit_logs",
    "get_all_enrollments",
    "add_enrollment",
]
