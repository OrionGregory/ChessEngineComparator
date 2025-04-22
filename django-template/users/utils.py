import os
import uuid
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

# Define maximum file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

def validate_file_size(file):
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(f"File size cannot exceed {MAX_FILE_SIZE/(1024*1024)}MB.")

def validate_file_extension(file):
    ext = os.path.splitext(file.name)[1]
    valid_extensions = ['.py']
    
    if ext.lower() not in valid_extensions:
        raise ValidationError('Only Python (.py) files are allowed.')

@deconstructible
class PathAndRename:
    """
    Generate unique path for uploading files.
    Example: chess_bots/user_<id>/yyyy/mm/dd/<uuid>_<filename>
    """
    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = f"{uuid.uuid4().hex}_{instance.name.replace(' ', '_')}.{ext}"
        
        # Generate path format: chess_bots/user_<id>/yyyy/mm/dd/<uuid>_<filename>
        return os.path.join(
            'chess_bots',
            f'user_{instance.owner.id}',
            self.sub_path, 
            filename
        )