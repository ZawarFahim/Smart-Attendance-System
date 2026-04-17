"""
Notification logic implementation.
"""
from config.db_config import fetch_all, execute_query

def get_notifications(user_id):
    query = "SELECT notification_id, message, is_read, created_at FROM Notifications WHERE user_id = %s ORDER BY created_at DESC"
    return fetch_all(query, (user_id,))

def mark_as_read(notification_id):
    query = "UPDATE Notifications SET is_read = TRUE WHERE notification_id = %s"
    return execute_query(query, (notification_id,))

def create_notification(user_id, message):
    query = "INSERT INTO Notifications (user_id, message) VALUES (%s, %s)"
    return execute_query(query, (user_id, message))
