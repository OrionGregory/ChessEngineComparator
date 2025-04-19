from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import os
import uuid

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    created_at = models.DateTimeField(default=timezone.now)
    
    # Add educational domain field to help determine role
    email_domain = models.CharField(max_length=255, blank=True)
    
    # Make email the primary field for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Username still required for Django admin
    
    class Meta:
        db_table = 'auth_user'
        swappable = 'AUTH_USER_MODEL'
        
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        # Extract domain from email for role assignment
        if self.email and not self.email_domain:
            self.email_domain = self.email.split('@')[-1]
        super().save(*args, **kwargs)

# Add this new model for bot uploads
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
    file_path = models.FileField(upload_to='chess_bots/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    version = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} (v{self.version}) - {self.owner.email}"
    
    def get_file_name(self):
        return os.path.basename(self.file_path.name)
    
    def increment_version(self):
        self.version += 1
        self.save(update_fields=['version'])

class Tournament(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_tournaments')
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    participants = models.ManyToManyField(ChessBot, through='TournamentParticipant')
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def start_tournament(self):
        self.status = 'in_progress'
        self.save()
        
    def complete_tournament(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        
    def cancel_tournament(self):
        self.status = 'cancelled'
        self.save()


class TournamentParticipant(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    bot = models.ForeignKey(ChessBot, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    rank = models.IntegerField(null=True, blank=True)
    
    class Meta:
        unique_together = ('tournament', 'bot')


class Match(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    )
    
    RESULT_CHOICES = (
        ('white_win', 'White Win'),
        ('black_win', 'Black Win'),
        ('draw', 'Draw'),
        ('timeout', 'Timeout'),
        ('error', 'Error'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    white_bot = models.ForeignKey(ChessBot, on_delete=models.CASCADE, related_name='white_matches')
    black_bot = models.ForeignKey(ChessBot, on_delete=models.CASCADE, related_name='black_matches')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, null=True, blank=True)
    pgn_file = models.FileField(upload_to='match_records/%Y/%m/%d/', null=True, blank=True)
    log_file = models.FileField(upload_to='match_logs/%Y/%m/%d/', null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Match: {self.white_bot.name} vs {self.black_bot.name}"
    
    def start_match(self):
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()
    
    def complete_match(self, result):
        self.status = 'completed'
        self.result = result
        self.completed_at = timezone.now()
        self.save()
        
        # Update tournament participant scores
        if result == 'white_win':
            self._update_score(self.white_bot, 1)
            self._update_score(self.black_bot, 0)
        elif result == 'black_win':
            self._update_score(self.white_bot, 0)
            self._update_score(self.black_bot, 1)
        elif result == 'draw':
            self._update_score(self.white_bot, 0.5)
            self._update_score(self.black_bot, 0.5)
    
    def _update_score(self, bot, points):
        participant = TournamentParticipant.objects.get(
            tournament=self.tournament,
            bot=bot
        )
        participant.score += points
        participant.save()


class ClassGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='teaching_classes')
    students = models.ManyToManyField(CustomUser, related_name='enrolled_classes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
