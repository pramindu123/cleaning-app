from django.contrib.auth import get_user_model, login
from django.conf import settings


class AutoLoginMiddleware:
    """Middleware that automatically logs in a development user when DEBUG=True.

    Behavior:
    - Only runs when settings.DEBUG is True (safe for development only).
    - If the request user is not authenticated, it will get or create a user
      with username from settings.AUTO_LOGIN_USERNAME (defaults to 'dev').
    - If the user is newly created, it sets an unusable password and marks
      the account as staff/superuser so admin access is available during dev.
    - Uses django.contrib.auth.login with ModelBackend to attach the user to
      the session.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only auto-login in DEBUG mode and when no user is authenticated.
        if not getattr(settings, 'DEBUG', False):
            return self.get_response(request)

        # Don't auto-login for certain paths (logout, login pages, static assets)
        exempt_paths = getattr(settings, 'AUTO_LOGIN_EXEMPT_PATHS', ['/logout/', '/accounts/logout/'])
        try:
            req_path = request.path
        except Exception:
            req_path = ''

        for p in exempt_paths:
            if req_path.startswith(p):
                return self.get_response(request)

        user_obj = getattr(request, 'user', None)
        if user_obj and user_obj.is_authenticated:
            return self.get_response(request)

        User = get_user_model()
        username = getattr(settings, 'AUTO_LOGIN_USERNAME', 'dev')
        desired_role = getattr(settings, 'AUTO_LOGIN_ROLE', None)

        # Create or get the development user.
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'is_staff': True, 'is_superuser': True},
        )

        # If a desired role is provided, ensure the user has that role.
        if desired_role:
            try:
                # Some custom user models use 'role' attribute
                if getattr(user, 'role', None) != desired_role:
                    setattr(user, 'role', desired_role)
                    user.save()
            except Exception:
                # If role can't be set, ignore silently in dev
                pass

        if created:
            user.set_unusable_password()
            user.save()

        # Ensure we set a backend so login() doesn't complain.
        try:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        except Exception:
            # If something goes wrong (very rare), skip auto-login silently.
            pass

        response = self.get_response(request)
        return response
