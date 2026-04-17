-- ==================================================
-- ATTENDIFY - Stored Procedures and Functions
-- ==================================================

-- 1. Procedure: mark_attendance
CREATE OR REPLACE PROCEDURE mark_attendance(
    p_session_id INT,
    p_student_id INT,
    p_status_name VARCHAR,
    p_remarks VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_status_id INT;
BEGIN
    -- Get status ID
    SELECT status_id INTO v_status_id FROM AttendanceStatus WHERE status_name = p_status_name;
    
    IF v_status_id IS NULL THEN
        RAISE EXCEPTION 'Invalid attendance status: %', p_status_name;
    END IF;

    -- Insert or Update Attendance
    INSERT INTO StudentAttendance (session_id, student_id, status_id, remarks)
    VALUES (p_session_id, p_student_id, v_status_id, p_remarks)
    ON CONFLICT (session_id, student_id) DO UPDATE 
    SET status_id = EXCLUDED.status_id,
        remarks = EXCLUDED.remarks;
END;
$$;

-- 2. Function: calculate_attendance_percentage
-- Returns percentage of classes attended (Present or Late) by a student for a specific section
CREATE OR REPLACE FUNCTION calculate_attendance_percentage(
    p_student_id INT,
    p_section_id INT
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_total_sessions INT;
    v_attended_sessions INT;
    v_percentage NUMERIC := 0.0;
BEGIN
    -- Total scheduled sessions for the section so far
    SELECT COUNT(*) INTO v_total_sessions
    FROM AttendanceSessions
    WHERE section_id = p_section_id;

    IF v_total_sessions = 0 THEN
        RETURN 0.0;
    END IF;

    -- Count sessions attended (assuming 'Present' and 'Late' count as attended)
    SELECT COUNT(*) INTO v_attended_sessions
    FROM StudentAttendance sa
    JOIN AttendanceSessions s ON sa.session_id = s.session_id
    JOIN AttendanceStatus st ON sa.status_id = st.status_id
    WHERE s.section_id = p_section_id
      AND sa.student_id = p_student_id
      AND st.status_name IN ('Present', 'Late');

    v_percentage := (v_attended_sessions::NUMERIC / v_total_sessions::NUMERIC) * 100.0;
    
    RETURN ROUND(v_percentage, 2);
END;
$$;
