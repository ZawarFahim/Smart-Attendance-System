# ATTENDIFY - Smart Attendance Management System

A comprehensive, modular University Database Management System (DBMS) project. This project implements advanced PostgreSQL concepts through a clean Tkinter GUI, providing role-based access for Admins, Faculty, and Students to manage coursework, timetables, and attendance records.

## Features
- **Role-Based Access Control**: Separate dashboards for Admins, Faculty, and Students.
- **Attendance Tracking**: Real-time attendance logging, calculating aggregated attendance percentages.
- **Academic Setup**: Manage Departments, Courses, Rooms, and Sections.
- **Timetable Scheduling**: Handle weekly schedules and exam timetables with clash detection.
- **Leave Management**: Review and approve/reject leave requests.
- **System Audit Logging**: Track database insertions, updates, and deletions using database triggers.
- **Prerequisite-Aware Enrollment**: Enforce multi-course prerequisite chains with normalized tables, views, and triggers.
- **Faculty Workload Analyzer**: Compute ranked workload, weekly teaching hours, semester summaries, and monthly sessions.
- **Attendance Freeze & Archive**: Time-based freeze policy, override support, archival of old semesters, and unified history views.

## Technologies Used
- **Language**: Python 3.10+
- **Database**: PostgreSQL 14+
- **GUI Framework**: Tkinter + `sv_ttk` (Sun Valley Theme)
- **Database Driver**: `psycopg2`
- **Data Export**: Built-in `csv` module

## Folder Structure Explanation
```
ProjectStructure/
│
├── app.py                   # Main application entry point
├── db.py                    # Database connection setup
├── requirements.txt         # Python dependencies
├── .gitignore               # Git ignored files
├── README.md                # Project documentation
├── Report.docx              # Project report placeholder
│
├── services/                # Business logic and database operations
│   ├── auth_service.py
│   ├── attendance_service.py
│   ├── timetable_service.py
│   ├── report_service.py
│   └── user_service.py
│
├── gui/                     # Graphical User Interface modules
│   ├── login.py
│   ├── admin_dashboard.py
│   ├── faculty_dashboard.py
│   ├── student_dashboard.py
│   ├── attendance_page.py
│   ├── timetable_page.py
│   └── reports_page.py
│
├── utils/                   # Shared utilities and helpers
│   ├── validators.py
│   ├── helpers.py
│   ├── constants.py
│   └── exporters.py
│
├── assets/                  # Images, icons, and themes
│   ├── icons/
│   └── themes/
│
└── sql/                     # PostgreSQL schema definition and logic
    ├── 01_tables.sql        # Table structures
    ├── 02_constraints.sql   # Foreign keys and check constraints
    ├── 03_indexes.sql       # Performance optimization indexes
    ├── 04_views.sql         # Complex SELECT combinations
    ├── 05_triggers.sql      # Automated auditing
    ├── 06_procedures.sql    # Transactional logic
    ├── 07_functions.sql     # Data calculations
    ├── 08_cursors.sql       # Procedural data processing
    ├── 09_seed_data.sql     # Test application data
    └── 10_master_reset.sql  # Master execution script
```

## Database Concepts Implemented
This project rigorously demonstrates the following core DBMS concepts:
1. **Views**: Abstracted complex joins (e.g., `student_attendance_report`).
2. **Triggers**: Automated audit logging capturing table changes.
3. **Stored Procedures**: Encapsulated transaction logic for marking attendance.
4. **Functions**: Custom math calculations for student attendance percentages.
5. **Cursors**: Processing high volumes of data row-by-row (e.g., notifications).
6. **Transactions**: Explicit `COMMIT` and `ROLLBACK` for multi-table inserts.
7. **Indexes**: Composite indexing for faster lookups.
8. **Constraints**: `CHECK` rules preventing overlapping end/start times.
9. **Joins**: Comprehensive inner, left, and right joins throughout `services/`.
10. **Aggregate Queries**: Use of `SUM()`, `COUNT()`, `COALESCE()`.
11. **HAVING Clauses**: Advanced filtering on aggregate data.
12. **Subqueries**: Used within cursors and reports.

## Installation Guide (Run From Scratch)

### 1. Configure Python Environment
Install the required python packages using pip:
```bash
pip install -r requirements.txt
```

### 2. Configure Database Credentials
Edit the `db.py` file to include your local PostgreSQL connection credentials (Host, Username, Password).

### 3. PostgreSQL Database Initialization
Open your `psql` terminal or pgAdmin, and create the database:
```sql
CREATE DATABASE attendify;
\c attendify
```

### 4. Execute SQL Files in Order
You can run all files using the provided master reset script from the command line:
```bash
psql -U postgres -d attendify -f "sql/10_master_reset.sql"
```
Or manually run them in this exact order:
1. `01_tables.sql`
2. `02_constraints.sql`
3. `03_indexes.sql`
4. `04_views.sql`
5. `05_triggers.sql`
6. `06_procedures.sql`
7. `07_functions.sql`
8. `08_cursors.sql`
9. `09_seed_data.sql`

