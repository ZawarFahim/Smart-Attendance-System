import csv
import os

def export_to_csv(headers: list, data: list, filepath: str) -> bool:
    """
    Exports a list of dicts/tuples to a CSV file.
    
    :param headers: List of column names
    :param data: List of dictionaries matching the headers
    :param filepath: Complete path string to save the CSV
    """
    try:
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in data:
                # Extract dictionary values in order of headers if dictionary
                if isinstance(row, dict):
                    writer.writerow([row.get(h, "") for h in headers])
                else:
                    writer.writerow(row)
        return True
    except Exception as e:
        print(f"Error exporting CSV: {e}")
        return False
