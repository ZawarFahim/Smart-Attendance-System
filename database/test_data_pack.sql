-- ==================================================
-- ATTENDIFY - Extended Test Data Pack
-- Run this AFTER database/master_reset.sql
-- ==================================================

BEGIN;

-- --------------------------------------------------
-- Extra departments
-- --------------------------------------------------
INSERT INTO Departments (dept_name)
VALUES
('Physics'),
('Business Administration')
ON CONFLICT (dept_name) DO NOTHING;

-- --------------------------------------------------
-- Extra users (plaintext passwords by current project logic)
-- --------------------------------------------------
INSERT INTO Users (username, email, password_hash, role) VALUES
('admin2', 'admin2@attendify.edu', 'admin234', 'Admin'),
('fac2', 'faculty2@attendify.edu', 'fac234', 'Faculty'),
('fac3', 'faculty3@attendify.edu', 'fac345', 'Faculty'),
('stud3', 'student3@attendify.edu', 'stud333', 'Student'),
('stud4', 'student4@attendify.edu', 'stud444', 'Student'),
('stud5', 'student5@attendify.edu', 'stud555', 'Student')
ON CONFLICT (username) DO NOTHING;

-- --------------------------------------------------
-- Faculty profile rows
-- --------------------------------------------------
INSERT INTO Faculty (faculty_id, first_name, last_name, dept_id)
SELECT u.user_id, 'Dr. Bob', 'Martin', d.dept_id
FROM Users u
JOIN Departments d ON d.dept_name = 'Computer Science'
WHERE u.username = 'fac2'
ON CONFLICT (faculty_id) DO NOTHING;

INSERT INTO Faculty (faculty_id, first_name, last_name, dept_id)
SELECT u.user_id, 'Dr. Clara', 'Nguyen', d.dept_id
FROM Users u
JOIN Departments d ON d.dept_name = 'Information Technology'
WHERE u.username = 'fac3'
ON CONFLICT (faculty_id) DO NOTHING;

-- --------------------------------------------------
-- Student profile rows
-- --------------------------------------------------
INSERT INTO Students (student_id, first_name, last_name, dept_id)
SELECT u.user_id, 'Mark', 'Taylor', d.dept_id
FROM Users u
JOIN Departments d ON d.dept_name = 'Computer Science'
WHERE u.username = 'stud3'
ON CONFLICT (student_id) DO NOTHING;

INSERT INTO Students (student_id, first_name, last_name, dept_id)
SELECT u.user_id, 'Priya', 'Sharma', d.dept_id
FROM Users u
JOIN Departments d ON d.dept_name = 'Information Technology'
WHERE u.username = 'stud4'
ON CONFLICT (student_id) DO NOTHING;

INSERT INTO Students (student_id, first_name, last_name, dept_id)
SELECT u.user_id, 'Amina', 'Khan', d.dept_id
FROM Users u
JOIN Departments d ON d.dept_name = 'Mathematics'
WHERE u.username = 'stud5'
ON CONFLICT (student_id) DO NOTHING;

-- --------------------------------------------------
-- Extra courses and rooms
-- --------------------------------------------------
INSERT INTO Courses (course_code, course_name, credits, dept_id)
SELECT 'CS301', 'Algorithms', 4, d.dept_id
FROM Departments d WHERE d.dept_name = 'Computer Science'
ON CONFLICT (course_code) DO NOTHING;

INSERT INTO Courses (course_code, course_name, credits, dept_id)
SELECT 'IT305', 'Cloud Computing', 3, d.dept_id
FROM Departments d WHERE d.dept_name = 'Information Technology'
ON CONFLICT (course_code) DO NOTHING;

INSERT INTO Courses (course_code, course_name, credits, dept_id)
SELECT 'MTH210', 'Linear Algebra', 3, d.dept_id
FROM Departments d WHERE d.dept_name = 'Mathematics'
ON CONFLICT (course_code) DO NOTHING;

INSERT INTO Rooms (room_name, capacity) VALUES
('Room 103', 55),
('Room 104', 45),
('Lab B', 35)
ON CONFLICT (room_name) DO NOTHING;

-- --------------------------------------------------
-- Extra sections
-- --------------------------------------------------
INSERT INTO Sections (course_id, faculty_id, room_id, semester, academic_year)
SELECT c.course_id, f.faculty_id, r.room_id, 'Spring', '2026-2027'
FROM Courses c
JOIN Faculty f ON f.faculty_id = (SELECT user_id FROM Users WHERE username = 'fac2')
JOIN Rooms r ON r.room_name = 'Room 103'
WHERE c.course_code = 'CS301'
ON CONFLICT (course_id, faculty_id, semester, academic_year) DO NOTHING;

INSERT INTO Sections (course_id, faculty_id, room_id, semester, academic_year)
SELECT c.course_id, f.faculty_id, r.room_id, 'Spring', '2026-2027'
FROM Courses c
JOIN Faculty f ON f.faculty_id = (SELECT user_id FROM Users WHERE username = 'fac3')
JOIN Rooms r ON r.room_name = 'Lab B'
WHERE c.course_code = 'IT305'
ON CONFLICT (course_id, faculty_id, semester, academic_year) DO NOTHING;

INSERT INTO Sections (course_id, faculty_id, room_id, semester, academic_year)
SELECT c.course_id, f.faculty_id, r.room_id, 'Spring', '2026-2027'
FROM Courses c
JOIN Faculty f ON f.faculty_id = (SELECT user_id FROM Users WHERE username = 'fac2')
JOIN Rooms r ON r.room_name = 'Room 104'
WHERE c.course_code = 'MTH210'
ON CONFLICT (course_id, faculty_id, semester, academic_year) DO NOTHING;

