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
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner_email', 'file_name', 'file_path']
    
    def get_owner_email(self, obj):
        return obj.owner.email
    
    def get_file_name(self, obj):
        return obj.get_file_name()
        
class ChessBotUploadSerializer(serializers.ModelSerializer):
    file_path = serializers.FileField(
        validators=[validate_file_size, validate_file_extension],
        required=False  # Make it optional for updates
    )
    
    class Meta:
        model = ChessBot
        fields = ['name', 'description', 'file_path', 'visibility', 'status']
    
    def create(self, validated_data):
        # Add owner (current user) from context
        validated_data['owner'] = self.context['request'].user
        
        # Create new bot
        return ChessBot.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        # Update standard fields
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.visibility = validated_data.get('visibility', instance.visibility)
        
        # Status can only be changed by teachers or through specific endpoints (activate/archive)
        if self.context['request'].user.role == 'teacher':
            instance.status = validated_data.get('status', instance.status)
        
        # Only update file_path if provided
        if 'file_path' in validated_data:
            instance.file_path = validated_data.get('file_path')
            instance.version += 1  # Increment version when file changes
            
        instance.save()
        return instance

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
    
    class Meta:
        model = Tournament
        fields = [
            'id', 'name', 'description', 'created_at', 'scheduled_at',
            'completed_at', 'status', 'created_by', 'created_by_email'
        ]
        read_only_fields = ['id', 'created_at', 'created_by', 'created_by_email']
    
    def get_created_by_email(self, obj):
        return obj.created_by.email if obj.created_by else None

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
        # Use select_related to optimize queries
        participants = TournamentParticipant.objects.filter(tournament=obj)\
            .select_related('bot', 'bot__owner')\
            .order_by('-score')
        
        # Debug print to check what's being retrieved
        print(f"Found {participants.count()} participants for tournament {obj.id}")
        
        return [{
            'bot_id': str(p.bot.id),  # Convert UUID to string for serialization
            'bot_name': p.bot.name,
            'owner_email': p.bot.owner.email if p.bot.owner else "Unknown",
            'score': p.score,
            'rank': p.rank
        } for p in participants]
    
    def get_matches(self, obj):
        return MatchSerializer(obj.matches.all(), many=True).data

class MatchSerializer(serializers.ModelSerializer):
    white_bot_name = serializers.SerializerMethodField()
    black_bot_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = [
            'id', 'tournament', 'white_bot', 'white_bot_name',
            'black_bot', 'black_bot_name', 'status', 'result',
            'created_at', 'started_at', 'completed_at', 
            'pgn_file', 'log_file', 'round'  # Added round field
        ]
        read_only_fields = ['id', 'created_at', 'white_bot_name', 'black_bot_name']
    
    def get_white_bot_name(self, obj):
        return obj.white_bot.name
    
    def get_black_bot_name(self, obj):
        return obj.black_bot.name