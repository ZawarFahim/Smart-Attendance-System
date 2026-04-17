# ATTENDIFY – Smart Attendance Management System

ATTENDIFY is a robust, modular, and enterprise-grade Python application for managing student attendance, faculty schedules, and administrative reporting. Built according to clean architecture, it separates Database functionality, Service logic bridging, and User Interface management into distinct components.

## Features Required By the Spec
- 100% Python with `Tkinter` (ttk) for the UI.
- `PostgreSQL` Database interaction using `psycopg2`.
- Advanced SQL Triggers, Stored Procedures, and Views.
- Complete modular setup.
- Login validation & Role-based Dashboards (Admin / Faculty / Student).

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
