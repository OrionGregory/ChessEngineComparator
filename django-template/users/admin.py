from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ChessBot, Tournament, TournamentParticipant, Match, ClassGroup

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'role', 'is_staff', 'created_at']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'created_at')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(ChessBot)
class ChessBotAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'visibility', 'created_at')
    list_filter = ('status', 'visibility')
    search_fields = ('name', 'owner__email')

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'created_by__email')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('white_bot', 'black_bot', 'result', 'status', 'created_at')
    list_filter = ('status', 'result')
    search_fields = ('white_bot__name', 'black_bot__name')

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'created_at')
    search_fields = ('name', 'teacher__email')
