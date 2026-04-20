-- ==================================================
-- ATTENDIFY - Master Reset Script
-- Run this single file in pgAdmin Query Tool.
-- Drops everything and rebuilds from scratch.
-- Safe to run on first run OR re-run.
-- ==================================================

BEGIN;

-- ==================================================
-- STEP 1: DROP TABLES
-- Ordered child-first so foreign keys don't block drops.
-- CASCADE also auto-drops all triggers on these tables.
-- ==================================================

DROP TABLE IF EXISTS AuditLogs          CASCADE;
DROP TABLE IF EXISTS Notifications      CASCADE;
DROP TABLE IF EXISTS LeaveRequests      CASCADE;
DROP TABLE IF EXISTS Timetable          CASCADE;
DROP TABLE IF EXISTS FacultyAttendance  CASCADE;
DROP TABLE IF EXISTS StudentAttendance  CASCADE;
DROP TABLE IF EXISTS AttendanceSessions CASCADE;
DROP TABLE IF EXISTS AttendanceStatus   CASCADE;
DROP TABLE IF EXISTS Enrollments        CASCADE;
DROP TABLE IF EXISTS Sections           CASCADE;
DROP TABLE IF EXISTS Rooms              CASCADE;
DROP TABLE IF EXISTS Courses            CASCADE;
DROP TABLE IF EXISTS Faculty            CASCADE;
DROP TABLE IF EXISTS Students           CASCADE;
DROP TABLE IF EXISTS Departments        CASCADE;
DROP TABLE IF EXISTS Users              CASCADE;

-- ==================================================
-- STEP 2: CREATE TABLES
-- ==================================================

-- 1. Users
CREATE TABLE Users (
    user_id       SERIAL       PRIMARY KEY,
    username      VARCHAR(50)  UNIQUE NOT NULL,
    email         VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20)  NOT NULL CHECK (role IN ('Admin', 'Faculty', 'Student')),
    created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- 2. Departments
CREATE TABLE Departments (
    dept_id   SERIAL       PRIMARY KEY,
    dept_name VARCHAR(100) UNIQUE NOT NULL
);

-- 3. Students
CREATE TABLE Students (
    student_id      INTEGER     PRIMARY KEY REFERENCES Users(user_id) ON DELETE CASCADE,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    enrollment_date DATE        NOT NULL DEFAULT CURRENT_DATE,
    dept_id         INTEGER     REFERENCES Departments(dept_id) ON DELETE SET NULL
);

-- 4. Faculty
CREATE TABLE Faculty (
    faculty_id INTEGER     PRIMARY KEY REFERENCES Users(user_id) ON DELETE CASCADE,
    first_name VARCHAR(50) NOT NULL,
    last_name  VARCHAR(50) NOT NULL,
    hire_date  DATE        NOT NULL DEFAULT CURRENT_DATE,
    dept_id    INTEGER     REFERENCES Departments(dept_id) ON DELETE SET NULL
);

-- 5. Courses
CREATE TABLE Courses (
    course_id   SERIAL       PRIMARY KEY,
    course_code VARCHAR(20)  UNIQUE NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    credits     INTEGER      CHECK (credits > 0),
    dept_id     INTEGER      REFERENCES Departments(dept_id) ON DELETE CASCADE
);

-- 6. Rooms
CREATE TABLE Rooms (
    room_id   SERIAL      PRIMARY KEY,
    room_name VARCHAR(50) UNIQUE NOT NULL,
    capacity  INTEGER     CHECK (capacity > 0)
);

-- 7. Sections
CREATE TABLE Sections (
    section_id    SERIAL      PRIMARY KEY,
    course_id     INTEGER     REFERENCES Courses(course_id)  ON DELETE CASCADE,
    faculty_id    INTEGER     REFERENCES Faculty(faculty_id) ON DELETE SET NULL,
    room_id       INTEGER     REFERENCES Rooms(room_id)      ON DELETE SET NULL,
    semester      VARCHAR(20) NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    UNIQUE (course_id, faculty_id, semester, academic_year)
);

-- 8. Enrollments
CREATE TABLE Enrollments (
    enrollment_id SERIAL  PRIMARY KEY,
    student_id    INTEGER REFERENCES Students(student_id) ON DELETE CASCADE,
    section_id    INTEGER REFERENCES Sections(section_id) ON DELETE CASCADE,
    enrolled_date DATE    DEFAULT CURRENT_DATE,
    UNIQUE (student_id, section_id)
);

