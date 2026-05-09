"""
services/backup_service.py
─────────────────────────────────────────────────────────────────────────────
PostgreSQL ↔ Firebase Firestore backup and restore utilities.

Design notes
────────────
• All Firestore writes reuse the single `db` client initialised in
  firebase_service.py — no repeated firebase_admin.initialize_app calls.
• sync_table / backup_postgres_to_firebase are BLOCKING.  Call them from a
  background thread in the UI (see admin_dashboard.py) to avoid freezing.
• Each row is retried up to MAX_RETRIES times on transient network errors
  before being counted as a failure.
• datetime / time / Decimal values are normalised before upload via
  firebase_service._clean_for_firestore so Firestore can serialise them.
─────────────────────────────────────────────────────────────────────────────
"""

import time
import logging

from db import fetch_all, get_connection
from services.firebase_service import db, _clean_for_firestore

# ─── Logging ──────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ─── Retry configuration ──────────────────────────────────────────────────────
MAX_RETRIES = 3          # attempts per row before giving up
RETRY_DELAY = 2.0        # seconds between retries (exponential back-off applied)

# ─── PostgreSQL table → Firestore collection mapping ─────────────────────────
# Each PostgreSQL table is mirrored to the matching Firestore collection name.
# "Users_Admin" is a virtual mapping — it filters the Users table by role.
TABLE_COLLECTION_MAP = {
    "Students":         "students",
    "Faculty":          "faculty",
    "Users_Admin":      "admins",       # virtual: SELECT * FROM Users WHERE role='Admin'
    "Departments":      "departments",
    "Courses":          "courses",
    "Sections":         "sections",
    "Enrollments":      "enrollments",
    "StudentAttendance":"attendance",
    "Timetable":        "timetable",
    "Notifications":    "broadcasts",
}

# ─── Primary-key field per table ─────────────────────────────────────────────
_PK_FIELD = {
    "Students":          "student_id",
    "Faculty":           "faculty_id",
    "Users_Admin":       "user_id",
    "Departments":       "dept_id",
    "Courses":           "course_id",
    "Sections":          "section_id",
    "Enrollments":       "enrollment_id",
    "StudentAttendance": "attendance_id",
    "Timetable":         "timetable_id",
    "Notifications":     "notification_id",
}


