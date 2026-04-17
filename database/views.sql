-- ==================================================
-- ATTENDIFY - Views
-- ==================================================

-- 1. View: Student Attendance Report
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
FROM Students s
JOIN Users u ON s.student_id = u.user_id
JOIN Enrollments e ON s.student_id = e.student_id
JOIN Sections sec ON e.section_id = sec.section_id
JOIN Courses c ON sec.course_id = c.course_id;

-- 2. View: Low Attendance Students (< 75%)
CREATE OR REPLACE VIEW low_attendance_students AS
SELECT * 
FROM student_attendance_report
WHERE attendance_percentage < 75.0;

-- 3. View: Detailed Session View
CREATE OR REPLACE VIEW session_details_view AS
SELECT 
    sess.session_id,
    sess.session_date,
    sess.start_time,
    sess.end_time,
    c.course_code,
    c.course_name,
    f.first_name AS faculty_first_name,
    f.last_name AS faculty_last_name
FROM AttendanceSessions sess
JOIN Sections sec ON sess.section_id = sec.section_id
JOIN Courses c ON sec.course_id = c.course_id
LEFT JOIN Faculty f ON sess.created_by = f.faculty_id;
