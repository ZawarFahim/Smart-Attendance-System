"""
faculty_service.py — Compatibility shim.
All faculty-related logic lives in user_service.py.
This file re-exports the necessary symbols so that any module that does
    from services.faculty_service import get_all_faculty
continues to work without modification.
"""
from services.user_service import (
    get_all_faculty,
    add_faculty,
    delete_faculty,
)

__all__ = [
    "get_all_faculty",
    "add_faculty",
    "delete_faculty",
]
