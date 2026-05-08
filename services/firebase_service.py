import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Firebase credentials path
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "config/firebase/serviceAccountKey.json")

# Initialize Firebase App safely
def initialize_firebase():
    """
    Safely initialize the Firebase admin SDK.
    Prevents duplicate app initialization and handles missing credentials.
    Returns the Firestore client instance or None if initialization fails.
    """
    try:
        if not firebase_admin._apps:
            if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
                print(f"Warning: Firebase credentials not found at {FIREBASE_CREDENTIALS_PATH}. Firebase features will be disabled.")
                return None
            
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully.")
        
        return firestore.client()
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")
        return None

# Global db client
db = initialize_firebase()

# ─── STUDENTS ───────────────────────────────────────────────────────────────

def sync_student_to_firebase(student_dict):
    """
    Syncs a single student dictionary to the 'students' collection in Firestore.
    Uses student_id as the document ID.
    Returns True on success, False on failure.
    """
    if not db: return False
    try:
        student_id = str(student_dict.get('student_id'))
        if not student_id: return False
        
        db.collection('students').document(student_id).set(student_dict)
        return True
    except Exception as e:
        print(f"Error syncing student {student_dict.get('student_id')} to Firebase: {e}")
        return False

def get_student_from_firebase(student_id):
    """
    Retrieves a student dictionary from the 'students' collection by ID.
    Returns the dict on success, None on failure.
    """
    if not db: return None
    try:
        doc = db.collection('students').document(str(student_id)).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error fetching student {student_id} from Firebase: {e}")
        return None

# ─── ATTENDANCE ─────────────────────────────────────────────────────────────

def sync_attendance_to_firebase(attendance_dict):
    """
    Syncs a single attendance dictionary to the 'attendance' collection.
    Uses attendance_id as the document ID.
    Returns True on success, False on failure.
    """
    if not db: return False
    try:
        attendance_id = str(attendance_dict.get('attendance_id'))
        if not attendance_id: return False
        
        db.collection('attendance').document(attendance_id).set(attendance_dict)
        return True
    except Exception as e:
        print(f"Error syncing attendance {attendance_dict.get('attendance_id')} to Firebase: {e}")
        return False

def get_attendance_from_firebase(student_id):
    """
    Retrieves a list of attendance records for a given student from Firebase.
    Returns list of dicts on success, None on failure.
    """
    if not db: return None
    try:
        docs = db.collection('attendance').where('student_id', '==', int(student_id)).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error fetching attendance for student {student_id} from Firebase: {e}")
        return None

# ─── BROADCASTS ─────────────────────────────────────────────────────────────

def sync_broadcast_to_firebase(broadcast_dict):
    """
    Syncs a broadcast dictionary to the 'broadcasts' collection.
    Uses notification_id as the document ID.
    Returns True on success, False on failure.
    """
    if not db: return False
    try:
        broadcast_id = str(broadcast_dict.get('notification_id'))
        if not broadcast_id: return False
        
        # Convert datetime to string if necessary, firestore handles standard datetimes,
        # but safe to just let Firestore handle it if passed as datetime object.
        db.collection('broadcasts').document(broadcast_id).set(broadcast_dict)
        return True
    except Exception as e:
        print(f"Error syncing broadcast {broadcast_dict.get('notification_id')} to Firebase: {e}")
        return False

# ─── TIMETABLE ──────────────────────────────────────────────────────────────

def sync_timetable_to_firebase(timetable_dict):
    """
    Syncs a timetable dictionary to the 'timetable' collection.
    Uses timetable_id as the document ID.
    Returns True on success, False on failure.
    """
    if not db: return False
    try:
        timetable_id = str(timetable_dict.get('timetable_id'))
        if not timetable_id: return False
        
        # Note: time objects from psycopg2 might need string conversion
        for key, value in timetable_dict.items():
            if hasattr(value, 'isoformat'):
                timetable_dict[key] = value.isoformat()

        db.collection('timetable').document(timetable_id).set(timetable_dict)
        return True
    except Exception as e:
        print(f"Error syncing timetable {timetable_dict.get('timetable_id')} to Firebase: {e}")
        return False

# ─── ENROLLMENTS ────────────────────────────────────────────────────────────

def sync_enrollment_to_firebase(enrollment_dict):
    """
    Syncs an enrollment dictionary to the 'enrollments' collection.
    Uses enrollment_id as the document ID.
    Returns True on success, False on failure.
    """
    if not db: return False
    try:
        enrollment_id = str(enrollment_dict.get('enrollment_id'))
        if not enrollment_id: return False
        
        for key, value in enrollment_dict.items():
            if hasattr(value, 'isoformat'):
                enrollment_dict[key] = value.isoformat()

        db.collection('enrollments').document(enrollment_id).set(enrollment_dict)
        return True
    except Exception as e:
        print(f"Error syncing enrollment {enrollment_dict.get('enrollment_id')} to Firebase: {e}")
        return False
