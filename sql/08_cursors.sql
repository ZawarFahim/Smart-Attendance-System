-- 08_cursors.sql
CREATE OR REPLACE FUNCTION notify_low_attendance_students()
RETURNS VOID AS $$
DECLARE
    student_cursor CURSOR FOR SELECT student_id FROM low_attendance_students;
    curr_student_id INT;
BEGIN
    OPEN student_cursor;
    LOOP
        FETCH student_cursor INTO curr_student_id;
        EXIT WHEN NOT FOUND;

        INSERT INTO Notifications (user_id, message)
        VALUES (curr_student_id, 'Warning: Your attendance has dropped below 75%. Please contact your faculty.');
    END LOOP;
    CLOSE student_cursor;
END;
$$ LANGUAGE plpgsql;
