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
    if ext.lower() != '.py':
        raise ValidationError('Only Python (.py) files are allowed.')

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
        return os.path.join(self.sub_path, filename)