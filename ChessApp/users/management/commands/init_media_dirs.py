import os
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime

class Command(BaseCommand):
    help = 'Initialize media directories with proper permissions using shell commands'

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        today = datetime.now()
        year, month, day = today.year, today.month, today.day
        
        # Make sure base media directory exists
        if not os.path.exists(media_root):
            os.makedirs(media_root, exist_ok=True)
        
        # Use shell commands to create and set permissions
        self.stdout.write(f"Creating media directories for {year}/{month}/{day}")
        
        # Use subprocess to run mkdir -p and chmod without failing on permission errors
        try:
            # Create base directories
            subprocess.run([
                'mkdir', '-p',
                os.path.join(media_root, 'chess_bots'),
                os.path.join(media_root, 'match_logs', str(year), str(month).zfill(2), str(day).zfill(2)),
                os.path.join(media_root, 'match_records', str(year), str(month).zfill(2), str(day).zfill(2))
            ])
            
            # Try to set permissions but don't fail if it doesn't work
            subprocess.run(['chmod', '-R', '777', media_root], check=False)
            
            self.stdout.write(self.style.SUCCESS(f"Media directories created in {media_root}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating directories: {e}"))
            # Try individual directory creation if bulk creation failed
            for path in [
                os.path.join(media_root, 'chess_bots'),
                os.path.join(media_root, 'match_logs'),
                os.path.join(media_root, 'match_logs', str(year)),
                os.path.join(media_root, 'match_logs', str(year), str(month).zfill(2)),
                os.path.join(media_root, 'match_logs', str(year), str(month).zfill(2), str(day).zfill(2)),
                os.path.join(media_root, 'match_records'),
                os.path.join(media_root, 'match_records', str(year)),
                os.path.join(media_root, 'match_records', str(year), str(month).zfill(2)),
                os.path.join(media_root, 'match_records', str(year), str(month).zfill(2), str(day).zfill(2))
            ]:
                try:
                    os.makedirs(path, exist_ok=True)
                    self.stdout.write(f"Created {path}")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Couldn't create {path}: {e}"))