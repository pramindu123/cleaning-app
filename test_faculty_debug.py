from cleaning.models import Faculty

faculties = list(Faculty.objects.all())
print(f"Number of faculties: {len(faculties)}")
for f in faculties:
    print(f"  ID: {f.id}, Name: {f.faculty_name}")

# Test _build_faculty_options
from dean_office.views import _build_faculty_options
options = _build_faculty_options(None, faculties)
print(f"\nNumber of options: {len(options)}")
for opt in options:
    print(f"  Value: {opt['value']}, Label: {opt['label']}")
