"""
leave_service.py — Compatibility shim.
All leave-request logic lives in user_service.py.
"""
from services.user_service import (
    create_leave_request,
    get_leave_requests_for_user,
    get_all_leave_requests,
    review_leave_request,
)

__all__ = [
    "create_leave_request",
    "get_leave_requests_for_user",
    "get_all_leave_requests",
    "review_leave_request",
]
