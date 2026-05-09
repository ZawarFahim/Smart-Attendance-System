"""
student_service.py — Compatibility shim.
All student-related logic lives in user_service.py.
This file re-exports the necessary symbols so that any module that does
    from services.student_service import get_all_students
continues to work without modification.
"""
from services.user_service import (
    get_all_students,
    get_student_by_id,
    add_student,
    update_student,
    delete_student,
)

__all__ = [
    "get_all_students",
    "get_student_by_id",
    "add_student",
    "update_student",
    "delete_student",
]