-- --------------------------------------------------
-- Enrollments (mix old and new students)
-- --------------------------------------------------
INSERT INTO Enrollments (student_id, section_id)
SELECT (SELECT user_id FROM Users WHERE username = 'stud1'),
       s.section_id
FROM Sections s
JOIN Courses c ON c.course_id = s.course_id
WHERE c.course_code = 'CS301'
ON CONFLICT (student_id, section_id) DO NOTHING;

INSERT INTO Enrollments (student_id, section_id)
SELECT (SELECT user_id FROM Users WHERE username = 'stud3'),
       s.section_id
FROM Sections s
JOIN Courses c ON c.course_id = s.course_id
WHERE c.course_code = 'CS301'
ON CONFLICT (student_id, section_id) DO NOTHING;

INSERT INTO Enrollments (student_id, section_id)
SELECT (SELECT user_id FROM Users WHERE username = 'stud4'),
       s.section_id
FROM Sections s
JOIN Courses c ON c.course_id = s.course_id
WHERE c.course_code = 'IT305'
ON CONFLICT (student_id, section_id) DO NOTHING;

INSERT INTO Enrollments (student_id, section_id)
SELECT (SELECT user_id FROM Users WHERE username = 'stud5'),
       s.section_id
FROM Sections s
JOIN Courses c ON c.course_id = s.course_id
WHERE c.course_code = 'MTH210'
ON CONFLICT (student_id, section_id) DO NOTHING;

-- --------------------------------------------------
-- Timetable rows for new sections
-- --------------------------------------------------
INSERT INTO Timetable (section_id, day_of_week, start_time, end_time, room_id)
SELECT s.section_id, 'Monday', '13:00', '14:30', s.room_id
FROM Sections s
JOIN Courses c ON c.course_id = s.course_id
WHERE c.course_code = 'CS301'
ON CONFLICT DO NOTHING;

INSERT INTO Timetable (section_id, day_of_week, start_time, end_time, room_id)
SELECT s.section_id, 'Thursday', '15:00', '16:30', s.room_id
FROM Sections s
JOIN Courses c ON c.course_id = s.course_id
WHERE c.course_code = 'IT305'
ON CONFLICT DO NOTHING;

INSERT INTO Timetable (section_id, day_of_week, start_time, end_time, room_id)
SELECT s.section_id, 'Friday', '10:00', '11:30', s.room_id
FROM Sections s
JOIN Courses c ON c.course_id = s.course_id
WHERE c.course_code = 'MTH210'
ON CONFLICT DO NOTHING;

-- --------------------------------------------------
-- Attendance sessions + records
-- --------------------------------------------------
INSERT INTO AttendanceSessions (section_id, session_date, start_time, end_time, created_by)
SELECT s.section_id, DATE '2026-04-10', '13:00', '14:00', s.faculty_id
FROM Sections s
JOIN Courses c ON c.course_id = s.course_id
WHERE c.course_code = 'CS301'
ON CONFLICT (section_id, session_date, start_time) DO NOTHING;

INSERT INTO AttendanceSessions (section_id, session_date, start_time, end_time, created_by)
SELECT s.section_id, DATE '2026-04-12', '15:00', '16:00', s.faculty_id
FROM Sections s
JOIN Courses c ON c.course_id = s.course_id
WHERE c.course_code = 'IT305'
ON CONFLICT (section_id, session_date, start_time) DO NOTHING;

INSERT INTO StudentAttendance (session_id, student_id, status_id, remarks)
SELECT sess.session_id, e.student_id, st.status_id, 'Auto test data'
FROM AttendanceSessions sess
JOIN Sections sec ON sec.section_id = sess.section_id
JOIN Courses c ON c.course_id = sec.course_id
JOIN Enrollments e ON e.section_id = sec.section_id
JOIN AttendanceStatus st ON st.status_name = 'Present'
WHERE c.course_code = 'CS301'
ON CONFLICT (session_id, student_id) DO NOTHING;

INSERT INTO StudentAttendance (session_id, student_id, status_id, remarks)
SELECT sess.session_id, e.student_id, st.status_id, 'Auto test data'
FROM AttendanceSessions sess
JOIN Sections sec ON sec.section_id = sess.section_id
JOIN Courses c ON c.course_id = sec.course_id
JOIN Enrollments e ON e.section_id = sec.section_id
JOIN AttendanceStatus st ON st.status_name = 'Late'
WHERE c.course_code = 'IT305'
ON CONFLICT (session_id, student_id) DO NOTHING;

-- --------------------------------------------------
-- Leave requests + notifications
-- --------------------------------------------------
INSERT INTO LeaveRequests (user_id, start_date, end_date, reason, status, reviewed_by)
VALUES
((SELECT user_id FROM Users WHERE username = 'stud3'), DATE '2026-05-01', DATE '2026-05-03', 'Medical leave', 'Pending', NULL),
((SELECT user_id FROM Users WHERE username = 'fac2'), DATE '2026-05-10', DATE '2026-05-12', 'Conference travel', 'Approved', (SELECT user_id FROM Users WHERE username = 'admin1')),
((SELECT user_id FROM Users WHERE username = 'stud4'), DATE '2026-05-15', DATE '2026-05-16', 'Family event', 'Rejected', (SELECT user_id FROM Users WHERE username = 'admin1'));

INSERT INTO Notifications (user_id, message, is_read)
VALUES
((SELECT user_id FROM Users WHERE username = 'stud4'), 'Your leave request was rejected.', FALSE),
((SELECT user_id FROM Users WHERE username = 'fac2'), 'Your leave request was approved.', FALSE),
((SELECT user_id FROM Users WHERE username = 'stud3'), 'Reminder: your leave request is pending review.', FALSE);

COMMIT;
