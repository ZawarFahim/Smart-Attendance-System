# ATTENDIFY - Smart Attendance Management System

ATTENDIFY is a robust, modular, and enterprise-grade Python application for managing student attendance, faculty schedules, and administrative reporting. Built according to clean architecture, it separates Database functionality, Service logic bridging, and User Interface management into distinct components.

## Features Required By the Spec
- 100% Python with `Tkinter` (ttk) for the UI.
- `PostgreSQL` Database interaction using `psycopg2`.
- Advanced SQL Triggers, Stored Procedures, and Views.
- Complete modular setup.
- Login validation & Role-based Dashboards (Admin / Faculty / Student).
- **Data Analytics**: Visual reporting via `matplotlib`.
- **Data Export**: Export to CSV using `pandas`.
- **Modern UI**: Sleek, modern Windows-11 style interface with Dark/Light mode support powered by `sv-ttk`.
- **System Broadcasts**: Admin panel for broadcasting important updates to specific roles.

## System Requirements
- Python 3.9+
- PostgreSQL 12+

## Installation & Setup

1. **Clone the Repository (or navigate to workspace):**
   ```bash
   cd "ATTENDIFY – Smart Attendance Management System"
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup:**
   Ensure your local PostgreSQL server is running.
   Create an empty database named `attendify`.
   Run the SQL files located in `/database` in this order (e.g., using `psql`, pgAdmin, or DBeaver):
   - `schema.sql`
   - `procedures.sql`
   - `triggers.sql`
   - `views.sql`
   - `seed.sql`

   *(Update `database.ini` credentials to match your PostgreSQL instance configuration if different from the default).*
   
   **One-click reset option (pgAdmin):**
   - Run `database/master_reset.sql` to perform full reset + setup in one script.

4. **Launch Application:**
   ```bash
   python main.py
   ```

## Seed Accounts For Testing
All seeded accounts use login text matching their stored hashed equivalents (e.g., plaintext configured in early run setup):
- **Admin**: Email: `admin@attendify.edu` | Pass: `admin123`
- **Faculty**: Email: `faculty1@attendify.edu` | Pass: `fac123`
- **Student**: Email: `student1@attendify.edu` | Pass: `stud123`

## Architecture Highlights
- `config/`: Configurations for database parsing and centralized GUI styling constants.
- `database/`: Raw SQL for tables (fully normalized 3NF), views, multi-insert functions.
- `utils/`: Data validation tools.
- `services/`: Business abstractions to decouple UI directly from db context.
- `gui/`: Interactive nested Tkinter elements broken into hierarchical dashboards per role.

---

## Database Normalization (1NF → 2NF → 3NF)

The schema is fully compliant with **Third Normal Form (3NF)**. Evidence:

### First Normal Form (1NF) ✅
- Every table has a **primary key** (`SERIAL PRIMARY KEY`).
- All columns store **atomic values** — no repeating groups or multi-valued cells.
- Example: a student's department is stored as a single `dept_id` FK, not a comma-separated list.

### Second Normal Form (2NF) ✅
_(Applies to tables with composite primary keys)_
- `StudentAttendance` has composite key `(session_id, student_id)`.  
  - `status_id` and `remarks` depend on the **full composite key**, not on just one part of it. ✅
- `Enrollments` has composite key `(student_id, section_id)`.  
  - `enrolled_date` depends on the full key (when that specific student enrolled in that specific section). ✅
- No partial dependencies exist anywhere.

### 6. Backup & Restore
To backup the database using `pg_dump`:
```bash
pg_dump -U postgres -d attendify -F c -f attendify_backup.dump
```
To restore it to a fresh instance:
```bash
pg_restore -U postgres -d attendify -1 attendify_backup.dump
```

---

## New Feature Walkthroughs

### A. Prerequisite Course Enrollment System

**Database design**

- `CoursePrerequisites` captures many-to-many course dependencies.
- `CourseResultStatuses` and `StudentCourseResults` record course-level outcomes per student.
- A trigger (`trg_validate_prereq_enrollment`) ensures that an `INSERT` into `Enrollments` is rejected if required prerequisites are not completed.
- Stored procedures:
  - `enroll_student_in_section(student_id, section_id)`
  - `record_student_course_result(student_id, course_id, status_code, recorded_by, notes)`
- Views:
  - `course_prerequisite_map`
  - `student_course_prerequisite_status`
  - `eligible_sections_for_student`
  - `blocked_enrollments_for_student`

**Service layer**

- `services/user_service.py`:
  - `add_enrollment` now calls `CALL enroll_student_in_section` for transaction-safe, trigger-validated enrollment.
  - `get_eligible_sections_for_student(student_id)` reads from the eligibility view.
- `services/report_service.py`:
  - `get_course_prerequisite_map()`
  - `get_student_prerequisite_status(student_id)`
  - `get_eligible_sections_for_student(student_id)`
  - `get_blocked_enrollments_for_student(student_id)`

**GUI**

- **Admin Dashboard** → **Prereqs & Enrollment**:
  - Tab *Course Prerequisite Map*: lists each course and its prerequisites.
  - Tab *Enrollments*: searchable table of enrollments plus a small form (`Student ID`, `Section ID`) that uses the stored procedure for enrollment; blocked enrollments (due to missing prerequisites) are surfaced as validation errors.
- **Student Dashboard** → **Course Eligibility**:
  - Tab *Prerequisite Status*: shows, per course, the number of prerequisites, how many are completed, and whether the student is currently eligible.
  - Tab *Eligible Sections*: lists sections the student can safely enroll in (all prerequisites satisfied).
  - Tab *Blocked Enrollments*: lists sections blocked, along with a comma-separated list of missing prerequisite course codes.

The entire flow is transaction-safe and enforced at the database level, demonstrating the use of triggers, procedures, views, subqueries, and aggregate queries.

### B. Faculty Workload Analyzer

**Database design**

- View `faculty_workload_report` extended to include:
  - `weekly_teaching_hours`
  - `weekly_class_slots`
  - Window function `RANK()` for ranking by total credits.
- New views:
  - `faculty_workload_semester_summary` (per faculty, per semester/year).
  - `faculty_monthly_class_sessions_summary` (per faculty, per calendar month).

**Service layer**

- `services/report_service.py`:
  - `get_faculty_workload_report()`
  - `get_faculty_workload_semester_summary()`
  - `get_faculty_monthly_sessions()`

**GUI**

- **Admin Dashboard** → **Analytics**:
  - Tab *Faculty Workload (Ranked)*: enhanced table including weekly hours and class slots.
  - Tab *Workload by Semester*: workload summary per faculty and semester.
  - Tab *Monthly Faculty Sessions*: monthly class sessions per faculty.
- **Faculty Dashboard** → **My Workload**:
  - Tab *Overall Workload*: shows the logged-in faculty member’s total sections, credits, weekly hours, slots, and rank.
  - Tab *By Semester*: their workload split by semester.
  - Tab *Monthly Sessions*: how many sessions they created each month and across how many sections.

These pages make heavy use of `GROUP BY`, `HAVING`, window functions, and optimized JOINs with composite indexes.

### C. Attendance Freeze & Archive System

**Database design**

- `AttendancePolicies(policy_id, freeze_minutes, archive_after_days)` controls:
  - How long after a session’s end time attendance editing is allowed.
  - When old semesters should be archived.
- `AttendanceEditOverrides` allows admins to grant session- or student-specific overrides.
- `AttendanceSessionsArchive` and `StudentAttendanceArchive` store historical snapshots of sessions and attendance.
- `AttendanceEditAudit` records post-freeze edits (who changed what and when).
- Triggers:
  - `trg_attendance_freeze_guard` (via `enforce_attendance_freeze`) blocks edits past the freeze deadline unless an override exists.
  - `trg_audit_student_attendance_update` records every status/remark change after the fact.
- Procedure:
  - `archive_attendance_for_semester(semester, academic_year, archived_by, reason)` moves data into the archive tables within a transaction.
- Unified history view:
  - `student_attendance_history_all` returns both current and archived rows with a `source` flag.

**Service layer**

- `services/attendance_service.py`:
  - `get_attendance_history_all(student_id)` aggregates current + archived history.
  - `archive_attendance_for_semester(semester, academic_year, archived_by, reason)` calls the stored procedure.

**GUI**

- **Admin Dashboard** → **Attendance Archive**:
  - Simple form to select `Semester`, `Academic Year`, and an optional `Reason`.
  - Button *Archive Attendance* calls `archive_attendance_for_semester` and shows success/failure.
- **Faculty Dashboard**:
  - `Mark Attendance` now warns that failed saves may be caused by the freeze policy.
  - `My Workload` and `Session History` help faculty understand their teaching load over time.
- **Student Dashboard**:
  - `My Attendance` now uses `get_attendance_history_all`, showing whether each row came from the *current* or *archive* tables.

This subsystem demonstrates transactions, triggers, procedures, archive tables, and temporal data management in PostgreSQL.

### D. Flowcharts & ERD (for your report)

You can use the following textual flows as a basis for diagrams in your project report:

- **Enrollment Flow**:  
  Student Dashboard → *Course Eligibility* → choose section → Admin Dashboard / backend calls `enroll_student_in_section` → DB trigger `validate_prerequisites_for_enrollment` → either INSERT into `Enrollments` or error with missing prerequisites.

- **Workload Flow**:  
  Faculty / Sections / Timetable / AttendanceSessions → PostgreSQL views (`faculty_workload_report`, `faculty_workload_semester_summary`, `faculty_monthly_class_sessions_summary`) → `report_service` → Admin and Faculty dashboards.

- **Attendance Archive Flow**:  
  Admin Dashboard → *Attendance Archive* → call `archive_attendance_for_semester` → rows moved from `AttendanceSessions`/`StudentAttendance` to archive tables → history consumed via `student_attendance_history_all` in Student/Faculty dashboards.

### E. Firebase Backup & Restore Integration

**Configuration**:
- The project integrates `firebase-admin` and `python-dotenv`.
- Place your `serviceAccountKey.json` inside `config/firebase/` (refer to `firebase_config.json.example`).
- Create a `.env` file based on `.env.example` to define the credentials path.

**Capabilities**:
- Admin Dashboard -> *Firebase Sync*
- **Backup**: Syncs all essential PostgreSQL tables to Firestore collections, properly mirroring the schemas.
- **Restore**: Pulls documents from Firestore and inserts them back into PostgreSQL using `ON CONFLICT DO NOTHING` to prevent duplicates.
- All errors are captured and reported safely without crashing the UI.

### F. Student Profile Image Storage (3NF)

**Database design**
- `StudentProfileImages(image_id, student_id, image_name, image_path, upload_timestamp)`
- Ensures 3NF compliance (each image explicitly depends on the `image_id` PK, with a unique FK to `student_id` for 1:1 mapping).
- Stored Procedure: `upsert_student_profile_image(student_id, image_name, image_path)` uses PostgreSQL's `ON CONFLICT DO UPDATE` to gracefully handle new uploads or replacements.

**Functionality**:
- Images are saved locally inside `uploads/student_profiles/`.
- Pillow (`PIL`) is used to automatically resize large profile images to maximum 500x500 pixels.
- The Student Dashboard now features a *My Profile* tab allowing students to upload and view their profile images.


