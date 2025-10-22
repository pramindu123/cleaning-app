"""
Sample data population script for the cleaning app.
Run this with: python manage.py shell < cleaning/sample_data.py
"""

from cleaning.models import Zone, Section, Faculty, Unit

print("🧹 Creating Sample Data for USJ Cleaning App")
print("=" * 60)

# Create Zones
print("\n📍 Creating Zones...")
main_campus = Zone.objects.create(
    name="Main Campus",
    code="MC",
    description="The main university campus with administrative and academic buildings"
)
print(f"✓ Created: {main_campus}")

medical_campus = Zone.objects.create(
    name="Medical Campus",
    code="MED",
    description="Campus dedicated to medical and health sciences"
)
print(f"✓ Created: {medical_campus}")

engineering_campus = Zone.objects.create(
    name="Engineering Campus",
    code="ENG",
    description="Campus with engineering facilities and labs"
)
print(f"✓ Created: {engineering_campus}")

# Create Faculties
print("\n🎓 Creating Faculties...")
fos = Faculty.objects.create(
    name="Faculty of Science",
    short_name="FOS",
    code="FOS",
    description="Natural and applied sciences"
)
print(f"✓ Created: {fos}")

foa = Faculty.objects.create(
    name="Faculty of Arts",
    short_name="FOA",
    code="FOA",
    description="Humanities and social sciences"
)
print(f"✓ Created: {foa}")

foe = Faculty.objects.create(
    name="Faculty of Engineering",
    short_name="FOE",
    code="FOE",
    description="Engineering and technology"
)
print(f"✓ Created: {foe}")

fomed = Faculty.objects.create(
    name="Faculty of Medicine",
    short_name="FOMED",
    code="FOMED",
    description="Medical and health sciences"
)
print(f"✓ Created: {fomed}")

# Create Sections
print("\n🏢 Creating Sections...")
science_building = Section.objects.create(
    zone=main_campus,
    name="Science Building",
    code="SB-01",
    floor_count=5,
    description="Main building for science lectures and labs"
)
print(f"✓ Created: {science_building}")

library_block = Section.objects.create(
    zone=main_campus,
    name="Library Block",
    code="LB-01",
    floor_count=4,
    description="Central library and study areas"
)
print(f"✓ Created: {library_block}")

canteen_area = Section.objects.create(
    zone=main_campus,
    name="Canteen Area",
    code="CA-01",
    floor_count=2,
    description="Student dining and cafeteria"
)
print(f"✓ Created: {canteen_area}")

medical_building = Section.objects.create(
    zone=medical_campus,
    name="Medical Building A",
    code="MBA-01",
    floor_count=6,
    description="Primary medical education building"
)
print(f"✓ Created: {medical_building}")

engineering_lab = Section.objects.create(
    zone=engineering_campus,
    name="Engineering Lab Complex",
    code="ELC-01",
    floor_count=3,
    description="Engineering laboratories and workshops"
)
print(f"✓ Created: {engineering_lab}")

# Create Units
print("\n📦 Creating Units...")

# Science Building Units
units_data = [
    # Science Building - Floor 1
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
        'faculty': foa,  # General admin
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
        'is_active': False,  # Under renovation
        'notes': 'Currently under renovation'
    },
]

for unit_data in units_data:
    unit = Unit.objects.create(**unit_data)
    status = "✓" if unit.is_active else "⚠"
    print(f"{status} Created: {unit}")

print("\n" + "=" * 60)
print("✅ Sample data creation completed!")
print(f"\nSummary:")
print(f"  - Zones: {Zone.objects.count()}")
print(f"  - Sections: {Section.objects.count()}")
print(f"  - Faculties: {Faculty.objects.count()}")
print(f"  - Units: {Unit.objects.count()} ({Unit.objects.filter(is_active=True).count()} active)")
print("\n🎯 You can now view this data in the Django admin panel!")
