-- 10_master_reset.sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

BEGIN;

\i 01_tables.sql
\i 02_constraints.sql
\i 03_indexes.sql
\i 04_views.sql
\i 05_triggers.sql
\i 06_procedures.sql
\i 07_functions.sql
\i 08_cursors.sql
\i 09_seed_data.sql

COMMIT;
