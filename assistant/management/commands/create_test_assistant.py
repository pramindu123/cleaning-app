from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from assistant.models import Assistant

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a test assistant user'

    def handle(self, *args, **options):
        # Create or get user
        user, created = User.objects.get_or_create(
            username='assistant1',
            defaults={
                'email': 'assistant@test.com',
                'first_name': 'Test',
                'last_name': 'Assistant',
                'role': 'ASSISTANT'
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(f'Created user: {user.username}')
        
        # Create or get assistant
        assistant, created = Assistant.objects.get_or_create(
            user=user,
            defaults={'is_active': True}
        )
        
        if created:
            self.stdout.write(f'Created assistant: {assistant}')
        else:
            self.stdout.write(f'Assistant already exists: {assistant}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Assistant user ready!\n'
                f'Username: assistant1\n'
                f'Password: password123'
            )
        )