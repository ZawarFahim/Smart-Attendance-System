-- ==================================================
-- ATTENDIFY - Seed Data
-- Run this AFTER database/schema.sql
-- ==================================================

-- First, remove all existing data so the script can be run multiple times safely
TRUNCATE Departments, Users, Courses, Rooms, AttendanceStatus, CourseResultStatuses, AttendancePolicies CASCADE;


INSERT INTO Departments (dept_name) VALUES
    ('Computer Science'),
    ('Information Technology'),
    ('Mathematics')
ON CONFLICT (dept_name) DO NOTHING;

-- Users seeded with plaintext passwords (project convention)
INSERT INTO Users (username, email, password_hash, role) VALUES
    ('admin1', 'admin@attendify.edu',    'admin123', 'Admin'),
    ('fac1',   'faculty1@attendify.edu', 'fac123',   'Faculty'),
    ('stud1',  'student1@attendify.edu', 'stud123',  'Student'),
    ('stud2',  'student2@attendify.edu', 'stud222',  'Student')
ON CONFLICT (username) DO NOTHING;

-- Use subqueries so IDs are never hardcoded
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
      AND f.faculty_id = (SELECT user_id FROM Users WHERE username = 'fac1')
      AND r.room_name  = 'Room 101';

INSERT INTO Sections (course_id, faculty_id, room_id, semester, academic_year)
    SELECT c.course_id, f.faculty_id, r.room_id, 'Fall', '2026-2027'
    FROM Courses c, Faculty f, Rooms r
    WHERE c.course_code = 'CS201'
      AND f.faculty_id = (SELECT user_id FROM Users WHERE username = 'fac1')
      AND r.room_name  = 'Lab A';

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

-- Adding Timetable Data
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

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 1: PREREQUISITE / COMPLETION SEEDING
-- CS101 is a prerequisite for CS201
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO CourseResultStatuses (status_code, status_name, is_passing) VALUES
    ('PASSED', 'Passed', TRUE),
    ('FAILED', 'Failed', FALSE),
    ('INPROG', 'In Progress', FALSE)
ON CONFLICT (status_code) DO NOTHING;

INSERT INTO CoursePrerequisites (course_id, prereq_course_id)
SELECT c2.course_id, c1.course_id
FROM Courses c1, Courses c2
WHERE c1.course_code = 'CS101'
  AND c2.course_code = 'CS201'
ON CONFLICT DO NOTHING;

-- stud1 has completed CS101 (can take CS201), stud2 has not.
INSERT INTO StudentCourseResults (student_id, course_id, status_code)
SELECT (SELECT user_id FROM Users WHERE username = 'stud1'),
       (SELECT course_id FROM Courses WHERE course_code = 'CS101'),
       'PASSED'
ON CONFLICT (student_id, course_id) DO UPDATE SET status_code = EXCLUDED.status_code;

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 3: ATTENDANCE POLICY DEFAULT
-- Freeze after 120 minutes; archive after 365 days (configurable via procedure).
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO AttendancePolicies (policy_id, freeze_minutes, archive_after_days)
VALUES (1, 120, 365)
ON CONFLICT (policy_id) DO NOTHING;

-- ==================================================
-- EXPANDED SAMPLE DATA (Appended)
-- ==================================================

-- 1. Additional Departments
INSERT INTO Departments (dept_name) VALUES
    ('Electrical Engineering'),
    ('Mechanical Engineering'),
    ('Business Administration')
ON CONFLICT (dept_name) DO NOTHING;

-- 2. Additional Courses
INSERT INTO Courses (course_code, course_name, credits, dept_id)
    SELECT 'EE201', 'Circuit Analysis', 4, dept_id FROM Departments WHERE dept_name = 'Electrical Engineering' UNION ALL
    SELECT 'ME301', 'Thermodynamics', 3, dept_id FROM Departments WHERE dept_name = 'Mechanical Engineering' UNION ALL
    SELECT 'MGT101', 'Principles of Management', 3, dept_id FROM Departments WHERE dept_name = 'Business Administration' UNION ALL
    SELECT 'CS301', 'Operating Systems', 4, dept_id FROM Departments WHERE dept_name = 'Computer Science' UNION ALL
    SELECT 'CS401', 'Artificial Intelligence', 3, dept_id FROM Departments WHERE dept_name = 'Computer Science';

-- 3. Additional Rooms
INSERT INTO Rooms (room_name, capacity) VALUES
    ('Room 201', 40),
    ('Room 202', 45),
    ('Lecture Hall A', 150),
    ('Seminar Room 1', 25);

-- 4. Additional Sections
INSERT INTO Sections (course_id, faculty_id, room_id, semester, academic_year)
    SELECT c.course_id, f.faculty_id, r.room_id, 'Fall', '2026-2027'
    FROM Courses c, Faculty f, Rooms r
    WHERE c.course_code = 'CS301' 
      AND f.faculty_id = (SELECT user_id FROM Users WHERE username = 'fac1') 
      AND r.room_name = 'Lecture Hall A';

INSERT INTO Sections (course_id, faculty_id, room_id, semester, academic_year)
    SELECT c.course_id, f.faculty_id, r.room_id, 'Fall', '2026-2027'
    FROM Courses c, Faculty f, Rooms r
    WHERE c.course_code = 'CS401' 
      AND f.faculty_id = (SELECT user_id FROM Users WHERE username = 'fac1') 
      AND r.room_name = 'Room 201';

-- 5. Additional Enrollments
INSERT INTO Enrollments (student_id, section_id)
    SELECT u.user_id, s.section_id
    FROM Users u, Sections s JOIN Courses c ON c.course_id = s.course_id
    WHERE u.username = 'stud1' AND c.course_code IN ('CS301', 'CS401');

