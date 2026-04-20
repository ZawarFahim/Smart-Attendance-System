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

-- ==================================================
-- 3. Procedure: notify_low_attendance_students
-- Demonstrates: CURSOR, OPEN / FETCH / CLOSE, LOOP, EXIT WHEN NOT FOUND
-- Iterates row-by-row over every student whose attendance < 75%
-- and inserts a personalised warning Notification for each one.
-- ==================================================
CREATE OR REPLACE PROCEDURE notify_low_attendance_students()
LANGUAGE plpgsql
AS $$
DECLARE
    -- Cursor iterates over the low_attendance_students view
    cur_low CURSOR FOR
        SELECT student_id,
               username,
               first_name,
               last_name,
               course_name,
               attendance_percentage
        FROM   low_attendance_students;

    rec         RECORD;   -- holds one fetched row at a time
    v_msg       TEXT;
BEGIN
    OPEN cur_low;

    LOOP
        FETCH cur_low INTO rec;
        EXIT WHEN NOT FOUND;          -- exit loop when no more rows

        -- Build a personalised warning message
        v_msg := format(
            'Attendance Alert: Dear %s %s, your attendance in "%s" is %.2f%% — below the required 75%%. Please attend classes regularly.',
            rec.first_name,
            rec.last_name,
            rec.course_name,
            rec.attendance_percentage
        );

        -- Insert notification; skip silently if identical message already exists
        INSERT INTO Notifications (user_id, message, is_read)
        VALUES (rec.student_id, v_msg, FALSE)
        ON CONFLICT DO NOTHING;

        RAISE NOTICE 'Notified student % (id=%) — %.2f%%',
            rec.username, rec.student_id, rec.attendance_percentage;
    END LOOP;

    CLOSE cur_low;
END;
$$;
