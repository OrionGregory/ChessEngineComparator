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
    # Existing paths
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('api/token/', views.TokenObtainView.as_view(), name='token_obtain'),
    
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    
    # Changed from <uuid:student_id> to <int:student_id>
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    
    # Keep other paths as they are
    path('class/<uuid:class_id>/', views.class_detail, name='class_detail'),
    path('tournament/<uuid:tournament_id>/', views.tournament_detail, name='tournament_detail'),
    
    path('api/', include(router.urls)),
]