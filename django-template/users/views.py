from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import CustomUser, ChessBot, Tournament, TournamentParticipant, Match, ClassGroup
from .serializers import (ChessBotSerializer, ChessBotUploadSerializer, StudentSerializer, StudentDetailSerializer,
                         ClassGroupSerializer, ClassGroupDetailSerializer,
                         TournamentSerializer, TournamentDetailSerializer, MatchSerializer)
from django.db.models import Q
from .services import generate_round_robin_matches, generate_round_robin_matches_with_rounds
from .tasks import run_chess_match
from celery import chain, group


@csrf_exempt
def logout_view(request):
    """
    Logs out the user and returns success status
    """
    logout(request)
    response = JsonResponse({'success': True})
    response["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response["Access-Control-Allow-Credentials"] = "true"
    return response

@login_required
def user_info(request):
    """Return user authentication status and details"""
    user = request.user
    return JsonResponse({
        "isAuthenticated": user.is_authenticated,
        "email": user.email,
        "role": "teacher" if user.email.endswith("@teacher.edu") else "student",
        "username": user.username,
    })

def google_login(request):
    """
    Redirects to Google OAuth2 authentication
    """
    # Get the 'next' parameter to redirect after authentication
    next_url = request.GET.get('next', '/')
    
    # Using django-allauth's URL pattern
    return redirect('/accounts/google/login/?process=login&next=' + next_url)

def logout_view(request):
    """
    Logs out the user and returns success status
    """
    logout(request)
    return JsonResponse({'success': True})

# Add this function if you haven't already defined it
def join_tournament(request, id):
    """
    Allow a user to join a tournament
    """
    # In a real implementation, this would create a participant record
    # For now, just return success
    if request.method == 'POST':
        # Your logic to add user to tournament
        return JsonResponse({'success': True, 'tournament_id': id})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def home(request):
    """Redirect to React app's homepage"""
    return redirect('http://localhost:3000/')

def login(request):
    """Render the login page with direct Google OAuth option"""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'users/login.html')

def google_login_redirect(request):
    """Direct redirect to Google OAuth without template tag processing"""
    return redirect('/accounts/google/login/')  # Note: using root accounts, not /users/accounts/

@login_required
def profile(request):
    """User profile view"""
    return render(request, 'users/profile.html', {
        'user': request.user
    })

@login_required
def teacher_dashboard(request):
    """Teacher dashboard view"""
    if request.user.role != 'teacher':
        return redirect('home')
    return render(request, 'users/teacher_dashboard.html', {'user': request.user})

@login_required
def student_detail(request, student_id):
    """View for detailed student information"""
    if request.user.role != 'teacher':
        return redirect('home')
    
    try:
        student = CustomUser.objects.get(id=student_id, role='student')
    except CustomUser.DoesNotExist:
        return redirect('teacher_dashboard')
    
    return render(request, 'users/student_detail.html', {
        'user': request.user,
        'student': student
    })

@login_required
def class_detail(request, class_id):
    """View for detailed class information"""
    if request.user.role != 'teacher':
        return redirect('home')
    
    try:
        class_group = ClassGroup.objects.get(id=class_id, teacher=request.user)
    except ClassGroup.DoesNotExist:
        return redirect('teacher_dashboard')
    
    return render(request, 'users/class_detail.html', {
        'user': request.user,
        'class_group': class_group
    })

@login_required
def tournament_detail(request, tournament_id):
    """View for detailed tournament information"""
    if request.user.role != 'teacher':
        return redirect('home')
    
    try:
        tournament = Tournament.objects.get(id=tournament_id, created_by=request.user)
    except Tournament.DoesNotExist:
        return redirect('teacher_dashboard')
    
    return render(request, 'users/tournament_detail.html', {
        'user': request.user,
        'tournament': tournament
    })

