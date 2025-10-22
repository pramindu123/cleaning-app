from django.core.management.base import BaseCommand
from cleaning.models import Zone, Section, Faculty, Unit


class Command(BaseCommand):
    help = 'Load sample data for the cleaning app (zones, sections, faculties, and units)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading sample data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('🗑️  Clearing existing data...'))
            Unit.objects.all().delete()
            Section.objects.all().delete()
            Zone.objects.all().delete()
            Faculty.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Data cleared'))

        self.stdout.write(self.style.HTTP_INFO('🧹 Loading Sample Data for USJ Cleaning App'))
        self.stdout.write('=' * 60)

        # Create Zones
        self.stdout.write('\n📍 Creating Zones...')
        main_campus, _ = Zone.objects.get_or_create(
            code="MC",
            defaults={
                'name': "Main Campus",
                'description': "The main university campus with administrative and academic buildings"
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ {main_campus}'))

        medical_campus, _ = Zone.objects.get_or_create(
            code="MED",
            defaults={
                'name': "Medical Campus",
                'description': "Campus dedicated to medical and health sciences"
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ {medical_campus}'))

        engineering_campus, _ = Zone.objects.get_or_create(
            code="ENG",
            defaults={
                'name': "Engineering Campus",
                'description': "Campus with engineering facilities and labs"
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ {engineering_campus}'))

        # Create Faculties
        self.stdout.write('\n🎓 Creating Faculties...')
        fos, _ = Faculty.objects.get_or_create(
            code="FOS",
            defaults={
                'name': "Faculty of Science",
                'short_name': "FOS",
                'description': "Natural and applied sciences"
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ {fos}'))

        foa, _ = Faculty.objects.get_or_create(
            code="FOA",
            defaults={
                'name': "Faculty of Arts",
                'short_name': "FOA",
                'description': "Humanities and social sciences"
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ {foa}'))

        foe, _ = Faculty.objects.get_or_create(
            code="FOE",
            defaults={
                'name': "Faculty of Engineering",
                'short_name': "FOE",
                'description': "Engineering and technology"
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ {foe}'))

        fomed, _ = Faculty.objects.get_or_create(
            code="FOMED",
            defaults={
                'name': "Faculty of Medicine",
                'short_name': "FOMED",
                'description': "Medical and health sciences"
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ {fomed}'))

        # Create Sections
        self.stdout.write('\n🏢 Creating Sections...')
        science_building, _ = Section.objects.get_or_create(
            code="SB-01",
            defaults={
                'zone': main_campus,
                'name': "Science Building",
                'floor_count': 5,
                'description': "Main building for science lectures and labs"
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ {science_building}'))

        library_block, _ = Section.objects.get_or_create(
            code="LB-01",
            defaults={
                'zone': main_campus,
                'name': "Library Block",
                'floor_count': 4,
                'description': "Central library and study areas"
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ {library_block}'))

        canteen_area, _ = Section.objects.get_or_create(
            code="CA-01",
            defaults={
                'zone': main_campus,
                'name': "Canteen Area",
                'floor_count': 2,
                'description': "Student dining and cafeteria"
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ {canteen_area}'))

        medical_building, _ = Section.objects.get_or_create(
            code="MBA-01",
            defaults={
                'zone': medical_campus,
                'name': "Medical Building A",
                'floor_count': 6,
                'description': "Primary medical education building"
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ {medical_building}'))

        engineering_lab, _ = Section.objects.get_or_create(
            code="ELC-01",
            defaults={
                'zone': engineering_campus,
                'name': "Engineering Lab Complex",
                'floor_count': 3,
                'description': "Engineering laboratories and workshops"
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ {engineering_lab}'))

        # Create Units
        self.stdout.write('\n📦 Creating Units...')
        units_data = [
            # Science Building Units
            {
                'section': science_building,
                'faculty': fos,
                'name': 'Lecture Hall 1',
                'code': 'SB-01-LH-001',
                'unit_type': 'LECTURE_HALL',
                'floor_number': 1,
                'area_sqm': 150.50,
                'capacity': 200,
                'description': 'Large lecture hall with multimedia facilities',
                'is_active': True
            },
            {
                'section': science_building,
                'faculty': fos,
                'name': 'Chemistry Lab A',
                'code': 'SB-01-CL-002',
                'unit_type': 'LABORATORY',
                'floor_number': 2,
                'area_sqm': 120.00,
                'capacity': 40,
                'description': 'Organic chemistry laboratory',
                'notes': 'Requires special chemical waste disposal',
                'is_active': True
            },
            {
                'section': science_building,
                'faculty': fos,
                'name': 'Physics Lab B',
                'code': 'SB-01-PL-003',
                'unit_type': 'LABORATORY',
                'floor_number': 3,
                'area_sqm': 110.00,
                'capacity': 35,
                'description': 'General physics laboratory',
                'is_active': True
            },
            {
                'section': science_building,
                'faculty': fos,
                'name': 'Staff Office',
                'code': 'SB-01-OF-004',
                'unit_type': 'OFFICE',
                'floor_number': 4,
                'area_sqm': 45.00,
                'capacity': 8,
                'description': 'Faculty staff office',
                'is_active': True
            },
            {
                'section': science_building,
                'faculty': fos,
                'name': 'Restroom 1',
                'code': 'SB-01-RR-005',
                'unit_type': 'RESTROOM',
                'floor_number': 1,
                'area_sqm': 25.00,
                'description': 'Ground floor restroom',
                'notes': 'Requires hourly checks during peak hours',
                'is_active': True
            },
            # Library Block Units
            {
                'section': library_block,
                'faculty': foa,
                'name': 'Reading Room 1',
                'code': 'LB-01-RR-001',
                'unit_type': 'LIBRARY',
                'floor_number': 1,
                'area_sqm': 200.00,
                'capacity': 100,
                'description': 'Silent reading area',
                'notes': 'Quiet cleaning required during operational hours',
                'is_active': True
            },
            {
                'section': library_block,
                'faculty': foa,
                'name': 'Group Study Room',
                'code': 'LB-01-GS-002',
                'unit_type': 'COMMON_AREA',
                'floor_number': 2,
                'area_sqm': 80.00,
                'capacity': 30,
                'description': 'Collaborative study space',
                'is_active': True
            },
            # Canteen Area Units
            {
                'section': canteen_area,
                'faculty': foa,
                'name': 'Main Dining Hall',
                'code': 'CA-01-DH-001',
                'unit_type': 'CAFETERIA',
                'floor_number': 1,
                'area_sqm': 300.00,
                'capacity': 300,
                'description': 'Main student cafeteria',
                'notes': 'Requires deep cleaning after each meal period',
                'is_active': True
            },
            # Medical Building Units
            {
                'section': medical_building,
                'faculty': fomed,
                'name': 'Anatomy Lab',
                'code': 'MBA-01-AL-001',
                'unit_type': 'LABORATORY',
                'floor_number': 2,
                'area_sqm': 140.00,
                'capacity': 45,
                'description': 'Human anatomy laboratory',
                'notes': 'Special sterilization protocols required',
                'is_active': True
            },
            {
                'section': medical_building,
                'faculty': fomed,
                'name': 'Lecture Theatre 1',
                'code': 'MBA-01-LT-002',
                'unit_type': 'AUDITORIUM',
                'floor_number': 1,
                'area_sqm': 180.00,
                'capacity': 250,
                'description': 'Large medical lecture theatre',
                'is_active': True
            },
            # Engineering Lab Units
            {
                'section': engineering_lab,
                'faculty': foe,
                'name': 'Computer Lab 1',
                'code': 'ELC-01-CL-001',
                'unit_type': 'LABORATORY',
                'floor_number': 1,
                'area_sqm': 100.00,
                'capacity': 50,
                'description': 'Computer programming lab',
                'notes': 'Electronics - careful dusting required',
                'is_active': True
            },
            {
                'section': engineering_lab,
                'faculty': foe,
                'name': 'Workshop Area',
                'code': 'ELC-01-WS-002',
                'unit_type': 'LABORATORY',
                'floor_number': 2,
                'area_sqm': 160.00,
                'capacity': 30,
                'description': 'Mechanical engineering workshop',
                'notes': 'Heavy machinery - requires special equipment',
                'is_active': True
            },
            {
                'section': engineering_lab,
                'faculty': foe,
                'name': 'Storage Room',
                'code': 'ELC-01-ST-003',
                'unit_type': 'STORAGE',
                'floor_number': 3,
                'area_sqm': 50.00,
                'description': 'Equipment storage',
                'is_active': False,
                'notes': 'Currently under renovation'
            },
        ]

        for unit_data in units_data:
            unit, created = Unit.objects.get_or_create(
                code=unit_data['code'],
                defaults=unit_data
            )
            status_icon = "✓" if unit.is_active else "⚠"
            action = "Created" if created else "Already exists"
            self.stdout.write(self.style.SUCCESS(f'{status_icon} {action}: {unit}'))

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✅ Sample data loading completed!'))
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'  - Zones: {Zone.objects.count()}')
        self.stdout.write(f'  - Sections: {Section.objects.count()}')
        self.stdout.write(f'  - Faculties: {Faculty.objects.count()}')
        self.stdout.write(f'  - Units: {Unit.objects.count()} ({Unit.objects.filter(is_active=True).count()} active)')
        self.stdout.write(self.style.HTTP_INFO('\n🎯 You can now view this data in the Django admin panel!'))
