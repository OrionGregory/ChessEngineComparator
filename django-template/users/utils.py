import os
import uuid
import stat
from pathlib import Path
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

# Define maximum file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

def validate_file_size(file):
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(f"File size cannot exceed {MAX_FILE_SIZE/(1024*1024)}MB.")

def validate_file_extension(file):
    ext = os.path.splitext(file.name)[1]
    if ext.lower() != '.py':
        raise ValidationError('Only Python (.py) files are allowed.')

def ensure_directory_exists(path):
    """
    Ensure a directory exists with proper permissions.
    Creates the directory and any parent directories if needed.
    Attempts to set permissions but gracefully handles failures.
    """
    # Create directory if it doesn't exist
    os.makedirs(path, exist_ok=True)
    
    try:
        # Try to set directory permissions to be world-writable (rwxrwxrwx)
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0o777
    except Exception as e:
        import logging
        logging.warning(f"Could not set permissions on {path}: {e}")
        
        # Alternative approach: try using subprocess to change permissions
        try:
            import subprocess
            subprocess.run(['chmod', '777', path], check=False)
        except Exception:
            # If that also fails, just continue - the directory exists which is the main requirement
            pass

@deconstructible
class PathAndRename:
    """
    Store bot files as: chess_bots/<bot_uuid>_<original_filename>
    """
    def __init__(self, sub_path='chess_bots'):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # Use bot UUID if available, else generate a new one
        if instance.pk:
            uid = str(instance.pk)
        else:
            uid = uuid.uuid4().hex
        filename = f"{uid}_{instance.name.replace(' ', '_')}.{ext}"
        
        # Ensure the directory exists with proper permissions
        from django.conf import settings
        directory = os.path.join(settings.MEDIA_ROOT, self.sub_path)
        ensure_directory_exists(directory)
        
        return os.path.join(self.sub_path, filename)