INSERT INTO Enrollments (student_id, section_id)
    SELECT u.user_id, s.section_id
    FROM Users u, Sections s JOIN Courses c ON c.course_id = s.course_id
    WHERE u.username = 'stud2' AND c.course_code = 'CS301';

-- 6. Additional Timetable Slots
INSERT INTO Timetable (section_id, day_of_week, start_time, end_time, room_id)
    SELECT s.section_id, 'Monday', '13:00:00', '14:30:00', s.room_id
    FROM Sections s JOIN Courses c ON c.course_id = s.course_id WHERE c.course_code = 'CS301';

INSERT INTO Timetable (section_id, day_of_week, start_time, end_time, room_id)
    SELECT s.section_id, 'Wednesday', '13:00:00', '14:30:00', s.room_id
    FROM Sections s JOIN Courses c ON c.course_id = s.course_id WHERE c.course_code = 'CS301';

INSERT INTO Timetable (section_id, day_of_week, start_time, end_time, room_id)
    SELECT s.section_id, 'Friday', '09:00:00', '11:00:00', s.room_id
    FROM Sections s JOIN Courses c ON c.course_id = s.course_id WHERE c.course_code = 'CS401';

-- 7. Course Prerequisites
INSERT INTO CoursePrerequisites (course_id, prereq_course_id)
SELECT c2.course_id, c1.course_id
FROM Courses c1, Courses c2
WHERE c1.course_code = 'CS301' AND c2.course_code = 'CS201'
ON CONFLICT DO NOTHING;

INSERT INTO CoursePrerequisites (course_id, prereq_course_id)
SELECT c2.course_id, c1.course_id
FROM Courses c1, Courses c2
WHERE c1.course_code = 'CS401' AND c2.course_code = 'CS301'
ON CONFLICT DO NOTHING;

-- 8. Leave Requests
INSERT INTO LeaveRequests (user_id, start_date, end_date, reason, status)
    SELECT user_id, '2026-10-10', '2026-10-12', 'Family event', 'Approved'
    FROM Users WHERE username = 'stud1';
INSERT INTO LeaveRequests (user_id, start_date, end_date, reason, status)
    SELECT user_id, '2026-11-01', '2026-11-03', 'Medical leave', 'Pending'
    FROM Users WHERE username = 'stud2';

-- 9. Notifications
INSERT INTO Notifications (user_id, message, is_read)
    SELECT user_id, 'Welcome to the Fall Semester 2026!', FALSE FROM Users WHERE role = 'Student';

INSERT INTO Notifications (user_id, message, is_read)
    SELECT user_id, 'Please submit your course outlines by next week.', FALSE FROM Users WHERE role = 'Faculty';

-- 10. Large scale Attendance Generation (75 Student records across 50 Sessions)
DO $$
DECLARE
    v_fac1_id INT;
    v_cs101_sec_id INT;
    v_cs201_sec_id INT;
    v_stud1_id INT;
    v_stud2_id INT;
    v_session_id INT;
    v_date DATE;
    v_status_present INT;
    v_status_absent INT;
    v_status_late INT;
BEGIN
    SELECT user_id INTO v_fac1_id FROM Users WHERE username = 'fac1';
    SELECT user_id INTO v_stud1_id FROM Users WHERE username = 'stud1';
    SELECT user_id INTO v_stud2_id FROM Users WHERE username = 'stud2';
    
    SELECT s.section_id INTO v_cs101_sec_id FROM Sections s JOIN Courses c ON s.course_id = c.course_id WHERE c.course_code = 'CS101' LIMIT 1;
    SELECT s.section_id INTO v_cs201_sec_id FROM Sections s JOIN Courses c ON s.course_id = c.course_id WHERE c.course_code = 'CS201' LIMIT 1;
    
    SELECT status_id INTO v_status_present FROM AttendanceStatus WHERE status_name = 'Present';
    SELECT status_id INTO v_status_absent FROM AttendanceStatus WHERE status_name = 'Absent';
    SELECT status_id INTO v_status_late FROM AttendanceStatus WHERE status_name = 'Late';

    -- Generate 25 sessions for CS101
    FOR i IN 1..25 LOOP
        v_date := '2026-09-01'::DATE + (i * 2);
        INSERT INTO AttendanceSessions (section_id, session_date, start_time, end_time, created_by)
        VALUES (v_cs101_sec_id, v_date, '09:00:00', '10:30:00', v_fac1_id)
        RETURNING session_id INTO v_session_id;

        -- stud1 (Mostly Present, some Late)
        INSERT INTO StudentAttendance (session_id, student_id, status_id)
        VALUES (v_session_id, v_stud1_id, CASE WHEN i % 5 = 0 THEN v_status_late ELSE v_status_present END);

        -- stud2 (Mix of Present and Absent)
        INSERT INTO StudentAttendance (session_id, student_id, status_id)
        VALUES (v_session_id, v_stud2_id, CASE WHEN i % 4 = 0 THEN v_status_absent ELSE v_status_present END);
    END LOOP;

    -- Generate 25 sessions for CS201
    FOR i IN 1..25 LOOP
        v_date := '2026-09-02'::DATE + (i * 2);
        INSERT INTO AttendanceSessions (section_id, session_date, start_time, end_time, created_by)
        VALUES (v_cs201_sec_id, v_date, '11:00:00', '12:30:00', v_fac1_id)
        RETURNING session_id INTO v_session_id;

        -- stud1 is enrolled in CS201, stud2 is not.
        INSERT INTO StudentAttendance (session_id, student_id, status_id)
        VALUES (v_session_id, v_stud1_id, CASE WHEN i % 7 = 0 THEN v_status_absent WHEN i % 3 = 0 THEN v_status_late ELSE v_status_present END);
    END LOOP;
END $$;
