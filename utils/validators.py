import re

def is_valid_email(email: str) -> bool:
    """Check if the provided email has a valid format."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def is_not_empty(*fields: str) -> bool:
    """Ensure all provided string fields are not empty or just whitespace."""
    for field in fields:
        if not field or not str(field).strip():
            return False
    return True

def is_valid_numeric(value: str) -> bool:
    """Check if the string contains only digits."""
    return str(value).isdigit()

def is_valid_date(date_string: str) -> bool:
    """Check if the date matches YYYY-MM-DD pattern."""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_string))
