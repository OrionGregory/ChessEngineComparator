from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from allauth.socialaccount.models import SocialApp

class NoSignupAccountAdapter(DefaultAccountAdapter):
    """Disable regular username/password registration"""
    def is_open_for_signup(self, request):
        """No regular signup allowed, only social"""
        return False

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter for social account auth with role assignment"""
    def is_open_for_signup(self, request, sociallogin):
        return True
        
    def populate_user(self, request, sociallogin, data):
        """Add custom fields to user when creating via social auth"""
        user = super().populate_user(request, sociallogin, data)
        
        # Assign role based on email domain or specific email
        email = user.email
        domain = email.split('@')[-1]
        
        if domain in getattr(settings, 'TEACHER_EMAIL_DOMAINS', []) or \
           email in getattr(settings, 'TEACHER_EMAILS', []):
            user.role = 'teacher'
        else:
            user.role = 'student'
            
        return user
        
    def get_app(self, request, provider, client_id=None):
        """Get the SocialApp for the given provider"""
        # If provider is a string, use it as-is
        if isinstance(provider, str):
            app = SocialApp.objects.filter(provider=provider).first()
        else:
            # Otherwise use the provider ID
            app = SocialApp.objects.filter(provider=provider.id).first()
            
        if app is None:
            raise SocialApp.DoesNotExist("No social app configured for provider %s" % provider)
        return app