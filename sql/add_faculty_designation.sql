-- ==================================================
-- ATTENDIFY - Migration: Add designation to Faculty
-- Run ONCE before using the "Add Faculty" admin form.
-- Safe: uses ADD COLUMN IF NOT EXISTS
-- ==================================================

BEGIN;

ALTER TABLE Faculty
    ADD COLUMN IF NOT EXISTS designation VARCHAR(100);

COMMIT;

-- Verify:
-- SELECT faculty_id, first_name, last_name, designation FROM Faculty LIMIT 5;
