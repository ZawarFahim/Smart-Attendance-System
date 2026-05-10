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

-- FacultyAttendance: REMOVED — never referenced by any Python service, view, trigger, or procedure.

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

-- ExamTimetable: REMOVED — exam scheduling feature was never implemented in the application.

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

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 4: STUDENT PROFILE IMAGES (3NF)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE StudentProfileImages (
    image_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL UNIQUE,
    image_name VARCHAR(255) NOT NULL,
    image_path TEXT NOT NULL,
    upload_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
