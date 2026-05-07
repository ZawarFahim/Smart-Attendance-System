-- 02_constraints.sql
-- Foreign keys and Check constraints

ALTER TABLE Users ADD CONSTRAINT chk_role CHECK (role IN ('Admin', 'Faculty', 'Student'));

ALTER TABLE Students ADD CONSTRAINT fk_students_users FOREIGN KEY (student_id) REFERENCES Users(user_id) ON DELETE CASCADE;
ALTER TABLE Students ADD CONSTRAINT fk_students_dept FOREIGN KEY (dept_id) REFERENCES Departments(dept_id) ON DELETE SET NULL;

ALTER TABLE Faculty ADD CONSTRAINT fk_faculty_users FOREIGN KEY (faculty_id) REFERENCES Users(user_id) ON DELETE CASCADE;
ALTER TABLE Faculty ADD CONSTRAINT fk_faculty_dept FOREIGN KEY (dept_id) REFERENCES Departments(dept_id) ON DELETE SET NULL;

ALTER TABLE Courses ADD CONSTRAINT chk_credits CHECK (credits > 0);
ALTER TABLE Courses ADD CONSTRAINT fk_courses_dept FOREIGN KEY (dept_id) REFERENCES Departments(dept_id) ON DELETE CASCADE;

ALTER TABLE Rooms ADD CONSTRAINT chk_capacity CHECK (capacity > 0);

ALTER TABLE Sections ADD CONSTRAINT fk_sections_course FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE;
ALTER TABLE Sections ADD CONSTRAINT fk_sections_faculty FOREIGN KEY (faculty_id) REFERENCES Faculty(faculty_id) ON DELETE SET NULL;
ALTER TABLE Sections ADD CONSTRAINT fk_sections_room FOREIGN KEY (room_id) REFERENCES Rooms(room_id) ON DELETE SET NULL;
ALTER TABLE Sections ADD CONSTRAINT uq_section_details UNIQUE (course_id, faculty_id, semester, academic_year);

ALTER TABLE Enrollments ADD CONSTRAINT fk_enroll_student FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE;
ALTER TABLE Enrollments ADD CONSTRAINT fk_enroll_section FOREIGN KEY (section_id) REFERENCES Sections(section_id) ON DELETE CASCADE;
ALTER TABLE Enrollments ADD CONSTRAINT uq_enrollment UNIQUE (student_id, section_id);

ALTER TABLE AttendanceSessions ADD CONSTRAINT fk_sess_section FOREIGN KEY (section_id) REFERENCES Sections(section_id) ON DELETE CASCADE;
ALTER TABLE AttendanceSessions ADD CONSTRAINT fk_sess_creator FOREIGN KEY (created_by) REFERENCES Faculty(faculty_id) ON DELETE SET NULL;
ALTER TABLE AttendanceSessions ADD CONSTRAINT chk_sess_time CHECK (end_time > start_time);
ALTER TABLE AttendanceSessions ADD CONSTRAINT uq_session UNIQUE (section_id, session_date, start_time);

ALTER TABLE StudentAttendance ADD CONSTRAINT fk_sa_session FOREIGN KEY (session_id) REFERENCES AttendanceSessions(session_id) ON DELETE CASCADE;
ALTER TABLE StudentAttendance ADD CONSTRAINT fk_sa_student FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE;
ALTER TABLE StudentAttendance ADD CONSTRAINT fk_sa_status FOREIGN KEY (status_id) REFERENCES AttendanceStatus(status_id);
ALTER TABLE StudentAttendance ADD CONSTRAINT uq_sa_record UNIQUE (session_id, student_id);

ALTER TABLE FacultyAttendance ADD CONSTRAINT fk_fa_faculty FOREIGN KEY (faculty_id) REFERENCES Faculty(faculty_id) ON DELETE CASCADE;
ALTER TABLE FacultyAttendance ADD CONSTRAINT fk_fa_status FOREIGN KEY (status_id) REFERENCES AttendanceStatus(status_id);
ALTER TABLE FacultyAttendance ADD CONSTRAINT uq_fa_record UNIQUE (faculty_id, date);

ALTER TABLE Timetable ADD CONSTRAINT fk_tt_section FOREIGN KEY (section_id) REFERENCES Sections(section_id) ON DELETE CASCADE;
ALTER TABLE Timetable ADD CONSTRAINT fk_tt_room FOREIGN KEY (room_id) REFERENCES Rooms(room_id) ON DELETE SET NULL;
ALTER TABLE Timetable ADD CONSTRAINT chk_tt_day CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'));
ALTER TABLE Timetable ADD CONSTRAINT chk_tt_time CHECK (end_time > start_time);
ALTER TABLE Timetable ADD CONSTRAINT uq_tt_slot UNIQUE (section_id, day_of_week, start_time);

ALTER TABLE ExamTimetable ADD CONSTRAINT fk_exam_course FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE;
ALTER TABLE ExamTimetable ADD CONSTRAINT fk_exam_room FOREIGN KEY (room_id) REFERENCES Rooms(room_id) ON DELETE SET NULL;
ALTER TABLE ExamTimetable ADD CONSTRAINT chk_exam_type CHECK (exam_type IN ('Midterm', 'Final', 'Quiz', 'Lab'));
ALTER TABLE ExamTimetable ADD CONSTRAINT chk_exam_time CHECK (end_time > start_time);

ALTER TABLE LeaveRequests ADD CONSTRAINT fk_leave_user FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE;
ALTER TABLE LeaveRequests ADD CONSTRAINT fk_leave_reviewer FOREIGN KEY (reviewed_by) REFERENCES Users(user_id) ON DELETE SET NULL;
ALTER TABLE LeaveRequests ADD CONSTRAINT chk_leave_status CHECK (status IN ('Pending', 'Approved', 'Rejected'));

ALTER TABLE Notifications ADD CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE;

ALTER TABLE AuditLogs ADD CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL;
