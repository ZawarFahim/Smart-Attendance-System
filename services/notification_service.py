"""
notification_service.py — Compatibility shim.
All notification logic lives in user_service.py.
"""
from services.user_service import (
    get_notifications,
    mark_as_read,
    create_notification,
    broadcast_notification,
)

__all__ = [
    "get_notifications",
    "mark_as_read",
    "create_notification",
    "broadcast_notification",
]
