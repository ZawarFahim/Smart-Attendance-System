import os
import shutil
from pathlib import Path
from PIL import Image
from db import fetch_all, execute_query, get_connection

# Define base upload directory
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads" / "student_profiles"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
MAX_IMAGE_SIZE = (500, 500) # Maximum dimensions

def is_valid_image(file_path):
    """Validate image extension and format."""
    ext = Path(file_path).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def upload_profile_image(student_id, source_file_path):
    """
    Uploads, resizes, and saves a student profile image.
    Updates the database using the upsert procedure.
    Returns (True, message) on success, (False, error) on failure.
    """
    if not os.path.exists(source_file_path):
        return False, "Source file does not exist."
        
    if not is_valid_image(source_file_path):
        return False, "Invalid image format. Allowed: .png, .jpg, .jpeg"

    # Generate new filename
    ext = Path(source_file_path).suffix.lower()
    image_name = f"student_{student_id}_profile{ext}"
    dest_path = UPLOAD_DIR / image_name

    try:
        # Resize and save
        with Image.open(source_file_path) as img:
            img.thumbnail(MAX_IMAGE_SIZE)
            img.save(dest_path)
            
        # Update database
        # Make sure path is relative or absolute, relative is better for portability
        rel_path = f"uploads/student_profiles/{image_name}"
        
        query = "CALL upsert_student_profile_image(%s, %s, %s)"
        success = execute_query(query, (student_id, image_name, rel_path))
        
        if success:
            return True, "Profile image uploaded successfully."
        else:
            # Rollback file if db update fails
            if dest_path.exists(): dest_path.unlink()
            return False, "Database update failed."

    except Exception as e:
        return False, f"Error processing image: {e}"

def get_student_profile_image(student_id):
    """
    Retrieves the profile image path for a student.
    Returns absolute path if exists, otherwise None.
    """
    query = "SELECT image_path FROM StudentProfileImages WHERE student_id = %s"
    result = fetch_all(query, (student_id,))
    
    if result and result[0].get('image_path'):
        rel_path = result[0]['image_path']
        abs_path = Path(__file__).resolve().parent.parent / rel_path
        if abs_path.exists():
            return str(abs_path)
            
    return None
