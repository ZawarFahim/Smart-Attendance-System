# ATTENDIFY – Smart Attendance Management System

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

### Third Normal Form (3NF) ✅
- No **transitive dependencies** (non-key column depending on another non-key column).
- Department info (`dept_name`) is stored once in `Departments` — not repeated inside `Students` or `Faculty`.
- Course info is stored in `Courses` — not duplicated inside `Sections` or `StudentAttendance`.
- Status names live in `AttendanceStatus` — not as raw strings across multiple tables.

### BCNF (Boyce–Codd NF) ✅
- Every determinant in every table is a candidate key, satisfying BCNF.

---

## DBMS Concepts Implemented

| Concept | Implementation | File |
|---|---|---|
| ER Diagram | 16-entity ERD with relationships | `database/erd_diagram.html` |
| DDL | CREATE / DROP TABLE, CREATE INDEX | `schema.sql` |
| DML | INSERT / UPDATE / DELETE / SELECT | `seed.sql`, service files |
| Constraints | PK, FK, UNIQUE, CHECK, NOT NULL, DEFAULT | `schema.sql` |
| Joins | INNER JOIN, LEFT JOIN, implicit cross join | `views.sql`, service files |
| Views | 5 views including view-on-view | `views.sql` |
| Stored Procedure | `mark_attendance` with UPSERT logic | `procedures.sql` |
| Function | `calculate_attendance_percentage` | `procedures.sql` |
| **Cursor** | `notify_low_attendance_students` — OPEN/FETCH/CLOSE loop | `procedures.sql` |
| Triggers | Duplicate guard + Audit log (BEFORE/AFTER) | `triggers.sql` |
| Subqueries | Scalar, correlated, derived-table style | `seed.sql`, `admin_service.py` |
| **HAVING** | `high_enrolment_sections`, `dept_low_avg_attendance` | `views.sql` |
| Indexes | 7 performance indexes on FK columns | `schema.sql` |
| Transactions | `BEGIN; … COMMIT;` wraps full reset | `master_reset.sql` |
| Aggregate Functions | COUNT, AVG, ROUND, COALESCE | Throughout |
| Normalization | 1NF + 2NF + 3NF + BCNF | See section above |
