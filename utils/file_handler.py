import os

def validate_file(filepath, allowed_extensions):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    if not any(filepath.lower().endswith(ext.lower()) for ext in allowed_extensions):
        raise ValueError(f"Invalid file type: {filepath}. Allowed: {allowed_extensions}")

