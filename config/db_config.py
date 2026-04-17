from configparser import ConfigParser
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor

def _read_db_config(filename=None, section="postgresql"):
    """
    Read database configuration from database.ini using ConfigParser.
    Expected section keys: host, database, user, password, port.
    """
    base_dir = Path(__file__).resolve().parent.parent
    config_path = Path(filename) if filename else base_dir / "database.ini"

    parser = ConfigParser()
    parser.read(config_path)

    if not parser.has_section(section):
        raise Exception(f"Section '{section}' not found in {config_path}")

    params = {}
    for key, value in parser.items(section):
        params[key] = value
    return params

def get_connection():
    """Returns a new psycopg2 database connection."""
    try:
        db_params = _read_db_config()
        conn = psycopg2.connect(**db_params)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def fetch_all(query, params=None):
    """Executes a SELECT query and returns all rows as dictionaries."""
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            return cur.fetchall()
    except Exception as e:
        print(f"Database fetch_all error: {e}")
        return []
    finally:
        conn.close()

def execute_query(query, params=None):
    """Executes an INSERT, UPDATE, or DELETE query and commits."""
    conn = get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            conn.commit()
            return True
    except Exception as e:
        print(f"Database execute error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