### 5. Launch the Application
Run the Python application:
```bash
python app.py
```

## Default Test Credentials
The `09_seed_data.sql` file creates sample users for testing out of the box.

- **Admin Account**: 
  - Username: `admin1`
  - Password: `admin123`
- **Faculty Account**: 
  - Username: `fac1`
  - Password: `fac123`
- **Student Account**: 
  - Username: `stud1`
  - Password: `stud123`


## Academic Documentation

### 1. Extended Entity-Relationship (EER) Modeling
This project utilizes EER mapping to represent inheritance (Specialization/Generalization):
- **Superclass**: `Users` (Contains common attributes like `user_id`, `username`, `password_hash`).
- **Subclasses**: `Students` and `Faculty`.
- Both subclasses use their `student_id` or `faculty_id` as both a Primary Key and a Foreign Key linking back to `Users(user_id)`. This effectively implements a 1:1 disjoint relationship constraint.

### 2. Relational Algebra Mapping
The application relies on SQL queries that map to core Relational Algebra concepts:

1. **Selection (σ)**: Finding a specific user.
   - *SQL*: `SELECT * FROM Users WHERE username = 'admin1';`
   - *Algebra*: σ<sub>username='admin1'</sub>(Users)
2. **Projection (π)**: Fetching only specific columns for privacy.
   - *SQL*: `SELECT username, role FROM Users;`
   - *Algebra*: π<sub>username, role</sub>(Users)
3. **Join (⨝)**: Fetching enrollments with course names.
   - *SQL*: `SELECT * FROM Enrollments e JOIN Sections s ON e.section_id = s.section_id;`
   - *Algebra*: Enrollments ⨝<sub>Enrollments.section_id = Sections.section_id</sub> Sections
4. **Union (∪)**: Combining Student and Faculty schedules (Conceptual).
   - *Algebra*: (π<sub>user_id</sub>(Students)) ∪ (π<sub>user_id</sub>(Faculty))
5. **Set Difference (-)**: Finding Unenrolled Students.
   - *SQL*: `SELECT student_id FROM Students EXCEPT SELECT student_id FROM Enrollments;`
   - *Algebra*: π<sub>student_id</sub>(Students) - π<sub>student_id</sub>(Enrollments)

### 3. Normalization Proof (Up to 3NF)
The database was designed to prevent Insert, Update, and Delete anomalies:
- **UNF (Unnormalized Form)**: Initial concept grouped Students, Enrollments, and Courses into one large spreadsheet-like table, causing repeating groups.
- **1NF**: Separated composite attributes and repeating groups. Each row has atomic values and a unique identifier.
- **2NF**: Removed Partial Dependencies. (e.g., `course_name` depends on `course_id`, not the composite PK of an Enrollment). Extracted to `Courses` table.
- **3NF**: Removed Transitive Dependencies. (e.g., `Student -> Department -> Department_Location`). Department details are stored in `Departments`.

  
Additional tables introduced for the advanced features also satisfy 3NF:

- **CoursePrerequisites(course_id, prereq_course_id)**  
  - Composite primary key; the only functional dependency is the key itself.
- **CourseResultStatuses(status_code, status_name, is_passing)**  
  - `status_code → status_name, is_passing`; `status_code` is the primary key.
- **StudentCourseResults(student_id, course_id, status_code, recorded_at, recorded_by, notes)**  
  - `(student_id, course_id) → status_code, recorded_at, recorded_by, notes`; all non-key attributes depend on the whole key.
- **AttendancePolicies(policy_id, freeze_minutes, archive_after_days, updated_at)**  
  - `policy_id → freeze_minutes, archive_after_days, updated_at`; singleton-like but still normalized.
- **AttendanceSessionsArchive / StudentAttendanceArchive / AttendanceEditAudit**  
  - Each has a single-column surrogate key; all descriptive attributes depend on that key only, while reference data (courses, students, statuses) remains normalized into parent tables.

### 4. Concurrency Control
PostgreSQL handles multiple simultaneous transactions. We provide a script `concurrency_demo.py` to explicitly demonstrate:
- **Row-Level Locking**: `SELECT ... FOR UPDATE` prevents two faculty members from marking attendance for the exact same student simultaneously.
- **Deadlock Detection**: If two threads attempt conflicting updates, PostgreSQL's deadlock detector rolls back one transaction, which we catch and recover using `SAVEPOINT`.

### 5. Query Optimization
We added **Composite Indexes** (`idx_sa_composite`) and foreign key indexes. Run `query_optimization_demo.py` to view the PostgreSQL `EXPLAIN ANALYZE` output. It proves the shift from slow **Sequential Scans (Seq Scan)** to rapid **Index Scans** for large dataset aggregations.

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


