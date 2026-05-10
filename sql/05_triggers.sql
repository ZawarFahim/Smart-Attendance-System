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




