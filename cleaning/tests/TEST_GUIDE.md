# Testing Guide for Cleaning App

This document explains how to run and write tests for the cleaning app's API endpoints and views.

## Test Structure

```
cleaning/tests/
├── __init__.py           # Package initialization
├── fixtures.py           # Test data factories and base classes
├── test_api.py          # API endpoint tests (AJAX/JSON endpoints)
├── test_views.py        # View tests (HTML endpoints)
└── TEST_GUIDE.md        # This file
```

## Running Tests

### Run all tests in the project
```bash
python manage.py test
```

### Run only cleaning app tests
```bash
python manage.py test cleaning
```

### Run specific test file
```bash
python manage.py test cleaning.tests.test_api
python manage.py test cleaning.tests.test_views
```

### Run specific test class
```bash
python manage.py test cleaning.tests.test_api.GetActivitiesByUnitAPITest
```

### Run specific test method
```bash
python manage.py test cleaning.tests.test_api.GetActivitiesByUnitAPITest.test_get_activities_success
```

### Run with verbose output
```bash
python manage.py test --verbosity=2
```

### Keep test database for inspection
```bash
python manage.py test --keepdb
```

## What's Tested

### API Endpoints (`test_api.py`)

1. **get_activities_by_unit** - Retrieve activities for a unit
   - ✓ Success case with multiple activities
   - ✓ Only returns active activities
   - ✓ Requires authentication
   - ✓ Returns correct JSON structure

2. **mark_activity_completed_day** - Mark a day as completed
   - ✓ Success case with COMPLETED status
   - ✓ Sets completed_date to marking time
   - ✓ Handles twice daily activities (2 marks per day)
   - ✓ Enforces monthly frequency limits
   - ✓ Requires manager role (403 for assistants)
   - ✓ Validates date format
   - ✓ Only accepts POST requests (405 for GET)

3. **Integration Tests**
   - ✓ Full workflow: create activity → get activities → mark completed → verify

### View Tests (`test_views.py`)

1. **CleaningRecordListView**
   - ✓ Requires authentication
   - ✓ Accessible by managers
   - ✓ Displays cleaning records
   - ✓ Filtering by status works

2. **CleaningRecordCreateView**
   - ✓ Requires authentication
   - ✓ Creates single day records as PENDING
   - ✓ Creates calendar-marked records as COMPLETED

3. **CleaningRecordCompleteView**
   - ✓ Marks pending records as completed
   - ✓ Sets completed_date
   - ✓ Handles already-completed records

4. **ActivityCalendarView**
   - ✓ Requires authentication
   - ✓ Shows completed days

5. **Role Permissions**
   - ✓ Assistants cannot create activities
   - ✓ Managers can create activities
   - ✓ Dean office can view reports

6. **Frequency Limits**
   - ✓ Daily: 1 per day
   - ✓ Twice daily: 2 per day
   - ✓ Weekly: 1 per week
   - ✓ Monthly: 1 per month

## Test Data Factory

The `fixtures.py` module provides a `TestDataFactory` class for creating test data:

```python
from cleaning.tests.fixtures import TestDataFactory

# Create users
manager = TestDataFactory.create_manager()
assistant = TestDataFactory.create_assistant()
dean = TestDataFactory.create_dean_office()

# Create hierarchy
zone = TestDataFactory.create_zone()
faculty = TestDataFactory.create_faculty(zone=zone)
unit = TestDataFactory.create_unit(zone=zone, faculty=faculty)

# Create activity
activity = TestDataFactory.create_activity(unit=unit, frequency='DAILY')

# Create cleaning record
record = TestDataFactory.create_cleaning_record(
    activity=activity,
    status='COMPLETED',
    assigned_to=assistant
)

# Create complete hierarchy in one call
hierarchy = TestDataFactory.create_complete_hierarchy()
# Returns: {'zone', 'faculty', 'manager', 'assistant', 'unit', 'activity', 'record'}
```

## Base Test Classes

Use `BaseTestCase` mixin for common setup:

```python
from django.test import TestCase
from cleaning.tests.fixtures import BaseTestCase

class MyTest(BaseTestCase, TestCase):
    def setUp(self):
        # Create standard users
        self.create_test_users()  # Creates manager, assistant, dean
        
        # Create standard hierarchy
        self.create_test_hierarchy()  # Creates zone, faculty, unit
        
        # Login helpers
        self.login_as_manager()
        # or self.login_as_assistant()
        # or self.login_as_dean()
```

