<<<<<<< HEAD
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_django.settings")

# Create the Celery app
app = Celery("chess_engine_comparator")

# Load config from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()
=======
import os
from celery import Celery
from celery.signals import worker_ready

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_django.settings")

# Create the Celery app
app = Celery("chess_engine_comparator")

# Load config from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

@worker_ready.connect
def setup_directories(**kwargs):
    """Set up media directories with proper permissions when worker starts"""
    from django.conf import settings
    from users.utils import ensure_directory_exists
    import os
    import datetime
    
    # Ensure main media directories exist
    media_root = settings.MEDIA_ROOT
    ensure_directory_exists(media_root)
    
    base_dirs = ['chess_bots', 'match_logs', 'match_records']
    for base_dir in base_dirs:
        ensure_directory_exists(os.path.join(media_root, base_dir))
    
    # Also create date-based subdirectories for current date
    today = datetime.date.today()
    year, month, day = today.year, today.month, today.day
    
    for base_dir in ['match_logs', 'match_records']:
        date_path = os.path.join(
            media_root,
            base_dir,
            str(year),
            str(month).zfill(2),
            str(day).zfill(2)
        )
        ensure_directory_exists(date_path)
>>>>>>> origin/TheDjangoMassRefactor