# ─── Internal: write one row to Firestore with retry ──────────────────────────
def _write_with_retry(collection: str, doc_id: str, data: dict) -> bool:
    """
    Attempt to write `data` to Firestore collection/doc_id up to MAX_RETRIES times.
    Uses exponential back-off between attempts.
    Returns True on success, False after all retries are exhausted.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            db.collection(collection).document(doc_id).set(data)
            return True
        except Exception as exc:
            wait = RETRY_DELAY * (2 ** (attempt - 1))   # 2s, 4s, 8s
            logger.warning(
                "[Backup] Write failed (attempt %d/%d) — collection=%s doc=%s  error=%s  "
                "Retrying in %.0fs…",
                attempt, MAX_RETRIES, collection, doc_id, exc, wait
            )
            if attempt < MAX_RETRIES:
                time.sleep(wait)
            else:
                logger.error(
                    "[Backup] Giving up on collection=%s doc=%s after %d attempts.",
                    collection, doc_id, MAX_RETRIES
                )
                print(f"Failed to sync row in {collection}: {exc}")
                return False


# ─── Sync a single table ──────────────────────────────────────────────────────
def sync_table(table_name: str) -> int:
    """
    Sync a single PostgreSQL table (or virtual mapping) to its Firestore collection.

    Args:
        table_name: A key from TABLE_COLLECTION_MAP (e.g. "Students").

    Returns:
        Number of rows successfully written.
    """
    if not db:
        print("[Backup] Firestore client not available — skipping sync.")
        logger.warning("[Backup] sync_table called but db is None.")
        return 0

    # ── Resolve table / collection / pk_field ─────────────────────────────────
    if table_name == "Users_Admin":
        sql       = "SELECT * FROM Users WHERE role = 'Admin'"
        pk_field  = _PK_FIELD["Users_Admin"]
        collection = TABLE_COLLECTION_MAP["Users_Admin"]
    else:
        if table_name not in TABLE_COLLECTION_MAP:
            logger.error("[Backup] Unknown table name: %s", table_name)
            print(f"[Backup] Invalid table name: {table_name}")
            return 0
        collection = TABLE_COLLECTION_MAP[table_name]
        pk_field   = _PK_FIELD.get(table_name, "id")
        sql        = f"SELECT * FROM {table_name}"

    # ── Fetch rows from PostgreSQL ─────────────────────────────────────────────
    print(f"Syncing {table_name}…")
    rows = fetch_all(sql)

    if not rows:
        print(f"  → No rows found in {table_name}.")
        return 0

    count = 0
    for row in rows:
        doc_id = str(row.get(pk_field, ""))
        if not doc_id or doc_id == "None":
            logger.warning("[Backup] Skipping row in %s — missing PK field '%s'.", table_name, pk_field)
            continue

        clean_row = _clean_for_firestore(dict(row))   # row may be RealDictRow; cast to plain dict
        if _write_with_retry(collection, doc_id, clean_row):
            count += 1

    print(f"  → Synced {count}/{len(rows)} records for '{collection}'.")
    return count


# ─── Full backup ──────────────────────────────────────────────────────────────
def backup_postgres_to_firebase() -> int:
    """
    Read every configured PostgreSQL table and write all rows to the matching
    Firestore collection.

    This function is BLOCKING — run it from a background thread in the UI.

    Returns:
        Total number of records successfully written across all tables.
    """
    if not db:
        print("[Backup] Cannot perform backup — Firebase not initialised.")
        logger.error("[Backup] backup_postgres_to_firebase: db is None.")
        return 0

    print("\n[Firebase] Starting full PostgreSQL → Firestore backup…")
    print(f"[Firebase] Service: Cloud Firestore  |  Tables: {len(TABLE_COLLECTION_MAP)}")

    total = 0
    for table in TABLE_COLLECTION_MAP:
        count = sync_table(table)
        total += count

    print(f"\n[Firebase] Backup complete — {total} records transferred to Firestore.")
    return total


# ─── Full restore ─────────────────────────────────────────────────────────────
def restore_firebase_to_postgres() -> int:
    """
    Read every Firestore collection and insert documents into the matching
    PostgreSQL table.  Duplicate primary keys are silently ignored via
    SAVEPOINTs so one failure does not roll back the entire transaction.

    This function is BLOCKING — run it from a background thread in the UI.

    Returns:
        Total number of records successfully inserted.
    """
    if not db:
        print("[Restore] Cannot perform restore — Firebase not initialised.")
        logger.error("[Restore] restore_firebase_to_postgres: db is None.")
        return 0

    conn = get_connection()
    if not conn:
        print("[Restore] Could not obtain a PostgreSQL connection.")
        logger.error("[Restore] get_connection() returned None.")
        return 0

    print("\n[Firebase] Starting Firestore → PostgreSQL restore…")
    total_restored = 0

    try:
        with conn.cursor() as cur:
            for pg_table, collection in TABLE_COLLECTION_MAP.items():
                print(f"  Restoring collection '{collection}' → table '{pg_table}'…")

                # Users_Admin documents go into the Users table
                target_table = "Users" if pg_table == "Users_Admin" else pg_table

                try:
                    docs = list(db.collection(collection).stream())
                except Exception as exc:
                    logger.error("[Restore] Failed to stream collection '%s': %s", collection, exc)
                    print(f"  → Could not read collection '{collection}': {exc}")
                    continue

                restored_in_collection = 0
                for doc in docs:
                    data = doc.to_dict()
                    if not data:
                        continue

                    columns      = list(data.keys())
                    values       = tuple(data.values())
                    placeholders = ", ".join(["%s"] * len(columns))
                    col_names    = ", ".join(columns)
                    insert_sql   = (
                        f"INSERT INTO {target_table} ({col_names}) VALUES ({placeholders})"
                    )

                    try:
                        cur.execute("SAVEPOINT restore_sp")
                        cur.execute(insert_sql, values)
                        cur.execute("RELEASE SAVEPOINT restore_sp")
                        restored_in_collection += 1
                        total_restored += 1
                    except Exception:
                        # Most likely a unique-constraint violation — ignore silently
                        cur.execute("ROLLBACK TO SAVEPOINT restore_sp")

                print(f"  → Restored {restored_in_collection} records for '{pg_table}'.")

        conn.commit()
        print(f"\n[Firebase] Restore complete — {total_restored} records inserted into PostgreSQL.")
        return total_restored

    except Exception as exc:
        conn.rollback()
        logger.error("[Restore] Transaction rolled back due to error: %s", exc)
        print(f"[Firebase] Restore failed — transaction rolled back. Error: {exc}")
        return 0

    finally:
        conn.close()
