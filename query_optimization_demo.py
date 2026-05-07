import psycopg2
from db import get_connection

print("==================================================")
print(" DBMS ACADEMIC DEMO: QUERY OPTIMIZATION")
print("==================================================")
print("This script uses EXPLAIN ANALYZE to compare the PostgreSQL")
print("execution plans for queries to demonstrate the importance of Indexing.\n")

def run_explain(query_name, query):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            print(f"--- EXPLAIN ANALYZE for {query_name} ---")
            cur.execute(f"EXPLAIN ANALYZE {query}")
            plan = cur.fetchall()
            for row in plan:
                print(row[0])
            print("-" * 50 + "\n")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Test 1: Query that should use our new composite index on StudentAttendance
    q1 = """
        SELECT * FROM StudentAttendance 
        WHERE session_id = 1 AND student_id = 3;
    """
    run_explain("Composite Index Lookup (StudentAttendance)", q1)

    # Test 2: Complex Join from our Views
    q2 = """
        SELECT * FROM department_attendance_ranking;
    """
    run_explain("Complex Aggregation View (department_attendance_ranking)", q2)

    print("Look at the execution plans above.")
    print("If tables grow large, PostgreSQL will switch from 'Seq Scan' (Sequential Scan)")
    print("to 'Index Scan' or 'Bitmap Index Scan', significantly reducing Execution Time.")
