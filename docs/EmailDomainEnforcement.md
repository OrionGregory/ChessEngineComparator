# Enforcing Email Domain Restrictions for Registration and Login

This guide explains how to enforce email domain restrictions for registration and login on the Chess Engine Comparator platform. This ensures that only users with specific email domains (e.g., school or university domains) can access the platform.

---

## Step 1: Update the Allowed Email Domains in `settings.py`

1. Open the `settings.py` file in your project.
2. Add or update the following settings to define the allowed email domains and specific email addresses:

   ```python
   # Allowed email domains for teachers or students
   TEACHER_EMAIL_DOMAINS = ['school.edu', 'university.edu']  # Replace with your domains
   TEACHER_EMAILS = ['specific.teacher@example.com']  # Optional: Add specific email addresses

## Step 2: Modify the CustomSocialAccountAdapter
The CustomSocialAccountAdapter class is responsible for handling custom logic during social account authentication. Follow these steps to enforce email domain restrictions:

Open the file ChessApp/users/adapters.py.

Locate the CustomSocialAccountAdapter class.

Ensure the populate_user method includes logic to assign roles based on email domains or specific emails. The method should look like this:
```py
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
```

Add a restriction to prevent users with unapproved email domains from signing up. Update the is_open_for_signup method as follows:
```py
def is_open_for_signup(self, request, sociallogin):
    """Restrict signup to specific email domains"""
    email = sociallogin.account.extra_data.get('email', '')
    domain = email.split('@')[-1]
    
    if domain not in getattr(settings, 'TEACHER_EMAIL_DOMAINS', []):
        return False  # Deny signup for unapproved domains
    return True
```

## Step 3: Test the Implementation
Attempt to sign up or log in with an email address outside the allowed domains. The system should deny access.
Verify that users with approved email domains or specific email addresses can successfully register and log in.
## Step 4: Deploy the Changes
Save all changes to the settings.py and adapters.py files.
Restart your Django application to apply the updates.