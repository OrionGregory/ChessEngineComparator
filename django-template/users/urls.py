from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for API endpoints
router = DefaultRouter()
router.register(r'bots', views.ChessBotViewSet, basename='chessbot')
router.register(r'students', views.StudentViewSet, basename='student')
router.register(r'classes', views.ClassGroupViewSet, basename='class')
router.register(r'tournaments', views.TournamentViewSet, basename='tournament')
router.register(r'matches', views.MatchViewSet, basename='match')

urlpatterns = [
    # Authentication paths
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('api/token/', views.TokenObtainView.as_view(), name='token_obtain'),
    
    # Dashboard paths
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    
    # Student paths
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('student/<int:student_id>/remove/', views.confirm_remove_student, name='confirm_remove_student'),
    
    # Class and tournament paths
    path('class/<uuid:class_id>/', views.class_detail, name='class_detail'),
    path('tournament/<uuid:tournament_id>/', views.tournament_detail, name='tournament_detail'),
    
    # API endpoints for tournaments
    path('api/tournaments/<int:id>/join/', views.join_tournament, name='join-tournament'),
    
    # Include DRF router URLs
    path('api/', include(router.urls)),
    path('', include(router.urls)),
]