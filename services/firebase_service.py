"""
services/firebase_service.py
─────────────────────────────────────────────────────────────────────────────
Firebase Admin SDK initialisation and Firestore helper functions.

SERVICE IN USE: Google Cloud Firestore
  ↳ NOT the Firebase Realtime Database.
  ↳ The Firestore database must be created in the Firebase Console:
       Firebase Console → Build → Firestore Database → Create database
       (choose a region such as "nam5" / us-east1 and start in production mode)

CREDENTIAL LOADING ORDER:
  1. .env file in the project root  →  FIREBASE_CREDENTIALS_PATH key
  2. Falls back to  firebase_config.json  in the project root
  3. Falls back to  config/firebase/serviceAccountKey.json

IMPORTANT: Never expose private key values in logs or UI messages.
─────────────────────────────────────────────────────────────────────────────
"""

import os
import json
import logging
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# ─── Logging ──────────────────────────────────────────────────────────────────
# Use the standard logging module so messages integrate with any log handler
# the rest of the application configures.
logger = logging.getLogger(__name__)

# ─── Resolve project root ──────────────────────────────────────────────────────
# __file__ is .../services/firebase_service.py  →  parent is services/  →
# parent.parent is the project root.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ─── Load .env from the project root (not from cwd) ───────────────────────────
_env_path = _PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=_env_path, override=False)

# ─── Resolve credentials path ─────────────────────────────────────────────────
def _resolve_credentials_path() -> Path:
    """
    Resolve the Firebase service-account JSON path.

    Priority:
      1. FIREBASE_CREDENTIALS_PATH env var (from .env or shell)
      2. firebase_config.json in project root
      3. config/firebase/serviceAccountKey.json
    """
    env_val = os.getenv("FIREBASE_CREDENTIALS_PATH", "").strip()

    candidates = []
    if env_val:
        # Could be absolute or relative-to-project-root
        p = Path(env_val)
        candidates.append(p if p.is_absolute() else _PROJECT_ROOT / p)

    # Built-in fallbacks
    candidates.append(_PROJECT_ROOT / "firebase_config.json")
    candidates.append(_PROJECT_ROOT / "config" / "firebase" / "serviceAccountKey.json")

    for path in candidates:
        if path.exists():
            logger.info("[Firebase] Using credentials file: %s", path.name)
            return path

    return None   # No file found


# ─── Initialise Firebase (called once at module import) ───────────────────────
def _initialize_firebase():
    """
    Safely initialise the Firebase Admin SDK exactly once per process.

    Returns:
        google.cloud.firestore.Client  or  None on failure.
    """
    cred_path = _resolve_credentials_path()

    if cred_path is None:
        logger.warning(
            "[Firebase] No credentials file found. "
            "Firebase features will be disabled. "
            "Set FIREBASE_CREDENTIALS_PATH in .env or place firebase_config.json "
            "in the project root."
        )
        return None

    try:
        # Guard: do NOT call initialize_app a second time if already running.
        if not firebase_admin._apps:
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred)
            logger.info("[Firebase] Firebase Admin SDK initialised successfully.")
            print("[Firebase] Service: Cloud Firestore | Initialisation: OK")
        else:
            logger.debug("[Firebase] Firebase app already initialised — reusing.")

        # Return the Firestore client (not Realtime Database).
        # Firestore does NOT require a databaseURL; it is separate from RTDB.
        client = firestore.client()
        logger.info("[Firebase] Firestore client obtained.")
        return client

    except Exception as exc:
        # Deliberately vague in the message to avoid leaking key material.
        logger.error("[Firebase] Initialisation failed: %s", type(exc).__name__)
        print(f"[Firebase] Initialisation FAILED ({type(exc).__name__}). "
              "Check that:\n"
              "  1. The service-account JSON is the latest key from Firebase Console.\n"
              "  2. Your machine's clock is accurate (JWT timestamps are time-sensitive).\n"
              "  3. You have internet access and firestore.googleapis.com is reachable.\n"
              f"  Details: {exc}")
        return None


# ─── Module-level singleton ────────────────────────────────────────────────────
# Initialised once when the module is first imported.
# All sync functions share this single client — no repeated initialisation.
db = _initialize_firebase()


# ─── Connection test utility ───────────────────────────────────────────────────
def test_firebase_connection() -> bool:
    """
    Write a small sentinel document to Firestore to confirm:
      • authentication is working (valid JWT / service-account key)
      • the Firestore database exists in the Firebase project
      • the network can reach firestore.googleapis.com

    Returns True on success, False on any failure.
    Prints a human-readable result to stdout and logs details.
    """
    if not db:
        print("[Firebase] Connection test SKIPPED — Firestore client not available.")
        return False

    try:
        test_ref = db.collection("_connection_test").document("ping")
        test_ref.set({"status": "ok", "source": "attendify-admin"})
        # Verify the write was accepted by reading it back
        doc = test_ref.get()
        if doc.exists:
            test_ref.delete()   # clean up the sentinel doc
            print("[Firebase] Connection test PASSED — authentication and network OK.")
            logger.info("[Firebase] Connection test passed.")
            return True
        else:
            print("[Firebase] Connection test FAILED — write succeeded but read returned nothing.")
            logger.warning("[Firebase] Connection test: write succeeded but document not readable.")
            return False

    except Exception as exc:
        logger.error("[Firebase] Connection test FAILED: %s", exc)
        print(
            f"[Firebase] Connection test FAILED.\n"
            f"  Error type : {type(exc).__name__}\n"
            f"  Message    : {exc}\n\n"
            "  Common causes:\n"
            "    • Invalid or expired service-account key → regenerate in Firebase Console\n"
            "    • System clock skew → ensure Windows time is synced\n"
            "    • No internet / firewall blocking firestore.googleapis.com\n"
            "    • Firestore database not created → Firebase Console → Build → Firestore Database\n"
            "    • VPN / proxy blocking Google Cloud endpoints\n"
        )
        return False


