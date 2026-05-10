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
        SUM(c.credits) as total_credits,
        -- Weekly teaching hours based on recurring timetable slots
        COALESCE(SUM(
            EXTRACT(EPOCH FROM (t.end_time - t.start_time)) / 3600.0
        ), 0) AS weekly_teaching_hours,
        COALESCE(COUNT(t.timetable_id), 0) AS weekly_class_slots
    FROM Faculty f
    JOIN Sections sec ON f.faculty_id = sec.faculty_id
    JOIN Courses c ON sec.course_id = c.course_id
    LEFT JOIN Timetable t ON t.section_id = sec.section_id AND COALESCE(t.is_recurring, TRUE) = TRUE
    GROUP BY f.faculty_id, f.first_name, f.last_name
)
SELECT 
    *,
    RANK() OVER (ORDER BY total_credits DESC) as workload_rank
FROM WorkloadCTE;

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 2: FACULTY WORKLOAD ANALYZER (semester + monthly summaries)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE VIEW faculty_workload_semester_summary AS
SELECT
    f.faculty_id,
    f.first_name,
    f.last_name,
    sec.semester,
    sec.academic_year,
    COUNT(DISTINCT sec.section_id) AS total_sections,
    COUNT(DISTINCT sec.course_id) AS total_courses,
    COALESCE(SUM(DISTINCT c.credits), 0) AS distinct_course_credits,
    COALESCE(SUM(EXTRACT(EPOCH FROM (t.end_time - t.start_time)) / 3600.0), 0) AS weekly_teaching_hours,
    COUNT(t.timetable_id) AS weekly_class_slots
FROM Faculty f
JOIN Sections sec ON f.faculty_id = sec.faculty_id
JOIN Courses c ON sec.course_id = c.course_id
LEFT JOIN Timetable t ON t.section_id = sec.section_id AND COALESCE(t.is_recurring, TRUE) = TRUE
GROUP BY f.faculty_id, f.first_name, f.last_name, sec.semester, sec.academic_year;

CREATE OR REPLACE VIEW faculty_monthly_class_sessions_summary AS
SELECT
    sess.created_by AS faculty_id,
    DATE_TRUNC('month', (sess.session_date::timestamp))::date AS month_start,
    COUNT(*) AS total_sessions_created,
    COUNT(DISTINCT sess.section_id) AS distinct_sections
FROM AttendanceSessions sess
GROUP BY sess.created_by, DATE_TRUNC('month', (sess.session_date::timestamp))::date
HAVING COUNT(*) > 0;

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 1: PREREQUISITE ENROLLMENT REPORTING
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE VIEW course_prerequisite_map AS
SELECT
    c.course_id,
    c.course_code,
    c.course_name,
    p.prereq_course_id,
    pc.course_code AS prereq_course_code,
    pc.course_name AS prereq_course_name
FROM CoursePrerequisites p
JOIN Courses c ON c.course_id = p.course_id
JOIN Courses pc ON pc.course_id = p.prereq_course_id;



-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 3: ATTENDANCE HISTORY (current + archived)
-- ─────────────────────────────────────────────────────────────────────────────



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
