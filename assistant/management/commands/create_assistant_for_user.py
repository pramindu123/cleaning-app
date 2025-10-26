from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create an Assistant profile for a given username'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, help='Username to create assistant for')

    def handle(self, *args, **options):
        username = options['username']
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"User '{username}' does not exist."))
            return

        # Import here to avoid app-loading issues
        from assistant.models import Assistant

        assistant, created = Assistant.objects.get_or_create(user=user)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Assistant profile created for user '{username}'."))
        else:
            self.stdout.write(self.style.WARNING(f"Assistant profile already exists for user '{username}'."))
