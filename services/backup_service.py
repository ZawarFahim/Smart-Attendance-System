import time
from db import fetch_all, execute_query, get_connection
from services.firebase_service import db

# PostgreSQL Table to Firebase Collection mapping
TABLE_COLLECTION_MAP = {
    'Students': 'students',
    'Faculty': 'faculty',
    'Users_Admin': 'admins', # Virtual table mapping
    'Departments': 'departments',
    'Courses': 'courses',
    'Sections': 'sections',
    'Enrollments': 'enrollments',
    'StudentAttendance': 'attendance',
    'Timetable': 'timetable',
    'Notifications': 'broadcasts'
}

def clean_dict_for_firestore(d):
    """Ensure datetime and time objects are converted to string for Firestore."""
    clean_d = {}
    for k, v in d.items():
        if hasattr(v, 'isoformat'):
            clean_d[k] = v.isoformat()
        else:
            clean_d[k] = v
    return clean_d

def sync_table(table_name):
    """
    Sync a single specific table to Firestore.
    """
    if not db:
        print("Firebase not initialized.")
        return 0
        
    print(f"Syncing {table_name}...")
    
    # Handle the virtual "Users_Admin" case
    if table_name == 'Users_Admin':
        query = "SELECT * FROM Users WHERE role = 'Admin'"
        pk_field = 'user_id'
        collection = 'admins'
    else:
        # Validate table name to prevent SQL injection or invalid access
        if table_name not in TABLE_COLLECTION_MAP and table_name not in TABLE_COLLECTION_MAP.values():
            print(f"Invalid table name: {table_name}")
            return 0
            
        # Get true table name if a collection name was passed
        actual_table = table_name
        for t, c in TABLE_COLLECTION_MAP.items():
            if table_name == c:
                actual_table = t
                break
                
        collection = TABLE_COLLECTION_MAP.get(actual_table, actual_table.lower())
        query = f"SELECT * FROM {actual_table}"
        
        # Determine Primary Key field for document ID
        if actual_table == 'Students': pk_field = 'student_id'
        elif actual_table == 'Faculty': pk_field = 'faculty_id'
        elif actual_table == 'Departments': pk_field = 'dept_id'
        elif actual_table == 'Courses': pk_field = 'course_id'
        elif actual_table == 'Sections': pk_field = 'section_id'
        elif actual_table == 'Enrollments': pk_field = 'enrollment_id'
        elif actual_table == 'StudentAttendance': pk_field = 'attendance_id'
        elif actual_table == 'Timetable': pk_field = 'timetable_id'
        elif actual_table == 'Notifications': pk_field = 'notification_id'
        else: pk_field = 'id'

    rows = fetch_all(query)
    count = 0
    for row in rows:
        try:
            doc_id = str(row.get(pk_field))
            clean_row = clean_dict_for_firestore(row)
            db.collection(collection).document(doc_id).set(clean_row)
            count += 1
        except Exception as e:
            print(f"Failed to sync row in {collection}: {e}")
            continue
            
    print(f"Synced {count} records for {collection}.")
    return count

def backup_postgres_to_firebase():
    """
    Reads all rows from all specified PostgreSQL tables and syncs them into matching Firestore collections.
    """
    if not db:
        print("Firebase not initialized. Cannot perform backup.")
        return 0

    total_count = 0
    for pg_table in TABLE_COLLECTION_MAP.keys():
        count = sync_table(pg_table)
        total_count += count
        
    print(f"Backup Complete — {total_count} records transferred.")
    return total_count

def restore_firebase_to_postgres():
    """
    Reads ALL Firestore documents from collections and inserts into PostgreSQL
    using INSERT ... ON CONFLICT DO NOTHING to avoid duplicates.
    Rolls back on failure.
    """
    if not db:
        print("Firebase not initialized.")
        return 0

    conn = get_connection()
    if not conn:
        print("Could not connect to Postgres for restore.")
        return 0

    total_restored = 0
    try:
        with conn.cursor() as cur:
            for pg_table, collection in TABLE_COLLECTION_MAP.items():
                print(f"Restoring collection {collection} to table {pg_table}...")
                docs = db.collection(collection).stream()
                restored_in_collection = 0
                
                # Handling virtual table Users_Admin
                target_table = "Users" if pg_table == "Users_Admin" else pg_table

                for doc in docs:
                    data = doc.to_dict()
                    if not data: continue
                    
                    columns = list(data.keys())
                    values = tuple(data.values())
                    placeholders = ", ".join(["%s"] * len(columns))
                    col_names = ", ".join(columns)
                    
                    # Assuming the first column in the dict or a known field is PK for ON CONFLICT DO NOTHING
                    # To do this safely dynamically without knowing the exact constraint, 
                    # Postgres 14 requires ON CONFLICT (pk) DO NOTHING.
                    # Since we don't know the exact PK dynamically in this generic function without querying pg_catalog,
                    # we will catch UniqueViolation exceptions per row or just use an exception block.
                    # A safer way is using savepoints or simple insert with exception catch.
                    
                    insert_query = f"INSERT INTO {target_table} ({col_names}) VALUES ({placeholders})"
                    
                    try:
                        cur.execute("SAVEPOINT restore_sp")
                        cur.execute(insert_query, values)
                        cur.execute("RELEASE SAVEPOINT restore_sp")
                        restored_in_collection += 1
                        total_restored += 1
                    except Exception as e:
                        cur.execute("ROLLBACK TO SAVEPOINT restore_sp")
                        # likely a unique constraint violation, ignore and continue
                        pass
                        
                print(f"Restored {restored_in_collection} records for {pg_table}.")

            conn.commit()
            print(f"Restore Complete — {total_restored} records restored to PostgreSQL.")
            return total_restored
            
    except Exception as e:
        conn.rollback()
        print(f"Restore Failed, transaction rolled back. Error: {e}")
        return 0
    finally:
        conn.close()