## Writing New Tests

### 1. Test API Endpoints

```python
from django.test import TestCase, Client
from django.urls import reverse
from cleaning.tests.fixtures import TestDataFactory

class MyAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = TestDataFactory.create_manager()
        
    def test_my_endpoint(self):
        self.client.login(username='manager', password='testpass123')
        url = reverse('cleaning:my_endpoint')
        response = self.client.post(url, {'data': 'value'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
```

### 2. Test Views

```python
from django.test import TestCase
from cleaning.tests.fixtures import BaseTestCase

class MyViewTest(BaseTestCase, TestCase):
    def setUp(self):
        self.create_test_users()
        self.create_test_hierarchy()
        
    def test_my_view(self):
        self.login_as_manager()
        url = reverse('cleaning:my_view')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cleaning/my_template.html')
        self.assertContains(response, 'Expected Text')
```

### 3. Test Permissions

```python
def test_requires_manager_role(self):
    # Try as assistant (should fail)
    self.login_as_assistant()
    response = self.client.post(url, data)
    self.assertEqual(response.status_code, 403)
    
    # Try as manager (should succeed)
    self.login_as_manager()
    response = self.client.post(url, data)
    self.assertEqual(response.status_code, 200)
```

## Coverage Reports

### Install coverage tool
```bash
pip install coverage
```

### Run tests with coverage
```bash
coverage run --source='.' manage.py test cleaning
coverage report
coverage html
```

### View HTML coverage report
Open `htmlcov/index.html` in browser

## Best Practices

1. **Use descriptive test names**: `test_mark_day_requires_manager` not `test_1`
2. **One assertion per test** (when possible): Makes failures easier to debug
3. **Use factories**: Don't repeat object creation code
4. **Test error cases**: Don't just test happy paths
5. **Test permissions**: Verify role-based access control
6. **Test edge cases**: Empty data, invalid formats, boundary conditions
7. **Keep tests independent**: Each test should be runnable alone
8. **Use setUp/tearDown**: For common initialization/cleanup

## Common Assertions

```python
# Status codes
self.assertEqual(response.status_code, 200)
self.assertEqual(response.status_code, 302)  # Redirect
self.assertEqual(response.status_code, 403)  # Forbidden
self.assertEqual(response.status_code, 404)  # Not found

# Templates
self.assertTemplateUsed(response, 'cleaning/list.html')

# Content
self.assertContains(response, 'Expected Text')
self.assertNotContains(response, 'Unexpected Text')

# JSON
data = response.json()
self.assertTrue(data['ok'])
self.assertIn('key', data)

# Database
self.assertEqual(Model.objects.count(), 1)
self.assertTrue(Model.objects.filter(name='test').exists())

# Context
self.assertIn('records', response.context)
self.assertEqual(len(response.context['records']), 5)
```

## Debugging Failed Tests

### 1. Use verbose output
```bash
python manage.py test --verbosity=2
```

### 2. Print debug info in tests
```python
def test_something(self):
    response = self.client.get(url)
    print(response.content)  # See actual HTML
    print(response.json())   # See JSON response
    print(response.context)  # See template context
```

### 3. Use pdb debugger
```python
def test_something(self):
    import pdb; pdb.set_trace()
    response = self.client.get(url)
```

### 4. Keep database
```bash
python manage.py test --keepdb
# Then inspect with: python manage.py dbshell
```

## CI/CD Integration

Add to your CI pipeline (e.g., GitHub Actions):

```yaml
- name: Run tests
  run: |
    python manage.py test
    
- name: Generate coverage
  run: |
    coverage run --source='.' manage.py test
    coverage report --fail-under=80
```

## Next Steps

1. **Add more test cases**: Cover remaining views and edge cases
2. **Add integration tests**: Test full user workflows
3. **Add performance tests**: Test with large datasets
4. **Add frontend tests**: Test JavaScript/AJAX interactions
5. **Set up CI/CD**: Automate testing on every commit

## Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Django TestCase API](https://docs.djangoproject.com/en/stable/topics/testing/tools/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
