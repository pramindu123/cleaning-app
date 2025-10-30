from accounts.models import User
from cleaning.models import Faculty
from dean_office.views import _faculties_for_user
from django.test import RequestFactory
from django.apps import apps

# Simulate the dean request
dean = User.objects.filter(role='DEAN_OFFICE').first()
print(f"Dean user: {dean.username}")
print(f"Dean faculty attribute: {dean.faculty}")
print(f"Dean role: {dean.role}")
print(f"Dean is_staff: {dean.is_staff}")
print(f"Dean is_superuser: {dean.is_superuser}")

# Create a mock request with month parameter
factory = RequestFactory()
request = factory.get('/dean/?month=2025-10')
request.user = dean

# Simulate what the view does
Faculty = apps.get_model('cleaning', 'Faculty')
print(f"\nFaculty model: {Faculty}")

faculties, selected_faculty = _faculties_for_user(Faculty, request.user, request)
print(f"\nAfter _faculties_for_user:")
print(f"  faculties: {faculties}")
print(f"  selected_faculty: {selected_faculty}")

# Check if there's a faculty GET parameter
if request.GET.get('faculty') or request.GET.get('faculty_id'):
    print(f"\nFaculty GET parameter found: {request.GET.get('faculty') or request.GET.get('faculty_id')}")
else:
    print(f"\nNo faculty GET parameter - selected_faculty should remain: {selected_faculty}")

# Check the actual faculty object
if selected_faculty:
    print(f"\nSelected faculty details:")
    print(f"  ID: {selected_faculty.id}")
    print(f"  Name: {selected_faculty.faculty_name}")
    print(f"  Is in faculties list: {selected_faculty in faculties}")
