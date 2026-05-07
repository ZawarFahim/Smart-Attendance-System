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

CREATE OR REPLACE PROCEDURE record_student_course_result(
    p_student_id INT,
    p_course_id INT,
    p_status_code VARCHAR,
    p_recorded_by INT DEFAULT NULL,
    p_notes TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO StudentCourseResults (student_id, course_id, status_code, recorded_by, notes)
    VALUES (p_student_id, p_course_id, p_status_code, p_recorded_by, p_notes)
    ON CONFLICT (student_id, course_id)
    DO UPDATE SET
        status_code = EXCLUDED.status_code,
        recorded_at = CURRENT_TIMESTAMP,
        recorded_by = EXCLUDED.recorded_by,
        notes = EXCLUDED.notes;
END;
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 3: FREEZE POLICY, OVERRIDES, AND ARCHIVING
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE PROCEDURE set_attendance_policy(
    p_freeze_minutes INT,
    p_archive_after_days INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO AttendancePolicies (policy_id, freeze_minutes, archive_after_days, updated_at)
    VALUES (1, p_freeze_minutes, p_archive_after_days, CURRENT_TIMESTAMP)
    ON CONFLICT (policy_id)
    DO UPDATE SET
        freeze_minutes = EXCLUDED.freeze_minutes,
        archive_after_days = EXCLUDED.archive_after_days,
        updated_at = CURRENT_TIMESTAMP;
END;
$$;

CREATE OR REPLACE PROCEDURE grant_attendance_edit_override(
    p_session_id INT,
    p_student_id INT DEFAULT NULL,
    p_granted_by INT,
    p_reason TEXT,
    p_valid_until TIMESTAMP DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO AttendanceEditOverrides (session_id, student_id, granted_by, reason, valid_until)
    VALUES (p_session_id, p_student_id, p_granted_by, p_reason, p_valid_until);
END;
$$;

CREATE OR REPLACE PROCEDURE archive_attendance_for_semester(
    p_semester VARCHAR,
    p_academic_year VARCHAR,
    p_archived_by INT DEFAULT NULL,
    p_reason TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Map original session_id -> new archive_session_id for this archival batch
    CREATE TEMP TABLE tmp_session_map (
        original_session_id INT PRIMARY KEY,
        archive_session_id INT NOT NULL
    ) ON COMMIT DROP;

    WITH ins AS (
        INSERT INTO AttendanceSessionsArchive (
            original_session_id,
            section_id,
            session_date,
            start_time,
            end_time,
            created_by,
            archived_at,
            archived_by,
            archive_reason
        )
        SELECT
            sess.session_id,
            sess.section_id,
            sess.session_date,
            sess.start_time,
            sess.end_time,
            sess.created_by,
            CURRENT_TIMESTAMP,
            p_archived_by,
            p_reason
        FROM AttendanceSessions sess
        JOIN Sections sec ON sec.section_id = sess.section_id
        WHERE sec.semester = p_semester
          AND sec.academic_year = p_academic_year
        RETURNING original_session_id, archive_session_id
    )
    INSERT INTO tmp_session_map (original_session_id, archive_session_id)
    SELECT original_session_id, archive_session_id
    FROM ins;

    -- Archive student attendance using the mapping table
    INSERT INTO StudentAttendanceArchive (
        archive_session_id,
        original_attendance_id,
        student_id,
        status_id,
        remarks,
        archived_at
    )
    SELECT
        m.archive_session_id,
        sa.attendance_id,
        sa.student_id,
        sa.status_id,
        sa.remarks,
        CURRENT_TIMESTAMP
    FROM StudentAttendance sa
    JOIN tmp_session_map m ON m.original_session_id = sa.session_id;

    -- Delete in FK-safe order
    DELETE FROM StudentAttendance sa
    USING tmp_session_map m
    WHERE sa.session_id = m.original_session_id;

    DELETE FROM AttendanceSessions sess
    USING tmp_session_map m
    WHERE sess.session_id = m.original_session_id;
END;
$$;
