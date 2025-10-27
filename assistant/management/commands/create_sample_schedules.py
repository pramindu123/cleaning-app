from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from assistant.models import Assistant, Schedule
from cleaning.models import Unit
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample schedules for assistant'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='ishadi')
            assistant = user.assistant
            
            # Get some units to assign
            units = Unit.objects.all()[:5]
            
            for i, unit in enumerate(units):
                schedule, created = Schedule.objects.get_or_create(
                    unit=unit,
                    month=date(2024, 1, 1),
                    assigned_assistant=assistant,
                    defaults={
                        'status': 'draft' if i < 3 else 'submitted'
                    }
                )
                
                if created:
                    self.stdout.write(f'Created schedule for {unit.name}')
                else:
                    self.stdout.write(f'Schedule already exists for {unit.name}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Sample schedules created for {assistant}')
            )
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User ishadi not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))