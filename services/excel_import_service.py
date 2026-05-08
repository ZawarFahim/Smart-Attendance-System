"""
Excel Bulk Import Service for ATTENDIFY.

Responsibilities:
  - Read an Excel file using pandas (path comes from config or is passed at runtime)
  - Validate required columns (Column B=reg_no, Column C=name, Column E=email)
  - Auto-generate email if missing:  u{reg_no}@giki.edu.pk
  - Hash password using bcrypt (default password = reg_no)
  - Insert student records into PostgreSQL (Users + Students tables)
  - Skip duplicates using reg_no (safe ON CONFLICT handling)
  - Return an import summary dict: inserted_count, skipped_count, failed_rows

Column mapping (0-indexed in pandas after read_excel with header=None):
  Index 1 (Excel col B) → reg_no
  Index 2 (Excel col C) → name
  Index 4 (Excel col E) → email

Usage:
  from services.excel_import_service import import_students_from_excel
  summary = import_students_from_excel("path/to/file.xlsx")
"""

import pandas as pd
from config.db_config import get_connection

# ── Password hashing ──────────────────────────────────────────────────────────
# Try bcrypt first; fall back to the project's existing plaintext convention
# so the import still works even if bcrypt is not installed yet.
try:
    import bcrypt as _bcrypt

    def _hash_password(plain: str) -> str:
        """Hash a password with bcrypt. Returns a UTF-8 string."""
        return _bcrypt.hashpw(plain.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")

    def _verify_bcrypt(plain: str, hashed: str) -> bool:
        """Verify a bcrypt hash."""
        try:
            return _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False

    BCRYPT_AVAILABLE = True

except ImportError:
    # Fallback: store plaintext (matches existing project convention in utils/auth.py)
    def _hash_password(plain: str) -> str:  # type: ignore[misc]
        return plain

    BCRYPT_AVAILABLE = False
    print("[excel_import_service] WARNING: bcrypt not installed. "
          "Passwords will be stored as plaintext. "
          "Run: pip install bcrypt")


# ── Column indices (0-based after pandas read with header=None) ───────────────
_COL_REG_NO = 1   # Excel column B
_COL_NAME   = 2   # Excel column C
_COL_EMAIL  = 4   # Excel column E


def _generate_email(reg_no: str) -> str:
    """Auto-generate a GIKI email from a reg number."""
    safe = str(reg_no).strip().replace(" ", "").lower()
    return f"u{safe}@giki.edu.pk"


def _reg_no_exists(cur, reg_no: str) -> bool:
    """Check whether a reg_no is already in the Students table."""
    cur.execute("SELECT 1 FROM Students WHERE reg_no = %s LIMIT 1", (reg_no,))
    return cur.fetchone() is not None


def import_students_from_excel(
    filepath: str,
    default_dept_id: int = None,
) -> dict:
    """
    Import students from an Excel file into PostgreSQL.

    Parameters
    ----------
    filepath : str
        Absolute or relative path to the .xlsx / .xls file.
    default_dept_id : int, optional
        dept_id to assign imported students. If None, dept_id is set to NULL.

    Returns
    -------
    dict with keys:
        inserted_count  – number of rows successfully inserted
        skipped_count   – rows skipped because reg_no already exists
        failed_rows     – list of dicts describing rows that errored
                          Each dict: {row_index, reg_no, reason}
    """
    summary = {
        "inserted_count": 0,
        "skipped_count": 0,
        "failed_rows": [],
    }

    # ── 1. Load Excel file ────────────────────────────────────────────────────
    try:
        df = pd.read_excel(filepath, header=None, dtype=str)
    except FileNotFoundError:
        raise FileNotFoundError(f"Excel file not found: {filepath}")
    except Exception as exc:
        raise ValueError(f"Failed to read Excel file: {exc}") from exc

    # ── 2. Validate that required columns exist ───────────────────────────────
    required_indices = [_COL_REG_NO, _COL_NAME]
    for idx in required_indices:
        if idx >= len(df.columns):
            raise ValueError(
                f"Excel file has only {len(df.columns)} columns "
                f"(need at least {max(required_indices) + 1}). "
                f"Expected: col B=reg_no, col C=name, col E=email (optional)."
            )

    # ── 3. Process rows ───────────────────────────────────────────────────────
    conn = get_connection()
    if conn is None:
        raise ConnectionError("Cannot connect to the database. Check database.ini.")

    try:
        with conn.cursor() as cur:
            for excel_row_idx, row in df.iterrows():
                # Skip entirely empty rows
                reg_no = str(row.iloc[_COL_REG_NO]).strip() if len(row) > _COL_REG_NO else ""
                name   = str(row.iloc[_COL_NAME]).strip()   if len(row) > _COL_NAME   else ""

                if not reg_no or reg_no.lower() in ("nan", "none", ""):
                    continue  # silently skip header/blank rows
                if not name or name.lower() in ("nan", "none", ""):
                    summary["failed_rows"].append({
                        "row_index": excel_row_idx + 1,
                        "reg_no": reg_no,
                        "reason": "Missing student name",
                    })
                    continue

                # Email: use column E if present and non-empty, else auto-generate
                email = ""
                if _COL_EMAIL < len(row):
                    raw_email = str(row.iloc[_COL_EMAIL]).strip()
                    if raw_email.lower() not in ("nan", "none", ""):
                        email = raw_email
                if not email:
                    email = _generate_email(reg_no)

                # Username = reg_no (must be unique in Users table)
                username = reg_no

                # Default password = reg_no (hashed)
                password_hash = _hash_password(reg_no)

                try:
                    # ── Duplicate check by reg_no ─────────────────────────────
                    if _reg_no_exists(cur, reg_no):
                        summary["skipped_count"] += 1
                        continue

                    # ── Insert into Users ─────────────────────────────────────
                    cur.execute(
                        """
                        INSERT INTO Users (username, email, password_hash, role)
                        VALUES (%s, %s, %s, 'Student')
                        ON CONFLICT (username) DO NOTHING
                        RETURNING user_id
                        """,
                        (username, email, password_hash),
                    )
                    result = cur.fetchone()
                    if result is None:
                        # username conflict → skip
                        summary["skipped_count"] += 1
                        continue

                    user_id = result[0]

                    # ── Insert into Students ──────────────────────────────────
                    # Populate both name (new) and first_name/last_name (legacy)
                    # so existing code that reads first_name / last_name still works.
                    name_parts = name.split(" ", 1)
                    first_name = name_parts[0]
                    last_name  = name_parts[1] if len(name_parts) > 1 else ""

                    cur.execute(
                        """
                        INSERT INTO Students
                            (student_id, reg_no, name, first_name, last_name, dept_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (user_id, reg_no, name, first_name, last_name, default_dept_id),
                    )

                    conn.commit()
                    summary["inserted_count"] += 1

                except Exception as row_exc:
                    conn.rollback()
                    summary["failed_rows"].append({
                        "row_index": excel_row_idx + 1,
                        "reg_no": reg_no,
                        "reason": str(row_exc),
                    })

    finally:
        conn.close()

    return summary
