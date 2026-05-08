-- ==================================================
-- ATTENDIFY - Migration: Students Schema Update
-- Purpose:
--   1. Add reg_no (unique) to Students table
--   2. Add name column (merging first_name + last_name)
--   3. Keep first_name & last_name columns for legacy compatibility
--
-- SAFE APPROACH:
--   - Adds new columns WITHOUT dropping old ones
--   - Backfills name from existing first_name + last_name
--   - reg_no is nullable initially (existing students won't have one)
--
-- Run ONCE against your live database BEFORE using excel_import_service.
-- ==================================================

BEGIN;

-- Step 1: Add reg_no column to Students (nullable initially for safety)
ALTER TABLE Students
    ADD COLUMN IF NOT EXISTS reg_no VARCHAR(50);

-- Step 2: Add name column to Students (nullable initially)
ALTER TABLE Students
    ADD COLUMN IF NOT EXISTS name VARCHAR(100);

-- Step 3: Backfill name from existing first_name + last_name data
UPDATE Students
    SET name = TRIM(first_name || ' ' || last_name)
    WHERE name IS NULL;

-- Step 4: Add UNIQUE constraint on reg_no (NULLs are not considered duplicates)
ALTER TABLE Students
    ADD CONSTRAINT students_reg_no_unique UNIQUE (reg_no);

-- Step 5: Add index on reg_no for fast duplicate-check lookups
CREATE INDEX IF NOT EXISTS idx_students_reg_no ON Students(reg_no);

-- Step 6: Add name column to Faculty table for display consistency
ALTER TABLE Faculty
    ADD COLUMN IF NOT EXISTS name VARCHAR(100);

UPDATE Faculty
    SET name = TRIM(first_name || ' ' || last_name)
    WHERE name IS NULL;

COMMIT;

-- ==================================================
-- VERIFICATION QUERIES (run manually to confirm)
-- ==================================================
-- SELECT student_id, reg_no, name, first_name, last_name FROM Students LIMIT 10;
-- SELECT faculty_id, name, first_name, last_name FROM Faculty LIMIT 10;
