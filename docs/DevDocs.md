# Developer Documentation for Chess Engine Comparator
This document provides essential information for developers working on the Chess Engine Comparator project, a Django-based platform that enables students and teachers to create and compete with chess bots.

See our [GitHub Issues](https://github.com/OrionGregory/ChessEngineComparator/issues) for a starting point of what we have left.

## Project Structure
The Chess Engine Comparator is built with Django and follows a standard Django project structure:

- ChessApp - Main Django project directory
    - web_django/ 
        - Project settings and configuration
    - users/ 
        - User authentication and core application functionality
    - hello/ 
        - Basic landing page app, mainly for testing at beginning
    - templates/ 
        - HTML templates
    - media/ 
        - User uploads (chess bots, match logs)
    - staticfiles/ 
        - Compiled static assets
        
## Important Models
CustomUser Model
The application uses a custom user model that extends Django's AbstractUser:

```py
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    created_at = models.DateTimeField(default=timezone.now)
    email_domain = models.CharField(max_length=255, blank=True)
    
    # Email is the primary authentication field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
```

ChessBot Model
```py
class ChessBot(models.Model):
    VISIBILITY_CHOICES = (
        ('private', 'Private'),
        ('public', 'Public'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chess_bots')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    file_path = models.FileField(upload_to=PathAndRename())
    version = models.PositiveIntegerField(default=1)
    # Additional fields...
```
Other important models include Tournament, Match, and TournamentParticipant.

## Authentication Flow
The application uses django-allauth for OAuth authentication, with a focus on Google login:
    1. Regular username/password signup is disabled via NoSignupAccountAdapter
    2. OAuth login (primarily Google) is handled through CustomSocialAccountAdapter
    3. Role assignment (student or teacher) is based on email domains or explicit email lists

## API Endpoints
The project uses Django Rest Framework for API endpoints. Main ViewSets include:

    - ChessBotViewSet - Upload, manage, and activate chess bots
    - TournamentViewSet - Create and manage tournaments
    - MatchViewSet - View match details and logs
    - ClassGroupViewSet - Manage student class groups (teacher only)
    - StudentViewSet - View and manage students (teacher only)

## Background Tasks
    Celery is used for background processing:
    ```sh
    # Start the Celery worker with:
    celery -A web_django worker --loglevel=info
    ```
    Key tasks include running chess matches, processing tournament results, and generating logs.

## File Management
Chess bot files are stored under media/chess_bots/ using directory structure by date. Match logs and records are stored under media/match_logs/ and media/match_records/.

## Adding New Features
When adding a new feature:
    1. Create or modify models in the appropriate app
    2. Run python [manage.py](http://_vscodecontentref_/20) makemigrations and python [manage.py](http://_vscodecontentref_/21) migrate
    3. Update serializers if the feature needs API support
    4. Create or update views, viewsets and templates
    5. Add URL routes in the appropriate urls.py file

## Common Issues
File Permissions
    If you encounter permission issues with media files:
    ```sh
    python ChessApp/manage.py init_media_dirs
    ```
Database Connection
    Ensure PostgreSQL is running and credentials in .env are correct.

## Archetecture
- PostgreSQL for the database
- Redis for Celery task queue
- JWT for API authentication
- Class-based views for most functionality
- Django REST Framework for API endpoints