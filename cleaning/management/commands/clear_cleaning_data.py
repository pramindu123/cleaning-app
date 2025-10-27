"""
Management command to clear all cleaning records and activities.
Safety: requires --yes flag to proceed.
Optional: --records-only, --activities-only
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from cleaning.models import CleaningRecord, CleaningActivity


class Command(BaseCommand):
    help = 'Clear cleaning data: records and activities. USE WITH CAUTION.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes', '-y', action='store_true', dest='confirm',
            help='Confirm destructive operation without interactive prompt.'
        )
        parser.add_argument(
            '--records-only', action='store_true', dest='records_only',
            help='Delete only CleaningRecord entries.'
        )
        parser.add_argument(
            '--activities-only', action='store_true', dest='activities_only',
            help='Delete only CleaningActivity entries.'
        )

    def handle(self, *args, **options):
        confirm = options.get('confirm')
        records_only = options.get('records_only')
        activities_only = options.get('activities_only')

        if not confirm:
            raise CommandError('Destructive operation aborted. Re-run with --yes to proceed.')

        # Determine targets
        if records_only and activities_only:
            raise CommandError('Choose only one of --records-only or --activities-only, or no flag for both.')

        delete_records = True
        delete_activities = True
        if records_only:
            delete_activities = False
        if activities_only:
            delete_records = False

        with transaction.atomic():
            total_deleted = 0

            if delete_records:
                rc = CleaningRecord.objects.count()
                deleted_info = CleaningRecord.objects.all().delete()
                total_deleted += rc
                self.stdout.write(self.style.SUCCESS(f'Deleted {rc} CleaningRecord(s).'))

            if delete_activities:
                ac = CleaningActivity.objects.count()
                # Deleting activities after records avoids FK issues, though activity FK is SET_NULL
                deleted_info = CleaningActivity.objects.all().delete()
                total_deleted += ac
                self.stdout.write(self.style.SUCCESS(f'Deleted {ac} CleaningActivity/ies.'))

        if total_deleted == 0:
            self.stdout.write(self.style.WARNING('No cleaning data to delete.'))
        else:
            self.stdout.write(self.style.SUCCESS('Cleaning data purge completed.'))
