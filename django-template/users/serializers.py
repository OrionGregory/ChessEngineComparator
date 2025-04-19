from rest_framework import serializers
from .models import ChessBot, CustomUser, Tournament, TournamentParticipant, Match, ClassGroup
from .utils import validate_file_size, validate_file_extension

class ChessBotSerializer(serializers.ModelSerializer):
    owner_email = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ChessBot
        fields = [
            'id', 'name', 'description', 'file_path', 'created_at', 
            'updated_at', 'visibility', 'status', 'version',
            'owner_email', 'file_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner_email', 'file_name']
    
    def get_owner_email(self, obj):
        return obj.owner.email
    
    def get_file_name(self, obj):
        return obj.get_file_name()
        
class ChessBotUploadSerializer(serializers.ModelSerializer):
    file_path = serializers.FileField(
        validators=[validate_file_size, validate_file_extension]
    )
    
    class Meta:
        model = ChessBot
        fields = ['name', 'description', 'file_path', 'visibility']
    
    def create(self, validated_data):
        # Add owner (current user) from context
        validated_data['owner'] = self.context['request'].user
        
        # Create new bot
        return ChessBot.objects.create(**validated_data)

class StudentSerializer(serializers.ModelSerializer):
    bot_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'role', 'date_joined', 'bot_count']
        read_only_fields = ['id', 'date_joined', 'bot_count']
    
    def get_bot_count(self, obj):
        return obj.chess_bots.count()

class StudentDetailSerializer(serializers.ModelSerializer):
    bots = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'role', 'date_joined', 'bots']
        read_only_fields = ['id', 'date_joined', 'bots']
    
    def get_bots(self, obj):
        return ChessBotSerializer(obj.chess_bots.all(), many=True).data

class ClassGroupSerializer(serializers.ModelSerializer):
    teacher_email = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassGroup
        fields = ['id', 'name', 'description', 'teacher', 'teacher_email', 'student_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'teacher_email', 'student_count']
    
    def get_teacher_email(self, obj):
        return obj.teacher.email
    
    def get_student_count(self, obj):
        return obj.students.count()

class ClassGroupDetailSerializer(serializers.ModelSerializer):
    teacher_email = serializers.SerializerMethodField()
    students = StudentSerializer(many=True, read_only=True)
    
    class Meta:
        model = ClassGroup
        fields = ['id', 'name', 'description', 'teacher', 'teacher_email', 'students', 'created_at']
        read_only_fields = ['id', 'created_at', 'teacher_email']
    
    def get_teacher_email(self, obj):
        return obj.teacher.email

class TournamentSerializer(serializers.ModelSerializer):
    created_by_email = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()
    match_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tournament
        fields = ['id', 'name', 'description', 'created_by', 'created_by_email',
                 'created_at', 'scheduled_at', 'completed_at', 'status', 
                 'participant_count', 'match_count']
        read_only_fields = ['id', 'created_at', 'completed_at', 'created_by_email',
                          'participant_count', 'match_count']
    
    def get_created_by_email(self, obj):
        return obj.created_by.email
    
    def get_participant_count(self, obj):
        return obj.participants.count()
    
    def get_match_count(self, obj):
        return obj.matches.count()

class TournamentDetailSerializer(serializers.ModelSerializer):
    created_by_email = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()
    matches = serializers.SerializerMethodField()
    
    class Meta:
        model = Tournament
        fields = ['id', 'name', 'description', 'created_by', 'created_by_email',
                 'created_at', 'scheduled_at', 'completed_at', 'status',
                 'participants', 'matches']
        read_only_fields = ['id', 'created_at', 'completed_at', 'created_by_email']
    
    def get_created_by_email(self, obj):
        return obj.created_by.email
    
    def get_participants(self, obj):
        participants = TournamentParticipant.objects.filter(tournament=obj).order_by('-score')
        return [{
            'bot_id': p.bot.id,
            'bot_name': p.bot.name,
            'owner_email': p.bot.owner.email,
            'score': p.score,
            'rank': p.rank
        } for p in participants]
    
    def get_matches(self, obj):
        return MatchSerializer(obj.matches.all(), many=True).data

class MatchSerializer(serializers.ModelSerializer):
    white_bot_name = serializers.SerializerMethodField()
    black_bot_name = serializers.SerializerMethodField()
    white_bot_owner = serializers.SerializerMethodField()
    black_bot_owner = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = ['id', 'tournament', 'white_bot', 'white_bot_name', 'white_bot_owner',
                 'black_bot', 'black_bot_name', 'black_bot_owner', 'created_at', 
                 'started_at', 'completed_at', 'status', 'result', 
                 'pgn_file', 'log_file']
        read_only_fields = ['id', 'created_at', 'started_at', 'completed_at', 
                          'white_bot_name', 'black_bot_name', 
                          'white_bot_owner', 'black_bot_owner']
    
    def get_white_bot_name(self, obj):
        return obj.white_bot.name
    
    def get_black_bot_name(self, obj):
        return obj.black_bot.name
    
    def get_white_bot_owner(self, obj):
        return obj.white_bot.owner.email
    
    def get_black_bot_owner(self, obj):
        return obj.black_bot.owner.email