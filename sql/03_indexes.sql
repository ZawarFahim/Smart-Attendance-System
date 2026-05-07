-- 03_indexes.sql
CREATE INDEX idx_student_dept ON Students(dept_id);
CREATE INDEX idx_faculty_dept ON Faculty(dept_id);
CREATE INDEX idx_sections_course ON Sections(course_id);
CREATE INDEX idx_enrollment_student ON Enrollments(student_id);
CREATE INDEX idx_enrollment_section ON Enrollments(section_id);
CREATE INDEX idx_attendance_session ON StudentAttendance(session_id);
CREATE INDEX idx_attendance_student ON StudentAttendance(student_id);
CREATE INDEX idx_timetable_section_day ON Timetable(section_id, day_of_week);
CREATE INDEX idx_exam_course_date ON ExamTimetable(course_id, exam_date);
CREATE INDEX idx_attendance_session_date ON AttendanceSessions(section_id, session_date);

-- Composite Index for Query Optimization demonstration
CREATE INDEX idx_sa_composite ON StudentAttendance(session_id, student_id);
CREATE INDEX idx_timetable_room_time ON Timetable(room_id, day_of_week, start_time, end_time);
CREATE INDEX idx_sections_faculty_time ON Sections(faculty_id, semester, academic_year);

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 1: PREREQUISITES + COURSE COMPLETION
-- Index strategy: accelerate prerequisite lookups and student completion checks
-- ─────────────────────────────────────────────────────────────────────────────
CREATE INDEX idx_prereq_by_prereq_course ON CoursePrerequisites(prereq_course_id);
CREATE INDEX idx_scr_by_course ON StudentCourseResults(course_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- FEATURE 3: FREEZE + ARCHIVE
-- Index strategy: optimize archive/report scans by time & ownership
-- ─────────────────────────────────────────────────────────────────────────────
CREATE INDEX idx_asa_section_date ON AttendanceSessionsArchive(section_id, session_date);
CREATE INDEX idx_saa_student ON StudentAttendanceArchive(student_id);
CREATE INDEX idx_aeo_session_student_valid ON AttendanceEditOverrides(session_id, student_id, valid_until);
CREATE INDEX idx_aea_session_student_time ON AttendanceEditAudit(session_id, student_id, changed_at);
