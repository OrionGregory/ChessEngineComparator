from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import os
import uuid
from django.core.files.base import ContentFile

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
        """Mark tournament as complete and finalize scores"""
        # First recalculate all scores to ensure they're accurate
        self.recalculate_scores()
        
        # Then ensure tournament is marked as completed
        if self.status != 'completed':
            self.status = 'completed'
            self.completed_at = timezone.now() 
            self.save()
        
    def cancel_tournament(self):
        self.status = 'cancelled'
        self.save()
    
    def recalculate_scores(self):
        """Reset and recalculate scores for all participants"""
        from django.db import transaction
        
        with transaction.atomic():
            # Reset all scores to zero
            TournamentParticipant.objects.filter(tournament=self).update(score=0.0)
            
            # Get all completed matches and update scores
            completed_matches = Match.objects.filter(
                tournament=self,
                status='completed'
            )
            
            # Process each match
            for match in completed_matches:
                if match.result == 'white_win':
                    try:
                        participant = TournamentParticipant.objects.get(
                            tournament=self,
                            bot=match.white_bot
                        )
                        participant.score += 1.0
                        participant.save()
                    except TournamentParticipant.DoesNotExist:
                        pass
                    
                elif match.result == 'black_win':
                    try:
                        participant = TournamentParticipant.objects.get(
                            tournament=self,
                            bot=match.black_bot
                        )
                        participant.score += 1.0
                        participant.save()
                    except TournamentParticipant.DoesNotExist:
                        pass
                    
                elif match.result == 'draw':
                    try:
                        white_participant = TournamentParticipant.objects.get(
                            tournament=self,
                            bot=match.white_bot
                        )
                        white_participant.score += 0.5
                        white_participant.save()
                    except TournamentParticipant.DoesNotExist:
                        pass
                        
                    try:
                        black_participant = TournamentParticipant.objects.get(
                            tournament=self,
                            bot=match.black_bot
                        )
                        black_participant.score += 0.5
                        black_participant.save()
                    except TournamentParticipant.DoesNotExist:
                        pass
            
            # Check if tournament should be marked as complete
            if self.status == 'in_progress':
                total_matches = Match.objects.filter(tournament=self).count()
                completed_count = completed_matches.count()
                
                if total_matches > 0 and total_matches == completed_count:
                    self.status = 'completed'
                    self.completed_at = timezone.now()
                    self.save()
            
            return True

class TournamentParticipant(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    bot = models.ForeignKey(ChessBot, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0)  # Using float for half-points in draws
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
    round = models.PositiveIntegerField(null=True, blank=True)  # Added round field
    
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
    
    def save_log_file(self, log_content):
        """Save the log content to the log_file field"""
        log_file = ContentFile(log_content.encode('utf-8'))
        self.log_file.save(f"match_{self.id}_log.txt", log_file)
    
    def update_scores(self):
        """Update tournament participant scores based on match results"""
        # Only process if match is completed and part of a tournament
        if self.status != 'completed' or not self.tournament:
            return False
            
        # Get participants
        try:
            white_participant = TournamentParticipant.objects.get(
                tournament=self.tournament,
                bot=self.white_bot
            )
            
            black_participant = TournamentParticipant.objects.get(
                tournament=self.tournament,
                bot=self.black_bot
            )
            
            # Update scores based on match result
            if self.result == 'white_win':
                white_participant.score += 1.0
                white_participant.save()
                return True
            elif self.result == 'black_win':
                black_participant.score += 1.0
                black_participant.save()
                return True
            elif self.result == 'draw':
                white_participant.score += 0.5
                black_participant.score += 0.5
                white_participant.save()
                black_participant.save()
                return True
                
            return False  # Unrecognized result
            
        except TournamentParticipant.DoesNotExist:
            return False  # Participant not found
        except Exception as e:
            import logging
            logging.error(f"Error updating scores: {str(e)}")
            return False

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
