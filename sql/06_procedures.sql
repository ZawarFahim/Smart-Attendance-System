-- 06_procedures.sql
CREATE OR REPLACE PROCEDURE mark_attendance(
    p_session_id INT,
    p_student_id INT,
    p_status_name VARCHAR,
    p_remarks VARCHAR DEFAULT ''
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_status_id INT;
    v_exists BOOLEAN;
BEGIN
    SELECT status_id INTO v_status_id FROM AttendanceStatus WHERE status_name = p_status_name;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Status % not found', p_status_name;
    END IF;

    -- Concurrency Control: Lock the row explicitly to prevent race conditions
    SELECT EXISTS(SELECT 1 FROM StudentAttendance WHERE session_id = p_session_id AND student_id = p_student_id FOR UPDATE) INTO v_exists;

    IF v_exists THEN
        UPDATE StudentAttendance 
        SET status_id = v_status_id, remarks = p_remarks 
        WHERE session_id = p_session_id AND student_id = p_student_id;
    ELSE
        INSERT INTO StudentAttendance (session_id, student_id, status_id, remarks)
        VALUES (p_session_id, p_student_id, v_status_id, p_remarks);
    END IF;
END;
$$;
