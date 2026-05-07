-- 07_functions.sql
CREATE OR REPLACE FUNCTION calculate_attendance_percentage(p_student_id INT, p_section_id INT)
RETURNS FLOAT AS $$
DECLARE
    v_total_sessions INT;
    v_attended INT;
    v_percentage FLOAT;
BEGIN
    SELECT COUNT(sa.attendance_id) INTO v_total_sessions
    FROM AttendanceSessions s
    JOIN StudentAttendance sa ON s.session_id = sa.session_id
    WHERE sa.student_id = p_student_id AND s.section_id = p_section_id;

    IF v_total_sessions = 0 THEN
        RETURN 0.0;
    END IF;

    SELECT COUNT(sa.attendance_id) INTO v_attended
    FROM AttendanceSessions s
    JOIN StudentAttendance sa ON s.session_id = sa.session_id
    JOIN AttendanceStatus st ON sa.status_id = st.status_id
    WHERE sa.student_id = p_student_id AND s.section_id = p_section_id
    AND st.status_name IN ('Present', 'Late');

    v_percentage := (v_attended::FLOAT / v_total_sessions) * 100.0;
    RETURN v_percentage;
END;
$$ LANGUAGE plpgsql;
