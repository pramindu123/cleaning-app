"""
Management command to load USJ faculties into the database
"""
from django.core.management.base import BaseCommand
from cleaning.models import Faculty


class Command(BaseCommand):
    help = 'Load USJ faculties into the database'

    def handle(self, *args, **options):
        faculties = [
            "Humanities and Social Sciences",
            "Applied Sciences",
            "Management Studies and Commerce",
            "Medical Sciences",
            "Graduate Studies",
            "Technology",
            "Engineering",
            "Allied Health Sciences",
            "Dental Sciences",
            "Urban and Aquatic Bioresources",
            "Computing",
        ]

        created_count = 0
        existing_count = 0

        for faculty_name in faculties:
            faculty, created = Faculty.objects.get_or_create(
                faculty_name=faculty_name
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created faculty: {faculty_name}')
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f'- Already exists: {faculty_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: {created_count} faculties created, {existing_count} already existed'
            )
        )
