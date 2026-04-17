-- ==================================================
-- ATTENDIFY - Smart Attendance Management System
-- Database Schema Definition (PostgreSQL)
-- ==================================================

-- Drop tables if they exist to prevent errors on re-run
DROP TABLE IF EXISTS AuditLogs CASCADE;
DROP TABLE IF EXISTS Notifications CASCADE;
DROP TABLE IF EXISTS LeaveRequests CASCADE;
DROP TABLE IF EXISTS Timetable CASCADE;
DROP TABLE IF EXISTS FacultyAttendance CASCADE;
DROP TABLE IF EXISTS StudentAttendance CASCADE;
DROP TABLE IF EXISTS AttendanceSessions CASCADE;
DROP TABLE IF EXISTS AttendanceStatus CASCADE;
DROP TABLE IF EXISTS Enrollments CASCADE;
DROP TABLE IF EXISTS Sections CASCADE;
DROP TABLE IF EXISTS Rooms CASCADE;
DROP TABLE IF EXISTS Courses CASCADE;
DROP TABLE IF EXISTS Faculty CASCADE;
DROP TABLE IF EXISTS Students CASCADE;
DROP TABLE IF EXISTS Departments CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

-- 1. Users Table
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('Admin', 'Faculty', 'Student')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Departments Table
CREATE TABLE Departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) UNIQUE NOT NULL
);

-- 3. Students Table
CREATE TABLE Students (
    student_id INTEGER PRIMARY KEY REFERENCES Users(user_id) ON DELETE CASCADE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    enrollment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    dept_id INTEGER REFERENCES Departments(dept_id) ON DELETE SET NULL
);

-- 4. Faculty Table
CREATE TABLE Faculty (
    faculty_id INTEGER PRIMARY KEY REFERENCES Users(user_id) ON DELETE CASCADE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE,
    dept_id INTEGER REFERENCES Departments(dept_id) ON DELETE SET NULL
);

-- 5. Courses Table
CREATE TABLE Courses (
    course_id SERIAL PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    credits INTEGER CHECK (credits > 0),
    dept_id INTEGER REFERENCES Departments(dept_id) ON DELETE CASCADE
);

-- 6. Rooms Table
CREATE TABLE Rooms (
    room_id SERIAL PRIMARY KEY,
    room_name VARCHAR(50) UNIQUE NOT NULL,
    capacity INTEGER CHECK (capacity > 0)
);

-- 7. Sections Table
CREATE TABLE Sections (
    section_id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES Courses(course_id) ON DELETE CASCADE,
    faculty_id INTEGER REFERENCES Faculty(faculty_id) ON DELETE SET NULL,
    room_id INTEGER REFERENCES Rooms(room_id) ON DELETE SET NULL,
    semester VARCHAR(20) NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    UNIQUE (course_id, faculty_id, semester, academic_year)
);

-- 8. Enrollments Table
CREATE TABLE Enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES Students(student_id) ON DELETE CASCADE,
    section_id INTEGER REFERENCES Sections(section_id) ON DELETE CASCADE,
    enrolled_date DATE DEFAULT CURRENT_DATE,
    UNIQUE (student_id, section_id)
);

-- 9. AttendanceStatus Table
CREATE TABLE AttendanceStatus (
    status_id SERIAL PRIMARY KEY,
    status_name VARCHAR(20) UNIQUE NOT NULL -- Present, Absent, Late, Excused
);

-- 10. AttendanceSessions Table
CREATE TABLE AttendanceSessions (
    session_id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES Sections(section_id) ON DELETE CASCADE,
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_by INTEGER REFERENCES Faculty(faculty_id) ON DELETE SET NULL,
    UNIQUE (section_id, session_date, start_time)
);

-- 11. StudentAttendance Table
CREATE TABLE StudentAttendance (
    attendance_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES AttendanceSessions(session_id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES Students(student_id) ON DELETE CASCADE,
    status_id INTEGER REFERENCES AttendanceStatus(status_id),
    remarks VARCHAR(255),
    UNIQUE (session_id, student_id)
);

-- 12. FacultyAttendance Table
CREATE TABLE FacultyAttendance (
    faculty_attendance_id SERIAL PRIMARY KEY,
    faculty_id INTEGER REFERENCES Faculty(faculty_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status_id INTEGER REFERENCES AttendanceStatus(status_id),
    UNIQUE (faculty_id, date)
);

-- 13. Timetable Table
CREATE TABLE Timetable (
    timetable_id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES Sections(section_id) ON DELETE CASCADE,
    day_of_week VARCHAR(15) CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room_id INTEGER REFERENCES Rooms(room_id) ON DELETE SET NULL,
    UNIQUE (section_id, day_of_week, start_time)
);

-- 14. LeaveRequests Table
CREATE TABLE LeaveRequests (
    leave_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES Users(user_id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Rejected')),
    reviewed_by INTEGER REFERENCES Users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 15. Notifications Table
CREATE TABLE Notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES Users(user_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 16. AuditLogs Table
CREATE TABLE AuditLogs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES Users(user_id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL, -- INSERT, UPDATE, DELETE
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================================================
-- INDEXES
-- ==================================================
CREATE INDEX idx_student_dept ON Students(dept_id);
CREATE INDEX idx_faculty_dept ON Faculty(dept_id);
CREATE INDEX idx_sections_course ON Sections(course_id);
CREATE INDEX idx_enrollment_student ON Enrollments(student_id);
CREATE INDEX idx_enrollment_section ON Enrollments(section_id);
CREATE INDEX idx_attendance_session ON StudentAttendance(session_id);
CREATE INDEX idx_attendance_student ON StudentAttendance(student_id);