# ─── STUDENTS ──────────────────────────────────────────────────────────────────

def sync_student_to_firebase(student_dict: dict) -> bool:
    """
    Sync a single student dict to the 'students' Firestore collection.
    Uses student_id as the document ID.
    Returns True on success, False on failure.
    """
    if not db:
        return False
    try:
        student_id = str(student_dict.get("student_id"))
        if not student_id or student_id == "None":
            logger.warning("[Firebase] sync_student: missing student_id, skipping.")
            return False
        # Firestore cannot serialise datetime/time objects from psycopg2 — convert first
        clean = _clean_for_firestore(student_dict)
        db.collection("students").document(student_id).set(clean)
        return True
    except Exception as exc:
        logger.error("[Firebase] sync_student %s failed: %s", student_dict.get("student_id"), exc)
        return False


def get_student_from_firebase(student_id) -> dict | None:
    """
    Retrieve a student dict from the 'students' collection by ID.
    Returns the dict on success, None on failure or not found.
    """
    if not db:
        return None
    try:
        doc = db.collection("students").document(str(student_id)).get()
        return doc.to_dict() if doc.exists else None
    except Exception as exc:
        logger.error("[Firebase] get_student %s failed: %s", student_id, exc)
        return None


# ─── ATTENDANCE ────────────────────────────────────────────────────────────────

def sync_attendance_to_firebase(attendance_dict: dict) -> bool:
    """
    Sync a single attendance record to the 'attendance' Firestore collection.
    Uses attendance_id as the document ID.
    Returns True on success, False on failure.
    """
    if not db:
        return False
    try:
        attendance_id = str(attendance_dict.get("attendance_id"))
        if not attendance_id or attendance_id == "None":
            return False
        clean = _clean_for_firestore(attendance_dict)
        db.collection("attendance").document(attendance_id).set(clean)
        return True
    except Exception as exc:
        logger.error("[Firebase] sync_attendance %s failed: %s", attendance_dict.get("attendance_id"), exc)
        return False


def get_attendance_from_firebase(student_id) -> list | None:
    """
    Retrieve all attendance records for a student from Firebase.
    Returns a list of dicts on success, None on failure.
    """
    if not db:
        return None
    try:
        docs = db.collection("attendance").where("student_id", "==", int(student_id)).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as exc:
        logger.error("[Firebase] get_attendance student=%s failed: %s", student_id, exc)
        return None


# ─── BROADCASTS ────────────────────────────────────────────────────────────────

def sync_broadcast_to_firebase(broadcast_dict: dict) -> bool:
    """
    Sync a broadcast dict to the 'broadcasts' Firestore collection.
    Uses notification_id as the document ID.
    Returns True on success, False on failure.
    """
    if not db:
        return False
    try:
        broadcast_id = str(broadcast_dict.get("notification_id"))
        if not broadcast_id or broadcast_id == "None":
            return False
        clean = _clean_for_firestore(broadcast_dict)
        db.collection("broadcasts").document(broadcast_id).set(clean)
        return True
    except Exception as exc:
        logger.error("[Firebase] sync_broadcast %s failed: %s", broadcast_dict.get("notification_id"), exc)
        return False


# ─── TIMETABLE ─────────────────────────────────────────────────────────────────

def sync_timetable_to_firebase(timetable_dict: dict) -> bool:
    """
    Sync a timetable entry dict to the 'timetable' Firestore collection.
    Uses timetable_id as the document ID.
    Returns True on success, False on failure.
    """
    if not db:
        return False
    try:
        timetable_id = str(timetable_dict.get("timetable_id"))
        if not timetable_id or timetable_id == "None":
            return False
        clean = _clean_for_firestore(timetable_dict)
        db.collection("timetable").document(timetable_id).set(clean)
        return True
    except Exception as exc:
        logger.error("[Firebase] sync_timetable %s failed: %s", timetable_dict.get("timetable_id"), exc)
        return False


# ─── ENROLLMENTS ───────────────────────────────────────────────────────────────

def sync_enrollment_to_firebase(enrollment_dict: dict) -> bool:
    """
    Sync an enrollment dict to the 'enrollments' Firestore collection.
    Uses enrollment_id as the document ID.
    Returns True on success, False on failure.
    """
    if not db:
        return False
    try:
        enrollment_id = str(enrollment_dict.get("enrollment_id"))
        if not enrollment_id or enrollment_id == "None":
            return False
        clean = _clean_for_firestore(enrollment_dict)
        db.collection("enrollments").document(enrollment_id).set(clean)
        return True
    except Exception as exc:
        logger.error("[Firebase] sync_enrollment %s failed: %s", enrollment_dict.get("enrollment_id"), exc)
        return False


# ─── Internal helpers ──────────────────────────────────────────────────────────

def _clean_for_firestore(record: dict) -> dict:
    """
    Convert psycopg2 types that Firestore cannot serialise:
      • datetime / date / time  → ISO 8601 string
      • Decimal                 → float
      • None values             → kept as None (Firestore accepts null)
    Returns a new dict; the original is not mutated.
    """
    import decimal
    cleaned = {}
    for key, value in record.items():
        if value is None:
            cleaned[key] = None
        elif hasattr(value, "isoformat"):
            # Covers datetime.datetime, datetime.date, datetime.time
            cleaned[key] = value.isoformat()
        elif isinstance(value, decimal.Decimal):
            cleaned[key] = float(value)
        else:
            cleaned[key] = value
    return cleaned
