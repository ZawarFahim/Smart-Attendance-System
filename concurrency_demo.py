import threading
import time
import psycopg2
from db import get_connection

print("==================================================")
print(" DBMS ACADEMIC DEMO: CONCURRENCY & TRANSACTIONS")
print("==================================================")
print("This script demonstrates explicit row-level locking (SELECT ... FOR UPDATE)")
print("and concurrent transaction handling in PostgreSQL.")
print("It simulates two threads trying to mark attendance for the same student")
print("at the exact same time.\n")

def thread_task(thread_id, delay_before_commit):
    conn = get_connection()
    if not conn:
        print(f"[Thread {thread_id}] Failed to connect.")
        return

    try:
        with conn.cursor() as cur:
            print(f"[Thread {thread_id}] Starting transaction...")
            
            # Use explicit savepoint to demonstrate SAVEPOINT theory
            cur.execute("SAVEPOINT start_attendance;")
            
            print(f"[Thread {thread_id}] Attempting to lock row (SELECT ... FOR UPDATE)...")
            # This triggers the SELECT FOR UPDATE lock implemented in 06_procedures.sql indirectly,
            # but to demonstrate it directly in python we can lock a row here:
            cur.execute("SELECT * FROM Students WHERE student_id = 3 FOR UPDATE;")
            print(f"[Thread {thread_id}] Row locked successfully!")
            
            # Simulate work / delay
            print(f"[Thread {thread_id}] Processing data for {delay_before_commit} seconds...")
            time.sleep(delay_before_commit)
            
            print(f"[Thread {thread_id}] Attempting to update record...")
            # We are manually simulating what the stored procedure does for academic demonstration
            cur.execute("""
                UPDATE Students 
                SET last_name = last_name || '*' 
                WHERE student_id = 3
            """)
            
            print(f"[Thread {thread_id}] Committing transaction...")
            conn.commit()
            print(f"[Thread {thread_id}] SUCCESS!")
            
    except psycopg2.errors.DeadlockDetected:
        print(f"[Thread {thread_id}] DEADLOCK DETECTED! Rolling back to savepoint.")
        conn.rollback()
    except Exception as e:
        print(f"[Thread {thread_id}] Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    # Create two threads
    # Thread 1 will lock the row, then sleep for 3 seconds.
    # Thread 2 will start 1 second later, try to lock the same row, and will BLOCK
    # until Thread 1 commits.
    
    t1 = threading.Thread(target=thread_task, args=(1, 3))
    t2 = threading.Thread(target=thread_task, args=(2, 0))

    t1.start()
    time.sleep(0.5) # ensure t1 gets the lock first
    t2.start()

    t1.join()
    t2.join()

    print("\n[MAIN] Demonstration complete.")
    print("Notice how Thread 2 paused and WAITED for Thread 1 to release the lock.")
    print("This is strict concurrency control preventing race conditions!")
