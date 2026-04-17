-- ==================================================
-- ATTENDIFY - Triggers
-- ==================================================

-- 1. Trigger: Prevent Duplicate Attendance
-- Returns NULL to silently skip duplicate inserts so that ON CONFLICT DO NOTHING
-- works without aborting the transaction. The UNIQUE(session_id, student_id)
-- constraint on StudentAttendance remains the hard enforcement.
CREATE OR REPLACE FUNCTION check_duplicate_attendance()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM StudentAttendance 
        WHERE session_id = NEW.session_id AND student_id = NEW.student_id
    ) THEN
        RETURN NULL; -- skip insert instead of raising exception
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_duplicate_attendance_trg
BEFORE INSERT ON StudentAttendance
FOR EACH ROW
EXECUTE FUNCTION check_duplicate_attendance();


-- 2. Trigger: Audit log for Users table
CREATE OR REPLACE FUNCTION log_user_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO AuditLogs (user_id, action, table_name, record_id)
        VALUES (NULL, 'INSERT', 'Users', NEW.user_id);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO AuditLogs (user_id, action, table_name, record_id)
        VALUES (NULL, 'UPDATE', 'Users', NEW.user_id);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO AuditLogs (user_id, action, table_name, record_id)
        VALUES (NULL, 'DELETE', 'Users', OLD.user_id);
        RETURN OLD;
    END IF;
    RETURN NULL;
EXCEPTION
    WHEN OTHERS THEN
        -- If context fails, just insert NULL for user_id
        INSERT INTO AuditLogs (user_id, action, table_name, record_id)
        VALUES (NULL, TG_OP, 'Users', COALESCE(NEW.user_id, OLD.user_id));
        RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_users_changes
AFTER INSERT OR UPDATE OR DELETE ON Users
FOR EACH ROW
EXECUTE FUNCTION log_user_changes();
