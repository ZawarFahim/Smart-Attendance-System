# ATTENDIFY – Smart Attendance Management System

> **Enterprise-grade university attendance platform** built with Python (Tkinter), PostgreSQL, Firebase, and pandas.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Feature Highlights](#feature-highlights)
3. [System Architecture](#system-architecture)
4. [Prerequisites](#prerequisites)
5. [Installation & Setup](#installation--setup)
6. [Database Setup](#database-setup)
7. [Configuration](#configuration)
8. [Excel Bulk Import – Admin Feature](#excel-bulk-import--admin-feature)
9. [Running the Application](#running-the-application)
10. [Role-Based Login & Welcome Message](#role-based-login--welcome-message)
11. [Example Admin Workflow](#example-admin-workflow)
12. [Project Structure](#project-structure)

---

## Project Overview

ATTENDIFY is a full-featured student attendance management system for universities. It supports:

- **Role-based access control** – Admin, Faculty, Student
- **Real-time attendance marking** by faculty
- **Student self-service portal** – attendance history, leave requests, timetable
- **Admin ERP panel** – bulk onboarding, analytics, audit logs, Firebase sync
- **Secure credential management** – bcrypt password hashing

---

## Feature Highlights

| Feature | Description |
|---|---|
| **Bulk Student Import** | Import hundreds of students from a single Excel file |
| **Auto Credential Generation** | Email (`u{reg_no}@giki.edu.pk`) and password (bcrypt-hashed `reg_no`) generated automatically |
| **Role-Based Login** | Post-login greeting: `Welcome, {Full Name}` fetched from DB |
| **Attendance Marking** | Faculty create sessions and mark Present / Absent / Late per student |
| **Analytics Charts** | Pie and bar charts for overall attendance and department rates |
| **Leave Requests** | Students/Faculty submit; Admin approves/rejects with notifications |
| **Firebase Sync** | Full PostgreSQL ↔ Firebase Firestore backup & restore |
| **Audit Logs** | Every data mutation tracked with actor and timestamp |
| **Profile Images** | Students can upload/view their profile picture |
| **Dark/Light Theme Toggle** | Powered by `sv-ttk` |

---

## System Architecture

```
app.py                      ← Entry point
├── gui/
│   ├── login.py            ← Authentication UI
│   ├── dashboard.py        ← BaseDashboard (sidebar + content)
│   ├── admin_dashboard.py  ← Admin panel (import, analytics, audit…)
│   ├── faculty_dashboard.py← Faculty panel (mark attendance, workload…)
│   └── student_dashboard.py← Student portal (history, timetable…)
├── services/
│   ├── excel_import_service.py   ← NEW: Bulk Excel import
│   ├── auth_service.py           ← Login + display_name resolution
│   ├── user_service.py           ← All CRUD (students/faculty/admin)
│   ├── attendance_service.py     ← Session create, mark
│   ├── report_service.py         ← Analytics queries
│   ├── backup_service.py         ← Firebase sync
│   └── [shim files]             ← student/faculty/admin/leave/notification_service.py
├── config/
│   └── settings.py         ← Colors, fonts, EXCEL_IMPORT_PATH
├── utils/
│   └── helpers.py          ← bcrypt-aware hash_password / verify_password
├── sql/
│   ├── 01_tables.sql … 09_seed_data.sql
│   └── migrate_students_name.sql ← Schema migration for reg_no + name
├── database.ini            ← PostgreSQL connection config
└── .env                    ← Firebase credentials + EXCEL_IMPORT_PATH
```

---

## Prerequisites

| Tool | Version |
|---|---|
| Python | 3.10+ |
| PostgreSQL | 14+ |
| pip | Latest |

---

## Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/ZawarFahim/Smart-Attendance-System.git
cd Smart-Attendance-System

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

# 3. Install all dependencies
pip install -r requirements.txt
```

### Dependencies installed

| Package | Purpose |
|---|---|
| `psycopg2-binary` | PostgreSQL driver |
| `sv-ttk` | Modern Tkinter theme |
| `firebase-admin` | Firebase Firestore sync |
| `python-dotenv` | `.env` file loading |
| `Pillow` | Profile image handling |
| `pandas` | Excel file reading |
| `openpyxl` | `.xlsx` engine for pandas |
| `bcrypt` | Secure password hashing |
| `matplotlib` | Analytics charts |

---

## Database Setup

### Step 1 – Configure connection

Edit `database.ini`:

```ini
[postgresql]
host=localhost
database=attendify
user=postgres
password=your_password
port=5432
```

### Step 2 – Create database and run schema scripts

```sql
-- In psql:
CREATE DATABASE attendify;
\c attendify
\i sql/01_tables.sql
\i sql/02_constraints.sql
\i sql/03_indexes.sql
\i sql/04_views.sql
\i sql/05_triggers.sql
\i sql/06_procedures.sql
\i sql/07_functions.sql
\i sql/09_seed_data.sql
```

### Step 3 – Run migration (adds `reg_no` and `name` columns)

> **Run this ONCE** on an existing database before using the Excel import feature.  
> Safe to run on a fresh database too — uses `IF NOT EXISTS` guards.

```sql
\i sql/migrate_students_name.sql
```

This migration:
- Adds `reg_no VARCHAR(50) UNIQUE` to `Students`
- Adds `name VARCHAR(100)` to `Students` and `Faculty`
- Backfills `name` from existing `first_name + last_name` data
- Creates a fast index on `reg_no`

---

## Configuration

### `database.ini`
PostgreSQL connection parameters (see above).

### `.env`
```env
FIREBASE_CREDENTIALS_PATH=attendify-a38fe-firebase-adminsdk-fbsvc-726850afad.json

# Optional default Excel path for bulk import.
# Leave empty to always use the UI file picker.
EXCEL_IMPORT_PATH=
```

### `config/settings.py` – `EXCEL_IMPORT_PATH`

```python
# Line 43 in config/settings.py
EXCEL_IMPORT_PATH = ""   # e.g. "C:/data/students.xlsx"
```

Set this to a default path or leave blank and use the **Browse…** button in the Admin UI.

---

## Excel Bulk Import – Admin Feature

### Purpose

Import hundreds of students at once from an Excel file. The system:

1. Reads the Excel file using `pandas`
2. Validates required columns
3. Auto-generates email if missing: `u{reg_no}@giki.edu.pk`
4. Hashes the password with **bcrypt** (`default password = reg_no`)
5. Inserts into `Users` (role=Student) and `Students` tables atomically
6. Skips duplicates based on `reg_no`
7. Returns a summary: `inserted_count`, `skipped_count`, `failed_rows`

### Expected Excel Column Mapping

| Excel Column | Index | Field |
|---|---|---|
| Column B | 1 | `reg_no` (**required**) |
| Column C | 2 | `name` (**required**) |
| Column E | 4 | `email` (optional – auto-generated if blank) |

> Row 0 (the first row) is treated as data. If your Excel has a header row,
> it will be silently skipped because `reg_no` will be non-numeric/blank.

### How to Run Import via Admin UI

1. Launch the application: `python app.py`
2. Log in as **Admin**
3. Click **Import Students** in the sidebar
4. Click **Browse…** → select your `.xlsx` file  
   *(or pre-fill `EXCEL_IMPORT_PATH` in `.env` / `config/settings.py`)*
5. Optionally select a **Default Department**
6. Click **▶ Run Import**
7. Review the log panel:
   - `✅ Inserted` – new students added
   - `⏭ Skipped` – reg_no already exists
   - `❌ Failed` – rows with errors (details shown)

### How to Run Import Programmatically

```python
from services.excel_import_service import import_students_from_excel

summary = import_students_from_excel(
    filepath="C:/data/students.xlsx",
    default_dept_id=1   # optional
)
print(summary)
# {'inserted_count': 45, 'skipped_count': 3, 'failed_rows': [...]}
```

### Student Login After Import

After import, students log in with:

| Field | Value |
|---|---|
| Username / Email | Their `reg_no` OR `u{reg_no}@giki.edu.pk` |
| Password | Their `reg_no` (bcrypt-hashed in DB) |

---

## Running the Application

```bash
python app.py
```

The application checks the PostgreSQL connection at startup and exits with an error dialog if the database is unreachable.

---

## Role-Based Login & Welcome Message

After successful login, the system:

1. Fetches `name` from the `Students` or `Faculty` table (falls back to `first_name + last_name`, then `username`)
2. Stores it as `display_name` in the `user_info` session dict
3. Displays **`Welcome, {display_name}`** in the sidebar of every dashboard

No changes were made to the authentication logic — only the response payload was enhanced.

---

## Example Admin Workflow

```
1. Admin logs in → ATTENDIFY Admin Panel
2. Admin → Import Students → Browse → select students.xlsx → Run Import
   ✅ 120 students inserted | ⏭ 5 skipped | ❌ 0 failed
3. Students receive credentials:
   - Email:    u2023cs001@giki.edu.pk
   - Password: 2023CS001  (bcrypt-hashed in DB)
4. Student logs in → sees "Welcome, Ali Hassan" in sidebar
5. Student can view attendance, timetable, leave requests
```

---

## Project Structure

```
Smart-Attendance-System/
├── app.py
├── db.py
├── database.ini
├── .env
├── requirements.txt
├── README.md
├── config/
│   └── settings.py
├── gui/
│   ├── admin_dashboard.py
│   ├── dashboard.py
│   ├── faculty_dashboard.py
│   ├── login.py
│   └── student_dashboard.py
├── services/
│   ├── admin_service.py          (shim → user_service)
│   ├── attendance_service.py
│   ├── auth_service.py
│   ├── backup_service.py
│   ├── excel_import_service.py   ← NEW
│   ├── faculty_service.py        (shim → user_service)
│   ├── firebase_service.py
│   ├── image_service.py
│   ├── leave_service.py          (shim → user_service)
│   ├── notification_service.py   (shim → user_service)
│   ├── report_service.py
│   ├── student_service.py        (shim → user_service)
│   ├── timetable_service.py
│   └── user_service.py
├── sql/
│   ├── 01_tables.sql … 09_seed_data.sql
│   └── migrate_students_name.sql
└── utils/
    ├── auth.py
    ├── constants.py
    ├── exporters.py
    ├── helpers.py
    └── validators.py
```

---

## Security Notes

- Passwords are hashed with **bcrypt** (cost factor ≥ 12) for all newly imported/registered users
- Legacy seed-data accounts use plaintext; `verify_password` auto-detects the format
- All DB queries use **parameterized statements** – no SQL injection risk
- Firebase credentials are loaded from `.env` (never hardcoded)
