# ATTENDIFY - Smart Attendance Management System

A comprehensive, modular University Database Management System (DBMS) project. This project implements advanced PostgreSQL concepts through a clean Tkinter GUI, providing role-based access for Admins, Faculty, and Students to manage coursework, timetables, and attendance records.

## Features
- **Role-Based Access Control**: Separate dashboards for Admins, Faculty, and Students.
- **Attendance Tracking**: Real-time attendance logging, calculating aggregated attendance percentages.
- **Academic Setup**: Manage Departments, Courses, Rooms, and Sections.
- **Timetable Scheduling**: Handle weekly schedules and exam timetables with clash detection.
- **Leave Management**: Review and approve/reject leave requests.
- **System Audit Logging**: Track database insertions, updates, and deletions using database triggers.

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

## Screenshots
*(Insert screenshots of the Login, Admin Dashboard, and Attendance Pages here)*

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

### 3. Normalization Proof (Up to BCNF)
The database was designed to prevent Insert, Update, and Delete anomalies:
- **UNF (Unnormalized Form)**: Initial concept grouped Students, Enrollments, and Courses into one large spreadsheet-like table, causing repeating groups.
- **1NF**: Separated composite attributes and repeating groups. Each row has atomic values and a unique identifier.
- **2NF**: Removed Partial Dependencies. (e.g., `course_name` depends on `course_id`, not the composite PK of an Enrollment). Extracted to `Courses` table.
- **3NF**: Removed Transitive Dependencies. (e.g., `Student -> Department -> Department_Location`). Department details are stored in `Departments`.
- **BCNF**: Ensured that for every functional dependency X → Y, X is a superkey. The `Enrollments` table `(student_id, section_id)` uniquely identifies an enrollment, and neither part can determine the other.

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

## Authors
- Developed as a Final Year University DBMS Project.
