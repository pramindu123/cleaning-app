from accounts.models import User
from cleaning.models import Faculty
from dean_office.views import _faculties_for_user
from django.test import RequestFactory

dean = User.objects.filter(role='DEAN_OFFICE').first()
print(f"Dean: {dean.username}, Faculty: {dean.faculty}")

factory = RequestFactory()
request = factory.get('/dean/')
request.user = dean

faculties, selected_faculty = _faculties_for_user(Faculty, dean, request)
print(f"\nResult from _faculties_for_user:")
print(f"  faculties: {faculties}")
print(f"  selected_faculty: {selected_faculty}")
