-- 01_tables.sql
-- Base tables without foreign key constraints (or with them if simple)

CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE Students (
    student_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    enrollment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    dept_id INTEGER
);

CREATE TABLE Faculty (
    faculty_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE,
    dept_id INTEGER
);

CREATE TABLE Courses (
    course_id SERIAL PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    credits INTEGER,
    dept_id INTEGER
);

CREATE TABLE Rooms (
    room_id SERIAL PRIMARY KEY,
    room_name VARCHAR(50) UNIQUE NOT NULL,
    capacity INTEGER
);

CREATE TABLE Sections (
    section_id SERIAL PRIMARY KEY,
    course_id INTEGER,
    faculty_id INTEGER,
    room_id INTEGER,
    semester VARCHAR(20) NOT NULL,
    academic_year VARCHAR(10) NOT NULL
);

CREATE TABLE Enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER,
    section_id INTEGER,
    enrolled_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE AttendanceStatus (
    status_id SERIAL PRIMARY KEY,
    status_name VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE AttendanceSessions (
    session_id SERIAL PRIMARY KEY,
    section_id INTEGER,
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_by INTEGER
);

CREATE TABLE StudentAttendance (
    attendance_id SERIAL PRIMARY KEY,
    session_id INTEGER,
    student_id INTEGER,
    status_id INTEGER,
    remarks VARCHAR(255)
);

CREATE TABLE FacultyAttendance (
    faculty_attendance_id SERIAL PRIMARY KEY,
    faculty_id INTEGER,
    date DATE NOT NULL,
    status_id INTEGER
);

CREATE TABLE Timetable (
    timetable_id SERIAL PRIMARY KEY,
    section_id INTEGER,
    day_of_week VARCHAR(15),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room_id INTEGER,
    valid_from DATE,
    valid_to DATE,
    is_recurring BOOLEAN DEFAULT TRUE
);

CREATE TABLE ExamTimetable (
    exam_id SERIAL PRIMARY KEY,
    course_id INTEGER,
    exam_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room_id INTEGER,
    exam_type VARCHAR(50) NOT NULL
);

CREATE TABLE LeaveRequests (
    leave_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending',
    reviewed_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE AuditLogs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER,
    old_data JSONB,
    new_data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 1: PREREQUISITES + COURSE COMPLETION (3NF)
-- ─────────────────────────────────────────────────────────────────────────────

-- Course-to-course prerequisite dependencies (many-to-many self relationship)
CREATE TABLE CoursePrerequisites (
    course_id INTEGER NOT NULL,
    prereq_course_id INTEGER NOT NULL,
    PRIMARY KEY (course_id, prereq_course_id)
);

-- Normalized result status lookup to avoid embedding business meaning in raw text
CREATE TABLE CourseResultStatuses (
    status_code VARCHAR(20) PRIMARY KEY,
    status_name VARCHAR(50) UNIQUE NOT NULL,
    is_passing BOOLEAN NOT NULL
);

-- Student course completion/results (course-level, not section-level)
CREATE TABLE StudentCourseResults (
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    status_code VARCHAR(20) NOT NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    recorded_by INTEGER,
    notes TEXT,
    PRIMARY KEY (student_id, course_id)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 3: ATTENDANCE FREEZE + ARCHIVE + OVERRIDES (3NF)
-- ─────────────────────────────────────────────────────────────────────────────

-- Singleton-style policy table (kept normalized; 1 row expected)
CREATE TABLE AttendancePolicies (
    policy_id INTEGER PRIMARY KEY,
    freeze_minutes INTEGER NOT NULL,
    archive_after_days INTEGER NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Optional override grants allowing edits after freeze deadline
CREATE TABLE AttendanceEditOverrides (
    override_id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    student_id INTEGER,
    granted_by INTEGER NOT NULL,
    reason TEXT NOT NULL,
    granted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,
    UNIQUE (session_id, student_id, granted_by, granted_at)
);

-- Archive tables (historical tracking; do not reuse current PKs)
CREATE TABLE AttendanceSessionsArchive (
    archive_session_id SERIAL PRIMARY KEY,
    original_session_id INTEGER,
    section_id INTEGER NOT NULL,
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_by INTEGER,
    archived_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    archived_by INTEGER,
    archive_reason TEXT
);

CREATE TABLE StudentAttendanceArchive (
    archive_attendance_id SERIAL PRIMARY KEY,
    archive_session_id INTEGER NOT NULL,
    original_attendance_id INTEGER,
    student_id INTEGER NOT NULL,
    status_id INTEGER NOT NULL,
    remarks VARCHAR(255),
    archived_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Explicit audit trail for post-freeze edits (actor captured)
CREATE TABLE AttendanceEditAudit (
    audit_id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    old_status_id INTEGER,
    new_status_id INTEGER,
    old_remarks VARCHAR(255),
    new_remarks VARCHAR(255),
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    changed_by INTEGER,
    change_source VARCHAR(30) NOT NULL DEFAULT 'trigger'
);
