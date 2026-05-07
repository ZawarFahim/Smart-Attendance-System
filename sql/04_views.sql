-- 04_views.sql
CREATE OR REPLACE VIEW student_attendance_report AS
SELECT 
    s.student_id,
    u.username,
    s.first_name,
    s.last_name,
    c.course_code,
    c.course_name,
    COALESCE((SUM(CASE WHEN st.status_name IN ('Present', 'Late') THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(sa.attendance_id), 0), 0) AS attendance_percentage
FROM Students s
JOIN Users u ON s.student_id = u.user_id
JOIN Enrollments e ON s.student_id = e.student_id
JOIN Sections sec ON e.section_id = sec.section_id
JOIN Courses c ON sec.course_id = c.course_id
LEFT JOIN AttendanceSessions sess ON sess.section_id = sec.section_id
LEFT JOIN StudentAttendance sa ON sess.session_id = sa.session_id AND sa.student_id = s.student_id
LEFT JOIN AttendanceStatus st ON sa.status_id = st.status_id
GROUP BY s.student_id, u.username, s.first_name, s.last_name, c.course_code, c.course_name;

CREATE OR REPLACE VIEW low_attendance_students AS
SELECT * FROM student_attendance_report WHERE attendance_percentage < 75;

CREATE OR REPLACE VIEW faculty_workload_report AS
WITH WorkloadCTE AS (
    SELECT 
        f.faculty_id,
        f.first_name,
        f.last_name,
        COUNT(sec.section_id) as total_sections,
        SUM(c.credits) as total_credits
    FROM Faculty f
    JOIN Sections sec ON f.faculty_id = sec.faculty_id
    JOIN Courses c ON sec.course_id = c.course_id
    GROUP BY f.faculty_id, f.first_name, f.last_name
)
SELECT 
    *,
    RANK() OVER (ORDER BY total_credits DESC) as workload_rank
FROM WorkloadCTE;

CREATE OR REPLACE VIEW department_attendance_ranking AS
SELECT 
    d.dept_name,
    c.course_code,
    c.course_name,
    COUNT(sa.attendance_id) AS total_attendance_records,
    SUM(CASE WHEN st.status_name IN ('Present', 'Late') THEN 1 ELSE 0 END) AS total_present,
    COALESCE((SUM(CASE WHEN st.status_name IN ('Present', 'Late') THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(sa.attendance_id), 0), 0) AS dept_course_attendance_percentage,
    RANK() OVER (PARTITION BY d.dept_id ORDER BY COALESCE((SUM(CASE WHEN st.status_name IN ('Present', 'Late') THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(sa.attendance_id), 0), 0) DESC) AS rank_in_dept
FROM Departments d
JOIN Courses c ON d.dept_id = c.dept_id
JOIN Sections sec ON c.course_id = sec.course_id
JOIN AttendanceSessions sess ON sec.section_id = sess.section_id
JOIN StudentAttendance sa ON sess.session_id = sa.session_id
JOIN AttendanceStatus st ON sa.status_id = st.status_id
GROUP BY d.dept_id, d.dept_name, c.course_code, c.course_name;

CREATE OR REPLACE VIEW student_attendance_trends AS
SELECT 
    sa.student_id,
    sess.section_id,
    sess.session_date,
    st.status_name,
    LAG(st.status_name) OVER (PARTITION BY sa.student_id, sess.section_id ORDER BY sess.session_date) AS previous_status
FROM StudentAttendance sa
JOIN AttendanceSessions sess ON sa.session_id = sess.session_id
JOIN AttendanceStatus st ON sa.status_id = st.status_id;