-- 9. AttendanceStatus
CREATE TABLE AttendanceStatus (
    status_id   SERIAL      PRIMARY KEY,
    status_name VARCHAR(20) UNIQUE NOT NULL   -- Present, Absent, Late, Excused
);

-- 10. AttendanceSessions
CREATE TABLE AttendanceSessions (
    session_id   SERIAL  PRIMARY KEY,
    section_id   INTEGER REFERENCES Sections(section_id) ON DELETE CASCADE,
    session_date DATE    NOT NULL,
    start_time   TIME    NOT NULL,
    end_time     TIME    NOT NULL,
    created_by   INTEGER REFERENCES Faculty(faculty_id)  ON DELETE SET NULL,
    UNIQUE (section_id, session_date, start_time)
);

-- 11. StudentAttendance
CREATE TABLE StudentAttendance (
    attendance_id SERIAL  PRIMARY KEY,
    session_id    INTEGER REFERENCES AttendanceSessions(session_id) ON DELETE CASCADE,
    student_id    INTEGER REFERENCES Students(student_id)           ON DELETE CASCADE,
    status_id     INTEGER REFERENCES AttendanceStatus(status_id),
    remarks       VARCHAR(255),
    UNIQUE (session_id, student_id)
);

-- 12. FacultyAttendance
CREATE TABLE FacultyAttendance (
    faculty_attendance_id SERIAL  PRIMARY KEY,
    faculty_id            INTEGER REFERENCES Faculty(faculty_id)        ON DELETE CASCADE,
    date                  DATE    NOT NULL,
    status_id             INTEGER REFERENCES AttendanceStatus(status_id),
    UNIQUE (faculty_id, date)
);

