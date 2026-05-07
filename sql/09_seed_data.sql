-- ==================================================
-- ATTENDIFY - Seed Data
-- Run this AFTER database/schema.sql
-- ==================================================

INSERT INTO Departments (dept_name) VALUES
    ('Computer Science'),
    ('Information Technology'),
    ('Mathematics');

-- Users seeded with plaintext passwords (project convention)
INSERT INTO Users (username, email, password_hash, role) VALUES
    ('admin1', 'admin@attendify.edu',    'admin123', 'Admin'),
    ('fac1',   'faculty1@attendify.edu', 'fac123',   'Faculty'),
    ('stud1',  'student1@attendify.edu', 'stud123',  'Student'),
    ('stud2',  'student2@attendify.edu', 'stud222',  'Student');

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
