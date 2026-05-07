-- 05_triggers.sql
CREATE OR REPLACE FUNCTION log_user_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO AuditLogs (action, table_name, record_id, old_data)
        VALUES ('DELETE', TG_TABLE_NAME, OLD.user_id, row_to_json(OLD)::jsonb);
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO AuditLogs (action, table_name, record_id, old_data, new_data)
        VALUES ('UPDATE', TG_TABLE_NAME, NEW.user_id, row_to_json(OLD)::jsonb, row_to_json(NEW)::jsonb);
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO AuditLogs (action, table_name, record_id, new_data)
        VALUES ('INSERT', TG_TABLE_NAME, NEW.user_id, row_to_json(NEW)::jsonb);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_users_trigger
AFTER INSERT OR UPDATE OR DELETE ON Users
FOR EACH ROW EXECUTE FUNCTION log_user_changes();

-- Universal Logging Function for other tables
CREATE OR REPLACE FUNCTION log_universal_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO AuditLogs (action, table_name, old_data)
        VALUES ('DELETE', TG_TABLE_NAME, row_to_json(OLD)::jsonb);
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO AuditLogs (action, table_name, old_data, new_data)
        VALUES ('UPDATE', TG_TABLE_NAME, row_to_json(OLD)::jsonb, row_to_json(NEW)::jsonb);
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO AuditLogs (action, table_name, new_data)
        VALUES ('INSERT', TG_TABLE_NAME, row_to_json(NEW)::jsonb);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_timetable_trigger AFTER INSERT OR UPDATE OR DELETE ON Timetable FOR EACH ROW EXECUTE FUNCTION log_universal_changes();
CREATE TRIGGER audit_attendance_trigger AFTER INSERT OR UPDATE OR DELETE ON StudentAttendance FOR EACH ROW EXECUTE FUNCTION log_universal_changes();
CREATE TRIGGER audit_enrollments_trigger AFTER INSERT OR UPDATE OR DELETE ON Enrollments FOR EACH ROW EXECUTE FUNCTION log_universal_changes();

-- Timetable Clash Detection Trigger
CREATE OR REPLACE FUNCTION check_timetable_clash()
RETURNS TRIGGER AS $$
DECLARE
    v_clash_exists BOOLEAN;
    v_semester VARCHAR;
    v_academic_year VARCHAR;
    v_faculty_id INT;
BEGIN
    SELECT semester, academic_year, faculty_id INTO v_semester, v_academic_year, v_faculty_id 
    FROM Sections WHERE section_id = NEW.section_id;

    -- Check Room Clash
    SELECT EXISTS (
        SELECT 1 FROM Timetable t
        JOIN Sections s ON t.section_id = s.section_id
        WHERE t.room_id = NEW.room_id AND t.day_of_week = NEW.day_of_week 
          AND s.semester = v_semester AND s.academic_year = v_academic_year
          AND (t.start_time < NEW.end_time AND t.end_time > NEW.start_time)
          AND t.timetable_id IS DISTINCT FROM NEW.timetable_id
    ) INTO v_clash_exists;

    IF v_clash_exists THEN
        RAISE EXCEPTION 'Room Clash Detected: Room is already booked for this time slot.';
    END IF;

    -- Check Faculty Clash
    SELECT EXISTS (
        SELECT 1 FROM Timetable t
        JOIN Sections s ON t.section_id = s.section_id
        WHERE s.faculty_id = v_faculty_id AND t.day_of_week = NEW.day_of_week 
          AND s.semester = v_semester AND s.academic_year = v_academic_year
          AND (t.start_time < NEW.end_time AND t.end_time > NEW.start_time)
          AND t.timetable_id IS DISTINCT FROM NEW.timetable_id
    ) INTO v_clash_exists;

    IF v_clash_exists THEN
        RAISE EXCEPTION 'Faculty Clash Detected: Faculty is already teaching another section at this time.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_clash_trigger
BEFORE INSERT OR UPDATE ON Timetable
FOR EACH ROW EXECUTE FUNCTION check_timetable_clash();

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 1: PREREQUISITE ENROLLMENT ENFORCEMENT
-- Enforced at DB level so direct INSERTs cannot bypass validation.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION validate_prerequisites_for_enrollment()
RETURNS TRIGGER AS $$
DECLARE
    v_course_id INT;
    v_missing TEXT;
