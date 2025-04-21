"""
URL configuration for web_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static
from users.views import user_info, home, google_login, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    
    # Authentication endpoints
    path('auth/direct-google-login/', google_login, name='google-login'),
    path('api/logout/', logout_view, name='logout'),
    
    # API endpoints
    path('api/user-info/', user_info, name='user-info'),
    
    # Include app URLs
    path('', include('hello.urls')),
    
    # Default route
    path('', home, name='home'),
    
    # Catch-all route for SPA (optional, only if you're using React Router)
    re_path(r'^(?!api/|admin/|static/|media/|users/|accounts/|auth/).*$', 
            TemplateView.as_view(template_name='index.html'), name='frontend'),
]

urlpatterns += staticfiles_urlpatterns()

# Add this to serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)