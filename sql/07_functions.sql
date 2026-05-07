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

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 1: ELIGIBILITY CHECK FUNCTION (used in ad‑hoc queries / demos)
-- Demonstrates subqueries and EXISTS / NOT EXISTS.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION is_student_eligible_for_course(
    p_student_id INT,
    p_course_id INT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_missing_count INT;
BEGIN
    SELECT COUNT(*) INTO v_missing_count
    FROM CoursePrerequisites p
    LEFT JOIN StudentCourseResults scr
        ON scr.student_id = p_student_id
       AND scr.course_id = p.prereq_course_id
    LEFT JOIN CourseResultStatuses crs
        ON crs.status_code = scr.status_code
    WHERE p.course_id = p_course_id
      AND COALESCE(crs.is_passing, FALSE) = FALSE;

    RETURN v_missing_count = 0;
END;
$$ LANGUAGE plpgsql;
