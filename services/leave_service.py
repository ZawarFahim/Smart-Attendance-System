"""
Leave request service module.
Handles submit/view/review workflows for all roles.
"""
from config.db_config import fetch_all, execute_query


def create_leave_request(user_id, start_date, end_date, reason):
    """Create a leave request for a user."""
    query = """
        INSERT INTO LeaveRequests (user_id, start_date, end_date, reason)
        VALUES (%s, %s, %s, %s)
    """
    return execute_query(query, (user_id, start_date, end_date, reason))


def get_leave_requests_for_user(user_id):
    """Fetch leave requests submitted by a user."""
    query = """
        SELECT leave_id, start_date, end_date, reason, status, reviewed_by, created_at
        FROM LeaveRequests
        WHERE user_id = %s
        ORDER BY created_at DESC
    """
    return fetch_all(query, (user_id,))


def get_all_leave_requests():
    """Fetch all leave requests with requester and reviewer usernames."""
    query = """
        SELECT
            lr.leave_id,
            lr.user_id AS requester_user_id,
            requester.username AS requester_username,
            requester.role AS requester_role,
            lr.start_date,
            lr.end_date,
            lr.reason,
            lr.status,
            COALESCE(reviewer.username, '-') AS reviewed_by,
            lr.created_at
        FROM LeaveRequests lr
        JOIN Users requester ON lr.user_id = requester.user_id
        LEFT JOIN Users reviewer ON lr.reviewed_by = reviewer.user_id
        ORDER BY
            CASE lr.status
                WHEN 'Pending' THEN 1
                WHEN 'Approved' THEN 2
                ELSE 3
            END,
            lr.created_at DESC
    """
    return fetch_all(query)


def review_leave_request(leave_id, status, reviewed_by):
    """Approve or reject a pending leave request."""
    query = """
        UPDATE LeaveRequests
        SET status = %s, reviewed_by = %s
        WHERE leave_id = %s
    """
    return execute_query(query, (status, reviewed_by, leave_id))
