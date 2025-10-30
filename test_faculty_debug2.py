from cleaning.models import Faculty
from dean_office.views import _build_faculty_options

faculties = list(Faculty.objects.all())
print(f"Faculties: {faculties}")
options = _build_faculty_options(None, faculties)
print(f"Options: {options}")
for opt in options:
    print(f"  Option dict: {opt}")
