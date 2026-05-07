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

-- Per (student, course): prerequisite counts + eligibility flag (uses GROUP BY + HAVING pattern)
CREATE OR REPLACE VIEW student_course_prerequisite_status AS
SELECT
    s.student_id,
    c.course_id,
    c.course_code,
    c.course_name,
    COUNT(p.prereq_course_id) AS prereq_count,
    COALESCE(SUM(CASE WHEN crs.is_passing THEN 1 ELSE 0 END), 0) AS completed_prereq_count,
    CASE
        WHEN COUNT(p.prereq_course_id) = 0 THEN TRUE
        ELSE (COALESCE(SUM(CASE WHEN crs.is_passing THEN 1 ELSE 0 END), 0) = COUNT(p.prereq_course_id))
    END AS is_eligible
FROM Students s
CROSS JOIN Courses c
LEFT JOIN CoursePrerequisites p
    ON p.course_id = c.course_id
LEFT JOIN StudentCourseResults scr
    ON scr.student_id = s.student_id
   AND scr.course_id = p.prereq_course_id
LEFT JOIN CourseResultStatuses crs
    ON crs.status_code = scr.status_code
GROUP BY s.student_id, c.course_id, c.course_code, c.course_name;

-- Eligible sections for enrollment (excludes sections already enrolled by the student)
CREATE OR REPLACE VIEW eligible_sections_for_student AS
SELECT
    st.student_id,
    sec.section_id,
    sec.semester,
    sec.academic_year,
    c.course_id,
    c.course_code,
    c.course_name
FROM Students st
JOIN Sections sec ON TRUE
JOIN Courses c ON c.course_id = sec.course_id
JOIN student_course_prerequisite_status pcs
    ON pcs.student_id = st.student_id
   AND pcs.course_id = c.course_id
WHERE pcs.is_eligible = TRUE
  AND NOT EXISTS (
      SELECT 1
      FROM Enrollments e
      WHERE e.student_id = st.student_id
        AND e.section_id = sec.section_id
  );

-- Blocked enrollment report with missing prerequisite list (subquery + string_agg)
CREATE OR REPLACE VIEW blocked_enrollments_for_student AS
SELECT
    st.student_id,
    sec.section_id,
    sec.semester,
    sec.academic_year,
    c.course_code,
    c.course_name,
    (
        SELECT STRING_AGG(pc.course_code, ', ' ORDER BY pc.course_code)
        FROM CoursePrerequisites p
        JOIN Courses pc ON pc.course_id = p.prereq_course_id
        LEFT JOIN StudentCourseResults scr
            ON scr.student_id = st.student_id
           AND scr.course_id = p.prereq_course_id
        LEFT JOIN CourseResultStatuses crs
            ON crs.status_code = scr.status_code
        WHERE p.course_id = c.course_id
          AND COALESCE(crs.is_passing, FALSE) = FALSE
    ) AS missing_prerequisites
FROM Students st
JOIN Sections sec ON TRUE
JOIN Courses c ON c.course_id = sec.course_id
WHERE EXISTS (
    SELECT 1
    FROM CoursePrerequisites p
    WHERE p.course_id = c.course_id
)
AND NOT EXISTS (
    SELECT 1
    FROM student_course_prerequisite_status pcs
    WHERE pcs.student_id = st.student_id
      AND pcs.course_id = c.course_id
      AND pcs.is_eligible = TRUE
);

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 3: ATTENDANCE HISTORY (current + archived)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE VIEW student_attendance_history_all AS
SELECT
    sa.student_id,
    sess.section_id,
    sess.session_date,
    sess.start_time,
    sess.end_time,
    st.status_name,
    sa.remarks,
    'current'::text AS source
FROM StudentAttendance sa
JOIN AttendanceSessions sess ON sess.session_id = sa.session_id
JOIN AttendanceStatus st ON st.status_id = sa.status_id

UNION ALL

SELECT
    saa.student_id,
    asa.section_id,
    asa.session_date,
    asa.start_time,
    asa.end_time,
    st.status_name,
    saa.remarks,
    'archive'::text AS source
FROM StudentAttendanceArchive saa
JOIN AttendanceSessionsArchive asa ON asa.archive_session_id = saa.archive_session_id
JOIN AttendanceStatus st ON st.status_id = saa.status_id;

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