-- 13. Timetable
--     UNIQUE constraint is required so ON CONFLICT DO NOTHING is valid SQL.
CREATE TABLE Timetable (
    timetable_id SERIAL      PRIMARY KEY,
    section_id   INTEGER     REFERENCES Sections(section_id) ON DELETE CASCADE,
    day_of_week  VARCHAR(15) CHECK (day_of_week IN ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')),
    start_time   TIME        NOT NULL,
    end_time     TIME        NOT NULL,
    room_id      INTEGER     REFERENCES Rooms(room_id) ON DELETE SET NULL,
    UNIQUE (section_id, day_of_week, start_time)
);

-- 14. LeaveRequests
CREATE TABLE LeaveRequests (
    leave_id    SERIAL      PRIMARY KEY,
    user_id     INTEGER     REFERENCES Users(user_id) ON DELETE CASCADE,
    start_date  DATE        NOT NULL,
    end_date    DATE        NOT NULL,
    reason      TEXT        NOT NULL,
    status      VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Rejected')),
    reviewed_by INTEGER     REFERENCES Users(user_id) ON DELETE SET NULL,
    created_at  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

-- 15. Notifications
CREATE TABLE Notifications (
    notification_id SERIAL    PRIMARY KEY,
    user_id         INTEGER   REFERENCES Users(user_id) ON DELETE CASCADE,
    message         TEXT      NOT NULL,
    is_read         BOOLEAN   DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 16. AuditLogs
CREATE TABLE AuditLogs (
    log_id     SERIAL      PRIMARY KEY,
    user_id    INTEGER     REFERENCES Users(user_id) ON DELETE SET NULL,
    action     VARCHAR(50) NOT NULL,   -- INSERT, UPDATE, DELETE
    table_name VARCHAR(50) NOT NULL,
    record_id  INTEGER,
    timestamp  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

-- ==================================================
-- STEP 3: INDEXES
-- ==================================================

CREATE INDEX idx_student_dept       ON Students(dept_id);
CREATE INDEX idx_faculty_dept       ON Faculty(dept_id);
CREATE INDEX idx_sections_course    ON Sections(course_id);
CREATE INDEX idx_enrollment_student ON Enrollments(student_id);
CREATE INDEX idx_enrollment_section ON Enrollments(section_id);
CREATE INDEX idx_attendance_session ON StudentAttendance(session_id);
CREATE INDEX idx_attendance_student ON StudentAttendance(student_id);

-- ==================================================
-- STEP 4: FUNCTIONS & PROCEDURES
-- CREATE OR REPLACE handles the case where they already exist.
-- ==================================================

-- Mark or update one student attendance record
CREATE OR REPLACE PROCEDURE mark_attendance(
    p_session_id  INT,
    p_student_id  INT,
    p_status_name VARCHAR,
    p_remarks     VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    v_status_id INT;
BEGIN
    SELECT status_id INTO v_status_id
    FROM AttendanceStatus WHERE status_name = p_status_name;

    IF v_status_id IS NULL THEN
        RAISE EXCEPTION 'Invalid attendance status: %', p_status_name;
    END IF;

    INSERT INTO StudentAttendance (session_id, student_id, status_id, remarks)
    VALUES (p_session_id, p_student_id, v_status_id, p_remarks)
    ON CONFLICT (session_id, student_id) DO UPDATE
        SET status_id = EXCLUDED.status_id,
            remarks   = EXCLUDED.remarks;
END;
$$;

-- Calculate attendance percentage for a student in a section
CREATE OR REPLACE FUNCTION calculate_attendance_percentage(
    p_student_id INT,
    p_section_id INT
)
RETURNS NUMERIC
LANGUAGE plpgsql AS $$
DECLARE
    v_total_sessions    INT;
    v_attended_sessions INT;
    v_percentage        NUMERIC := 0.0;
BEGIN
    SELECT COUNT(*) INTO v_total_sessions
    FROM AttendanceSessions
    WHERE section_id = p_section_id;

    IF v_total_sessions = 0 THEN
        RETURN 0.0;
    END IF;

    SELECT COUNT(*) INTO v_attended_sessions
    FROM StudentAttendance sa
    JOIN AttendanceSessions s  ON sa.session_id = s.session_id
    JOIN AttendanceStatus   st ON sa.status_id  = st.status_id
    WHERE s.section_id    = p_section_id
      AND sa.student_id   = p_student_id
      AND st.status_name IN ('Present', 'Late');

    v_percentage := (v_attended_sessions::NUMERIC / v_total_sessions::NUMERIC) * 100.0;
    RETURN ROUND(v_percentage, 2);
END;
$$;

-- Procedure: notify_low_attendance_students (uses CURSOR)
-- Iterates row-by-row over every student below 75% attendance
-- and inserts a personalised warning Notification for each one.
-- Demonstrates: CURSOR, OPEN / FETCH / CLOSE, LOOP, EXIT WHEN NOT FOUND
CREATE OR REPLACE PROCEDURE notify_low_attendance_students()
LANGUAGE plpgsql AS $$
DECLARE
    cur_low CURSOR FOR
        SELECT student_id,
               username,
               first_name,
               last_name,
               course_name,
               attendance_percentage
        FROM   low_attendance_students;

    rec    RECORD;
    v_msg  TEXT;
BEGIN
    OPEN cur_low;
    LOOP
        FETCH cur_low INTO rec;
        EXIT WHEN NOT FOUND;

        v_msg := format(
            'Attendance Alert: Dear %s %s, your attendance in "%s" is %.2f%% — below the required 75%%. Please attend classes regularly.',
            rec.first_name,
            rec.last_name,
            rec.course_name,
            rec.attendance_percentage
        );

        INSERT INTO Notifications (user_id, message, is_read)
        VALUES (rec.student_id, v_msg, FALSE)
        ON CONFLICT DO NOTHING;

        RAISE NOTICE 'Notified student % (id=%) — %.2f%%',
            rec.username, rec.student_id, rec.attendance_percentage;
    END LOOP;
    CLOSE cur_low;
END;
$$;

-- ==================================================
-- STEP 5: TRIGGERS
-- ==================================================

-- Duplicate attendance guard:
-- Returns NULL (silently skips the row) so ON CONFLICT DO NOTHING
-- in seed/test scripts never aborts the transaction.
-- The UNIQUE(session_id, student_id) constraint is the hard enforcer.
CREATE OR REPLACE FUNCTION check_duplicate_attendance()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM StudentAttendance
        WHERE session_id = NEW.session_id AND student_id = NEW.student_id
    ) THEN
        RETURN NULL;   -- skip duplicate, never raise
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_duplicate_attendance_trg
BEFORE INSERT ON StudentAttendance
FOR EACH ROW
EXECUTE FUNCTION check_duplicate_attendance();

-- Audit log for all Users table changes
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
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_users_changes
AFTER INSERT OR UPDATE OR DELETE ON Users
FOR EACH ROW
EXECUTE FUNCTION log_user_changes();

-- ==================================================
-- STEP 6: VIEWS
-- ==================================================

CREATE OR REPLACE VIEW student_attendance_report AS
SELECT
    s.student_id,
    u.username,
    s.first_name,
    s.last_name,
    c.course_code,
    c.course_name,
    sec.section_id,
    calculate_attendance_percentage(s.student_id, sec.section_id) AS attendance_percentage
FROM Students    s
JOIN Users       u   ON s.student_id  = u.user_id
JOIN Enrollments e   ON s.student_id  = e.student_id
JOIN Sections    sec ON e.section_id  = sec.section_id
JOIN Courses     c   ON sec.course_id = c.course_id;

CREATE OR REPLACE VIEW low_attendance_students AS
SELECT * FROM student_attendance_report
WHERE attendance_percentage < 75.0;

CREATE OR REPLACE VIEW session_details_view AS
SELECT
    sess.session_id,
    sess.session_date,
    sess.start_time,
    sess.end_time,
    c.course_code,
    c.course_name,
    f.first_name AS faculty_first_name,
    f.last_name  AS faculty_last_name
FROM AttendanceSessions sess
JOIN Sections sec ON sess.section_id = sec.section_id
JOIN Courses  c   ON sec.course_id   = c.course_id
LEFT JOIN Faculty f ON sess.created_by = f.faculty_id;

-- 4. View: Sections with High Enrolment (GROUP BY + HAVING)
-- HAVING filters AFTER aggregation; shows sections with more than 1 enrolled student.
CREATE OR REPLACE VIEW high_enrolment_sections AS
SELECT
    sec.section_id,
    c.course_code,
    c.course_name,
    sec.semester,
    sec.academic_year,
    COUNT(e.student_id)  AS enrolled_students
FROM Sections    sec
JOIN Courses     c ON sec.course_id = c.course_id
JOIN Enrollments e ON e.section_id  = sec.section_id
GROUP BY
    sec.section_id,
    c.course_code,
    c.course_name,
    sec.semester,
    sec.academic_year
HAVING COUNT(e.student_id) > 1;

-- 5. View: Department Attendance Summary (GROUP BY + HAVING + AVG aggregate)
-- Shows only departments where average attendance falls below 80%.
CREATE OR REPLACE VIEW dept_low_avg_attendance AS
SELECT
    d.dept_id,
    d.dept_name,
    COUNT(DISTINCT s.student_id)                    AS total_students,
    ROUND(AVG(
        calculate_attendance_percentage(s.student_id, sec.section_id)
    ), 2)                                            AS avg_attendance_pct
FROM Departments  d
JOIN Students     s   ON s.dept_id     = d.dept_id
JOIN Enrollments  e   ON e.student_id  = s.student_id
JOIN Sections     sec ON sec.section_id = e.section_id
GROUP BY d.dept_id, d.dept_name
HAVING ROUND(AVG(
    calculate_attendance_percentage(s.student_id, sec.section_id)
), 2) < 80.0;

-- ==================================================
-- STEP 7: SEED DATA
-- All IDs resolved via subqueries — zero hardcoded integers.
-- ==================================================

INSERT INTO Departments (dept_name) VALUES
    ('Computer Science'),
    ('Information Technology'),
    ('Mathematics');

INSERT INTO Users (username, email, password_hash, role) VALUES
    ('admin1', 'admin@attendify.edu',    'admin123', 'Admin'),
    ('fac1',   'faculty1@attendify.edu', 'fac123',   'Faculty'),
    ('stud1',  'student1@attendify.edu', 'stud123',  'Student'),
    ('stud2',  'student2@attendify.edu', 'stud222',  'Student');

INSERT INTO Students (student_id, first_name, last_name, dept_id)
    SELECT u.user_id, 'John', 'Doe', d.dept_id
    FROM Users u, Departments d
    WHERE u.username = 'stud1' AND d.dept_name = 'Computer Science';

INSERT INTO Students (student_id, first_name, last_name, dept_id)
    SELECT u.user_id, 'Jane', 'Smith', d.dept_id
    FROM Users u, Departments d
    WHERE u.username = 'stud2' AND d.dept_name = 'Computer Science';

INSERT INTO Faculty (faculty_id, first_name, last_name, dept_id)
    SELECT u.user_id, 'Dr. Alice', 'Cooper', d.dept_id
    FROM Users u, Departments d
    WHERE u.username = 'fac1' AND d.dept_name = 'Computer Science';

INSERT INTO Courses (course_code, course_name, credits, dept_id)
    SELECT 'CS101', 'Introduction to Programming', 3, dept_id
    FROM Departments WHERE dept_name = 'Computer Science';

INSERT INTO Courses (course_code, course_name, credits, dept_id)
    SELECT 'CS201', 'Data Structures', 4, dept_id
    FROM Departments WHERE dept_name = 'Computer Science';

INSERT INTO Courses (course_code, course_name, credits, dept_id)
    SELECT 'IT201', 'Database Systems', 4, dept_id
    FROM Departments WHERE dept_name = 'Information Technology';

INSERT INTO Rooms (room_name, capacity) VALUES
    ('Room 101', 50),
    ('Room 102', 60),
    ('Lab A',    30);

INSERT INTO Sections (course_id, faculty_id, room_id, semester, academic_year)
    SELECT c.course_id, f.faculty_id, r.room_id, 'Fall', '2026-2027'
    FROM Courses c, Faculty f, Rooms r
    WHERE c.course_code = 'CS101'
      AND f.faculty_id  = (SELECT user_id FROM Users WHERE username = 'fac1')
      AND r.room_name   = 'Room 101';

INSERT INTO Sections (course_id, faculty_id, room_id, semester, academic_year)
    SELECT c.course_id, f.faculty_id, r.room_id, 'Fall', '2026-2027'
    FROM Courses c, Faculty f, Rooms r
    WHERE c.course_code = 'CS201'
      AND f.faculty_id  = (SELECT user_id FROM Users WHERE username = 'fac1')
      AND r.room_name   = 'Lab A';

INSERT INTO Enrollments (student_id, section_id)
    SELECT (SELECT user_id FROM Users WHERE username = 'stud1'), s.section_id
    FROM Sections s JOIN Courses c ON c.course_id = s.course_id
    WHERE c.course_code = 'CS101';

INSERT INTO Enrollments (student_id, section_id)
    SELECT (SELECT user_id FROM Users WHERE username = 'stud1'), s.section_id
    FROM Sections s JOIN Courses c ON c.course_id = s.course_id
    WHERE c.course_code = 'CS201';

INSERT INTO Enrollments (student_id, section_id)
    SELECT (SELECT user_id FROM Users WHERE username = 'stud2'), s.section_id
    FROM Sections s JOIN Courses c ON c.course_id = s.course_id
    WHERE c.course_code = 'CS101';

INSERT INTO AttendanceStatus (status_name) VALUES
    ('Present'), ('Absent'), ('Late'), ('Excused');

INSERT INTO Timetable (section_id, day_of_week, start_time, end_time, room_id)
    SELECT s.section_id, 'Monday', '09:00:00', '10:30:00', s.room_id
    FROM Sections s JOIN Courses c ON c.course_id = s.course_id
    WHERE c.course_code = 'CS101';

INSERT INTO Timetable (section_id, day_of_week, start_time, end_time, room_id)
    SELECT s.section_id, 'Wednesday', '09:00:00', '10:30:00', s.room_id
    FROM Sections s JOIN Courses c ON c.course_id = s.course_id
    WHERE c.course_code = 'CS101';

INSERT INTO Timetable (section_id, day_of_week, start_time, end_time, room_id)
    SELECT s.section_id, 'Tuesday', '11:00:00', '12:30:00', s.room_id
    FROM Sections s JOIN Courses c ON c.course_id = s.course_id
    WHERE c.course_code = 'CS201';

INSERT INTO Timetable (section_id, day_of_week, start_time, end_time, room_id)
    SELECT s.section_id, 'Thursday', '11:00:00', '12:30:00', s.room_id
    FROM Sections s JOIN Courses c ON c.course_id = s.course_id
    WHERE c.course_code = 'CS201';

COMMIT;
