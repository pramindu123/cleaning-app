from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from assistant.models import Assistant

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup ishadi as assistant'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='ishadi')
            user.set_password('123')
            user.save()
            
            assistant, created = Assistant.objects.get_or_create(
                user=user,
                defaults={'is_active': True}
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Setup complete!\n'
                    f'Username: ishadi\n'
                    f'Password: 123'
                )
            )
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User ishadi not found'))