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

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 1: TRANSACTION-SAFE ENROLLMENT WITH PREREQUISITE VALIDATION
-- Uses trigger-based enforcement + explicit transaction boundary in procedure.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE PROCEDURE enroll_student_in_section(
    p_student_id INT,
    p_section_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Insert is guarded by trg_validate_prereq_enrollment (and unique constraint uq_enrollment)
    INSERT INTO Enrollments (student_id, section_id)
    VALUES (p_student_id, p_section_id);
END;
$$;



-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 4: UPSERT PROFILE IMAGE
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE PROCEDURE upsert_student_profile_image(
    p_student_id INT,
    p_image_name VARCHAR,
    p_image_path TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO StudentProfileImages (student_id, image_name, image_path, upload_timestamp)
    VALUES (p_student_id, p_image_name, p_image_path, CURRENT_TIMESTAMP)
    ON CONFLICT (student_id)
    DO UPDATE SET
        image_name = EXCLUDED.image_name,
        image_path = EXCLUDED.image_path,
        upload_timestamp = CURRENT_TIMESTAMP;
END;
$$;