class TokenObtainView(APIView):
    """Get JWT tokens for the authenticated user (for React frontend)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
            }
        })

class ChessBotViewSet(viewsets.ModelViewSet):
    """API endpoint for chess bots"""
    serializer_class = ChessBotSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)  # Added JSONParser
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter bots based on ownership and visibility:
        - User can see all their own bots
        - User can see others' public bots
        - Teachers can see all bots
        """
        user = self.request.user
        if user.role == 'teacher':
            return ChessBot.objects.all()
        return ChessBot.objects.filter(
            Q(owner=user) | Q(visibility='public')
        )
    
    def get_serializer_class(self):
        """Use different serializers for list/retrieve vs create"""
        if self.action == 'create' or self.action == 'update':
            return ChessBotUploadSerializer
        return ChessBotSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new bot with uploaded file"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Set owner automatically
            bot = serializer.save()
            return Response(
                ChessBotSerializer(bot).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def perform_create(self, serializer):
        """Set owner to current user when creating a bot"""
        serializer.save(owner=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """
        Update a bot with the following restrictions:
        - Teachers can update any bot
        - Students can only update their own bots that are in draft status
        """
        bot = self.get_object()
        user = request.user
        
        # Check permissions
        if user.role == 'teacher':
            # Teachers can update any bot
            pass
        elif bot.owner == user:
            # Students can only update their own bots in draft status
            if bot.status != 'draft':
                return Response(
                    {"error": "You can only edit bots in draft status"},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {"error": "You don't have permission to modify this bot"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Get partial=True if it's a PATCH request
        partial = kwargs.pop('partial', request.method == 'PATCH')
        
        serializer = self.get_serializer(bot, data=request.data, partial=partial)
        if serializer.is_valid():
            bot = serializer.save()
            return Response(ChessBotSerializer(bot).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a bot with restrictions:
        - Teachers can delete any bot
        - Students can only delete their own bots in draft status
        """
        bot = self.get_object()
        user = request.user
        
        # Check permissions
        if user.role == 'teacher':
            # Teachers can delete any bot
            pass
        elif bot.owner == user:
            # Students can only delete their own bots in draft status
            if bot.status != 'draft':
                return Response(
                    {"error": "You can only delete bots in draft status"},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {"error": "You don't have permission to delete this bot"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        bot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a bot (only owner can activate)"""
        bot = self.get_object()
        
        # Check ownership - students can only activate their own bots
        if bot.owner != request.user:
            return Response(
                {"error": "You don't have permission to activate this bot"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if bot is in draft state
        if bot.status != 'draft':
            return Response(
                {"error": "Only draft bots can be activated"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Activate the bot
        bot.status = 'active'
        bot.save()
        
        return Response({"message": "Bot activated successfully"})
        
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a bot (only owner can archive their own bots)"""
        bot = self.get_object()
        
        # Check ownership - students can only archive their own bots
        if bot.owner != request.user:
            return Response(
                {"error": "You don't have permission to archive this bot"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if bot is in active state (only active bots can be archived)
        if bot.status != 'active':
            return Response(
                {"error": "Only active bots can be archived"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Archive the bot
        bot.status = 'archived'
        bot.save()
        
        return Response({"message": "Bot archived successfully"})

class IsTeacher(permissions.BasePermission):
    """Permission to only allow teachers to access view"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'
    
class IsTeacherOrReadOnly(permissions.BasePermission):
    """Permission to allow teachers to edit, others to read"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'teacher'

class StudentViewSet(viewsets.ModelViewSet):
    """API endpoint for managing students (teacher only)"""
    serializer_class = StudentSerializer
    permission_classes = [IsTeacher]
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'username']
    
    def get_queryset(self):
        """Only return users with student role"""
        return CustomUser.objects.filter(role='student')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StudentDetailSerializer
        return StudentSerializer
    
    @action(detail=True, methods=['get'])
    def bots(self, request, pk=None):
        """Get all bots for a specific student"""
        student = self.get_object()
        bots = ChessBot.objects.filter(owner=student)
        serializer = ChessBotSerializer(bots, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a student (teachers only)"""
        if request.user.role != 'teacher':
            return Response(
                {"error": "Only teachers can remove students"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        student = self.get_object()
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ClassGroupViewSet(viewsets.ModelViewSet):
    """API endpoint for managing class groups"""
    serializer_class = ClassGroupSerializer
    permission_classes = [IsTeacher]
    
    def get_queryset(self):
        """Only return class groups where user is the teacher"""
        return ClassGroup.objects.filter(teacher=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClassGroupDetailSerializer
        return ClassGroupSerializer
    
    def perform_create(self, serializer):
        """Set teacher to current user when creating"""
        serializer.save(teacher=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        """Add a student to the class"""
        class_group = self.get_object()
        student_id = request.data.get('student_id')
        
        try:
            student = CustomUser.objects.get(id=student_id, role='student')
            class_group.students.add(student)
            return Response({"message": f"Added {student.email} to {class_group.name}"})
        except CustomUser.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_student(self, request, pk=None):
        """Remove a student from the class"""
        class_group = self.get_object()
        student_id = request.data.get('student_id')
        
        try:
            student = CustomUser.objects.get(id=student_id)
            if student in class_group.students.all():
                class_group.students.remove(student)
                return Response({"message": f"Removed {student.email} from {class_group.name}"})
            else:
                return Response({"error": "Student not in class"}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

class TournamentViewSet(viewsets.ModelViewSet):
    """API endpoint for managing tournaments"""
    permission_classes = [IsTeacher]
    
    def get_queryset(self):
        """Return tournaments created by current user"""
        return Tournament.objects.filter(created_by=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TournamentDetailSerializer
        return TournamentSerializer
    
    def perform_create(self, serializer):
        """Set created_by to current user when creating"""
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        """Debug tournament creation"""
        print(f"Request data: {request.data}")
        print(f"User: {request.user.email} (authenticated: {request.user.is_authenticated})")
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def start_tournament(self, request, pk=None):
        """Start the tournament and generate matches"""
        tournament = self.get_object()
        
        if tournament.status != 'scheduled':
            return Response({"error": "Tournament can only be started from scheduled state"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Check if there are enough active participants
        participants = list(tournament.participants.filter(status='active'))
        if len(participants) < 2:
            return Response({"error": "Need at least 2 active bots to start tournament"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Start the tournament
        tournament.start_tournament()
        
        # Choose matchmaking method based on presence of 'use_rounds' parameter
        use_rounds = request.data.get('use_rounds', False)
        matches_created = 0
        match_ids = []
        
        if use_rounds:
            # Generate round-robin tournament matches organized by rounds
            rounds = generate_round_robin_matches_with_rounds(tournament)
            
            # Create match objects in the database with round information
            for round_num, pairings in rounds.items():
                for white_bot, black_bot in pairings:
                    match = Match.objects.create(
                        tournament=tournament,
                        white_bot=white_bot,
                        black_bot=black_bot,
                        round=round_num
                    )
                    matches_created += 1
                    match_ids.append(str(match.id))
                    
                    # Optionally create reverse matches (black/white switched) in the same round
                    if request.data.get('double_round_robin', False):
                        match = Match.objects.create(
                            tournament=tournament,
                            white_bot=black_bot,
                            black_bot=white_bot,
                            round=round_num
                        )
                        matches_created += 1
                        match_ids.append(str(match.id))
        else:
            # Generate standard round-robin tournament matches
            match_pairings = generate_round_robin_matches(tournament)
            
            # Create match objects in the database
            for white_bot, black_bot in match_pairings:
                match = Match.objects.create(
                    tournament=tournament,
                    white_bot=white_bot,
                    black_bot=black_bot
                )
                matches_created += 1
                match_ids.append(str(match.id))
                
                # Optionally create reverse matches (black/white switched)
                if request.data.get('double_round_robin', False):
                    match = Match.objects.create(
                        tournament=tournament,
                        white_bot=black_bot,
                        black_bot=white_bot
                    )
                    matches_created += 1
                    match_ids.append(str(match.id))
        
        # Start a background tasks to run the matches
        # Dispatch Celery tasks for each match
        for match_id in match_ids:
            run_chess_match.delay(match_id)
        
        return Response({
            "message": "Tournament started successfully", 
            "matches_created": matches_created
        })

    @action(detail=True, methods=['post'])
    def add_bot(self, request, pk=None):
        """Add a bot to the tournament"""
        tournament = self.get_object()
        bot_id = request.data.get('bot_id')
        
        if tournament.status != 'scheduled':
            return Response({"error": "Can only add bots to scheduled tournaments"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            bot = ChessBot.objects.get(id=bot_id, status='active')
            # Check if the bot is already in the tournament
            if TournamentParticipant.objects.filter(tournament=tournament, bot=bot).exists():
                return Response({"error": "Bot already in tournament"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            TournamentParticipant.objects.create(tournament=tournament, bot=bot)
            return Response({"message": f"Added {bot.name} to tournament"})
        except ChessBot.DoesNotExist:
            return Response({"error": "Bot not found or not active"}, 
                            status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_bot(self, request, pk=None):
        """Remove a bot from the tournament"""
        tournament = self.get_object()
        bot_id = request.data.get('bot_id')
        
        if tournament.status != 'scheduled':
            return Response({"error": "Can only remove bots from scheduled tournaments"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            participant = TournamentParticipant.objects.get(
                tournament=tournament, 
                bot__id=bot_id
            )
            participant.delete()
            return Response({"message": "Bot removed from tournament"})
        except TournamentParticipant.DoesNotExist:
            return Response({"error": "Bot not in tournament"}, 
                            status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def download_results(self, request, pk=None):
        """Download tournament results as CSV"""
        tournament = self.get_object()
        
        if tournament.status != 'completed':
            return Response({"error": "Tournament not completed"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Generate CSV content
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Bot Name', 'Owner', 'Score', 'Rank'])
        
        # Write data
        participants = TournamentParticipant.objects.filter(tournament=tournament).order_by('-score')
        for idx, participant in enumerate(participants, 1):
            writer.writerow([
                participant.bot.name,
                participant.bot.owner.email,
                participant.score,
                idx  # Assign rank based on sort order
            ])
            
            # Update rank in database
            participant.rank = idx
            participant.save(update_fields=['rank'])
        
        # Create response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=tournament_{tournament.id}_results.csv'
        return response
    
    @action(detail=True, methods=['post'])
    def cancel_tournament(self, request, pk=None):
        """Cancel the tournament"""
        tournament = self.get_object()
        
        if tournament.status == 'completed':
            return Response({"error": "Cannot cancel completed tournament"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        tournament.cancel_tournament()
        return Response({"message": "Tournament cancelled"})

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a bot as participant to the tournament"""
        tournament = self.get_object()
        
        if tournament.status != 'scheduled':
            return Response({"error": "Can only add participants to scheduled tournaments"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        bot_id = request.data.get('bot_id')
        if not bot_id:
            return Response({"error": "Bot ID is required"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Print debug info
            print(f"Adding bot {bot_id} to tournament {tournament.id}")
            
            bot = ChessBot.objects.get(id=bot_id)
            
            # Check if the bot is already a participant
            if TournamentParticipant.objects.filter(tournament=tournament, bot=bot).exists():
                return Response({"error": "Bot is already a participant in this tournament"}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            # Add the bot as a participant
            participant = TournamentParticipant.objects.create(tournament=tournament, bot=bot)
            print(f"Created participant: {participant.id}")
            
            # Use detail serializer to return updated tournament data
            serializer = TournamentDetailSerializer(tournament)
            return Response({
                "message": "Bot added to tournament successfully",
                "tournament": serializer.data
            })
        except ChessBot.DoesNotExist:
            return Response({"error": "Bot not found"}, 
                           status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error adding participant: {str(e)}")
            return Response({"error": f"Error adding bot: {str(e)}"}, 
                           status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """Remove a bot as participant from the tournament"""
        tournament = self.get_object()
        
        if tournament.status != 'scheduled':
            return Response({"error": "Can only remove participants from scheduled tournaments"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        bot_id = request.data.get('bot_id')
        if not bot_id:
            return Response({"error": "Bot ID is required"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the bot is a participant
        try:
            participant = TournamentParticipant.objects.get(tournament=tournament, bot_id=bot_id)
            participant.delete()
            return Response({"message": "Bot removed from tournament successfully"})
        except TournamentParticipant.DoesNotExist:
            return Response({"error": "Bot is not a participant in this tournament"}, 
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel the tournament"""
        tournament = self.get_object()
        
        if tournament.status not in ['scheduled', 'in_progress']:
            return Response({"error": "Can only cancel scheduled or in-progress tournaments"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        tournament.cancel_tournament()
        
        return Response({"message": "Tournament cancelled successfully"})
        
    @action(detail=True, methods=['delete', 'post'])
    def delete_tournament(self, request, pk=None):
        """Delete a tournament and all related data"""
        tournament = self.get_object()
        
        # Check if the user is the tournament creator
        if tournament.created_by != request.user:
            return Response({"error": "You can only delete tournaments that you created"}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        # Store the name for the response message
        tournament_name = tournament.name
        
        try:
            # Print debug information
            print(f"Deleting tournament: {tournament_name} (ID: {tournament.id})")
            
            # Delete all related matches and participants first (will cascade in most cases)
            match_count = Match.objects.filter(tournament=tournament).count()
            participant_count = TournamentParticipant.objects.filter(tournament=tournament).count()
            
            print(f"Found {match_count} matches and {participant_count} participants to delete")
            
            Match.objects.filter(tournament=tournament).delete()
            TournamentParticipant.objects.filter(tournament=tournament).delete()
            
            # Delete the tournament itself
            tournament.delete()
            print(f"Tournament {tournament_name} successfully deleted")
            
            return Response({"message": f"Tournament '{tournament_name}' deleted successfully"})
        except Exception as e:
            print(f"Error deleting tournament: {str(e)}")
            return Response(
                {"error": f"Error deleting tournament: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MatchViewSet(viewsets.ModelViewSet):
    """API endpoint for managing matches"""
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [IsTeacher]
    
    def get_queryset(self):
        """Filter matches by tournament_id if provided"""
        queryset = Match.objects.all()
        tournament_id = self.request.query_params.get('tournament')
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        return queryset
    
    @action(detail=True, methods=['get'])
    def download_pgn(self, request, pk=None):
        """Download PGN file of the match"""
        match = self.get_object()
        
        if not match.pgn_file:
            return Response({"error": "No PGN file available"}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        response = HttpResponse(match.pgn_file, content_type='application/x-chess-pgn')
        response['Content-Disposition'] = f'attachment; filename=match_{match.id}.pgn'
        return response
    
    @action(detail=True, methods=['get'])
    def download_log(self, request, pk=None):
        """Download log file of the match"""
        match = self.get_object()
        
        if not match.log_file:
            return Response({"error": "No log file available"}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        response = HttpResponse(match.log_file, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename=match_{match.id}_log.txt'
        return response

    @action(detail=True, methods=['post'])
    def run_match(self, request, pk=None):
        """Run a specific match"""
        match = self.get_object()
        
        if match.status not in ['pending', 'error']:
            return Response({
                "error": "Match can only be run from pending or error state"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Dispatch Celery task to run the match
        run_chess_match.delay(str(match.id))
        
        return Response({"message": "Match execution started"})

@login_required
def confirm_remove_student(request, student_id):
    """Confirmation page before removing a student"""
    if request.user.role != 'teacher' or not request.user.is_staff:
        return redirect('home')
    
    try:
        student = CustomUser.objects.get(id=student_id, role='student')
    except CustomUser.DoesNotExist:
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        # Actually delete the student
        student.delete()
        return redirect('teacher_dashboard')
    
    return render(request, 'users/confirm_remove_student.html', {
        'student': student
    })