BEGIN
    SELECT course_id INTO v_course_id
    FROM Sections
    WHERE section_id = NEW.section_id;

    IF v_course_id IS NULL THEN
        RAISE EXCEPTION 'Invalid section_id % (no course found)', NEW.section_id;
    END IF;

    -- If the course has prerequisites, ensure the student has passing results for all of them.
    IF EXISTS (SELECT 1 FROM CoursePrerequisites p WHERE p.course_id = v_course_id) THEN
        SELECT STRING_AGG(pc.course_code, ', ' ORDER BY pc.course_code)
        INTO v_missing
        FROM CoursePrerequisites p
        JOIN Courses pc ON pc.course_id = p.prereq_course_id
        LEFT JOIN StudentCourseResults scr
            ON scr.student_id = NEW.student_id
           AND scr.course_id = p.prereq_course_id
        LEFT JOIN CourseResultStatuses crs
            ON crs.status_code = scr.status_code
        WHERE p.course_id = v_course_id
          AND COALESCE(crs.is_passing, FALSE) = FALSE;

        IF v_missing IS NOT NULL THEN
            RAISE EXCEPTION 'Enrollment blocked: missing prerequisites for course_id % => %', v_course_id, v_missing;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_prereq_enrollment
BEFORE INSERT ON Enrollments
FOR EACH ROW EXECUTE FUNCTION validate_prerequisites_for_enrollment();

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 3: ATTENDANCE FREEZE (configurable) + POST-FREEZE AUDIT
-- Uses AttendancePolicies(policy_id=1) for freeze window.
-- Supports overrides via AttendanceEditOverrides.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION enforce_attendance_freeze()
RETURNS TRIGGER AS $$
DECLARE
    v_freeze_minutes INT;
    v_deadline TIMESTAMP;
    v_now TIMESTAMP := CURRENT_TIMESTAMP;
    v_has_override BOOLEAN;
BEGIN
    SELECT freeze_minutes INTO v_freeze_minutes
    FROM AttendancePolicies
    WHERE policy_id = 1;

    -- If policy isn't seeded yet, default to 120 minutes to keep system operable.
    IF v_freeze_minutes IS NULL THEN
        v_freeze_minutes := 120;
    END IF;

    SELECT (s.session_date::timestamp + s.end_time) + (v_freeze_minutes || ' minutes')::interval
    INTO v_deadline
    FROM AttendanceSessions s
    WHERE s.session_id = COALESCE(NEW.session_id, OLD.session_id);

    -- If session not found, block to protect integrity.
    IF v_deadline IS NULL THEN
        RAISE EXCEPTION 'Attendance session % not found', COALESCE(NEW.session_id, OLD.session_id);
    END IF;

    IF v_now > v_deadline THEN
        SELECT EXISTS (
            SELECT 1
            FROM AttendanceEditOverrides o
            WHERE o.session_id = COALESCE(NEW.session_id, OLD.session_id)
              AND (o.student_id IS NULL OR o.student_id = COALESCE(NEW.student_id, OLD.student_id))
              AND (o.valid_until IS NULL OR o.valid_until >= v_now)
        ) INTO v_has_override;

        IF NOT v_has_override THEN
            RAISE EXCEPTION 'Attendance is frozen for session %. Deadline was %', COALESCE(NEW.session_id, OLD.session_id), v_deadline;
        END IF;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_attendance_freeze_guard
BEFORE INSERT OR UPDATE OR DELETE ON StudentAttendance
FOR EACH ROW EXECUTE FUNCTION enforce_attendance_freeze();

CREATE OR REPLACE FUNCTION audit_attendance_changes()
RETURNS TRIGGER AS $$
DECLARE
    v_actor INT;
BEGIN
    -- Optional app-provided actor; if absent, fallback to session creator.
    v_actor := NULLIF(current_setting('app.user_id', TRUE), '')::INT;

    IF v_actor IS NULL THEN
        SELECT created_by INTO v_actor
        FROM AttendanceSessions
        WHERE session_id = NEW.session_id;
    END IF;

    INSERT INTO AttendanceEditAudit (
        session_id,
        student_id,
        old_status_id,
        new_status_id,
        old_remarks,
        new_remarks,
        changed_by,
        change_source
    )
    VALUES (
        NEW.session_id,
        NEW.student_id,
        OLD.status_id,
        NEW.status_id,
        OLD.remarks,
        NEW.remarks,
        v_actor,
        'trigger'
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_student_attendance_update
AFTER UPDATE ON StudentAttendance
FOR EACH ROW
WHEN (OLD.status_id IS DISTINCT FROM NEW.status_id OR OLD.remarks IS DISTINCT FROM NEW.remarks)
EXECUTE FUNCTION audit_attendance_changes();
