"""
Test fixtures and factories for creating test data

This module provides reusable factories for creating test objects
"""
from django.contrib.auth import get_user_model
from cleaning.models import Zone, Faculty, Unit, CleaningActivity, CleaningRecord
from datetime import date

User = get_user_model()


class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_manager(username='manager', email='manager@test.com', password='testpass123', faculty=None):
        """Create a manager user"""
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='MANAGER',
            faculty=faculty
        )
    
    @staticmethod
    def create_assistant(username='assistant', email='assistant@test.com', password='testpass123', faculty=None):
        """Create an assistant user"""
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='ASSISTANT',
            faculty=faculty
        )
    
    @staticmethod
    def create_dean_office(username='dean', email='dean@test.com', password='testpass123', faculty=None):
        """Create a dean office user"""
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='DEAN_OFFICE',
            faculty=faculty
        )
    
    @staticmethod
    def create_zone(zone_name='Test Zone', description='Test zone description'):
        """Create a zone"""
        return Zone.objects.create(
            zone_name=zone_name,
            description=description
        )
    
    @staticmethod
    def create_faculty(faculty_name='Test Faculty', zone=None):
        """Create a faculty"""
        if zone is None:
            zone = TestDataFactory.create_zone()
        return Faculty.objects.create(
            faculty_name=faculty_name,
            zone=zone
        )
    
    @staticmethod
    def create_unit(unit_name='Test Unit', zone=None, faculty=None, is_active=True, assigned_assistant=None):
        """Create a unit"""
        if zone is None:
            zone = TestDataFactory.create_zone()
        if faculty is None:
            faculty = TestDataFactory.create_faculty(zone=zone)
        
        return Unit.objects.create(
            unit_name=unit_name,
            zone=zone,
            faculty=faculty,
            is_active=is_active,
            assigned_assistant=assigned_assistant
        )
    
    @staticmethod
    def create_activity(
        activity_name='Test Activity',
        unit=None,
        frequency='DAILY',
        is_active=True
    ):
        """Create a cleaning activity"""
        if unit is None:
            unit = TestDataFactory.create_unit()
        
        return CleaningActivity.objects.create(
            activity_name=activity_name,
            unit=unit,
            frequency=frequency,
            is_active=is_active
        )
    
    @staticmethod
    def create_cleaning_record(
        activity=None,
        unit=None,
        scheduled_date=None,
        scheduled_time='09:00:00',
        status='PENDING',
        assigned_to=None,
        completed_date=None
    ):
        """Create a cleaning record"""
        if activity is None:
            activity = TestDataFactory.create_activity()
        if unit is None:
            unit = activity.unit
        if scheduled_date is None:
            scheduled_date = date.today()
        
        return CleaningRecord.objects.create(
            activity=activity,
            unit=unit,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            status=status,
            assigned_to=assigned_to,
            completed_date=completed_date
        )
    
    @staticmethod
    def create_complete_hierarchy():
        """
        Create a complete hierarchy: Zone -> Faculty -> Unit -> Activity -> Record
        Returns a dict with all created objects
        """
        zone = TestDataFactory.create_zone('Complete Zone')
        faculty = TestDataFactory.create_faculty('Complete Faculty', zone=zone)
        manager = TestDataFactory.create_manager('manager1', faculty=faculty)
        assistant = TestDataFactory.create_assistant('assistant1', faculty=faculty)
        
        unit = TestDataFactory.create_unit(
            unit_name='Complete Unit',
            zone=zone,
            faculty=faculty,
            assigned_assistant=assistant
        )
        
        activity = TestDataFactory.create_activity(
            activity_name='Complete Activity',
            unit=unit
        )
        
        record = TestDataFactory.create_cleaning_record(
            activity=activity,
            unit=unit,
            assigned_to=assistant
        )
        
        return {
            'zone': zone,
            'faculty': faculty,
            'manager': manager,
            'assistant': assistant,
            'unit': unit,
            'activity': activity,
            'record': record
        }


class BaseTestCase:
    """
    Mixin class providing common setup for tests
    Use by inheriting from both this and TestCase
    """
    
    def create_test_users(self):
        """Create standard test users"""
        self.manager = TestDataFactory.create_manager()
        self.assistant = TestDataFactory.create_assistant()
        self.dean = TestDataFactory.create_dean_office()
    
    def create_test_hierarchy(self):
        """Create standard test hierarchy"""
        self.zone = TestDataFactory.create_zone()
        self.faculty = TestDataFactory.create_faculty(zone=self.zone)
        self.unit = TestDataFactory.create_unit(zone=self.zone, faculty=self.faculty)
    
    def login_as_manager(self):
        """Login as manager user"""
        self.client.login(username='manager', password='testpass123')
    
    def login_as_assistant(self):
        """Login as assistant user"""
        self.client.login(username='assistant', password='testpass123')
    
    def login_as_dean(self):
        """Login as dean office user"""
        self.client.login(username='dean', password='testpass123')
