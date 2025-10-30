"""
Tests for Cleaning views (non-API endpoints)
"""
from django.test import TestCase, Client
from django.urls import reverse
from .fixtures import TestDataFactory, BaseTestCase
from cleaning.models import CleaningRecord
from datetime import date, timedelta


class CleaningRecordListViewTest(BaseTestCase, TestCase):
    """Test the cleaning_record_list view"""
    
    def setUp(self):
        self.client = Client()
        self.create_test_users()
        self.create_test_hierarchy()
        self.activity = TestDataFactory.create_activity(unit=self.unit)
    
    def test_list_view_requires_login(self):
        """Test that the list view requires authentication"""
        url = reverse('cleaning:cleaning_record_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
    
    def test_list_view_accessible_by_manager(self):
        """Test that managers can access the list view"""
        self.login_as_manager()
        url = reverse('cleaning:cleaning_record_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cleaning/cleaning_record_list.html')
    
    def test_list_shows_cleaning_records(self):
        """Test that the list displays cleaning records"""
        # Create some records
        record1 = TestDataFactory.create_cleaning_record(
            activity=self.activity,
            status='COMPLETED',
            assigned_to=self.assistant
        )
        record2 = TestDataFactory.create_cleaning_record(
            activity=self.activity,
            status='PENDING',
            assigned_to=self.assistant
        )
        
        self.login_as_manager()
        url = reverse('cleaning:cleaning_record_list')
        response = self.client.get(url)
        
        self.assertContains(response, record1.activity.activity_name)
        self.assertContains(response, 'COMPLETED')
        self.assertContains(response, 'PENDING')
    
    def test_list_filtering_by_status(self):
        """Test filtering records by status"""
        TestDataFactory.create_cleaning_record(activity=self.activity, status='COMPLETED')
        TestDataFactory.create_cleaning_record(activity=self.activity, status='PENDING')
        
        self.login_as_manager()
        url = reverse('cleaning:cleaning_record_list') + '?status=COMPLETED'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Should only show completed records
        self.assertEqual(response.context['object_list'].count(), 1)
        self.assertEqual(response.context['object_list'].first().status, 'COMPLETED')


class CleaningRecordCreateViewTest(BaseTestCase, TestCase):
    """Test creating cleaning records"""
    
    def setUp(self):
        self.client = Client()
        self.create_test_users()
        self.create_test_hierarchy()
    
    def test_create_view_requires_login(self):
        """Test that create view requires authentication"""
        url = reverse('cleaning:cleaning_record_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
    
    def test_create_single_day_record(self):
        """Test creating a single cleaning record"""
        activity = TestDataFactory.create_activity(unit=self.unit)
        
        self.login_as_manager()
        url = reverse('cleaning:cleaning_record_create')
        
        today = date.today()
        response = self.client.post(url, {
            'unit': self.unit.id,
            'activity': activity.id,
            'scheduled_date': today.isoformat(),
            'scheduled_time': '09:00',
            'assigned_to': self.assistant.id,
            'is_calendar_mark': 'false'
        })
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Verify record was created
        record = CleaningRecord.objects.filter(activity=activity).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.status, 'PENDING')
        self.assertEqual(record.assigned_to, self.assistant)
    
    def test_create_calendar_marked_record(self):
        """Test creating a record via calendar marking (directly COMPLETED)"""
        activity = TestDataFactory.create_activity(unit=self.unit)
        
        self.login_as_manager()
        url = reverse('cleaning:cleaning_record_create')
        
        today = date.today()
        response = self.client.post(url, {
            'unit': self.unit.id,
            'activity': activity.id,
            'scheduled_date': today.isoformat(),
            'scheduled_time': '09:00',
            'assigned_to': self.assistant.id,
            'is_calendar_mark': 'true'
        })
        
        # Verify record was created as COMPLETED
        record = CleaningRecord.objects.filter(activity=activity).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.status, 'COMPLETED')
        self.assertIsNotNone(record.completed_date)


class CleaningRecordCompleteViewTest(BaseTestCase, TestCase):
    """Test completing cleaning records"""
    
    def setUp(self):
        self.client = Client()
        self.create_test_users()
        self.create_test_hierarchy()
        self.activity = TestDataFactory.create_activity(unit=self.unit)
    
    def test_complete_pending_record(self):
        """Test marking a pending record as completed"""
        record = TestDataFactory.create_cleaning_record(
            activity=self.activity,
            status='PENDING',
            assigned_to=self.assistant
        )
        
        self.login_as_manager()
        url = reverse('cleaning:cleaning_record_complete', kwargs={'pk': record.id})
        response = self.client.post(url)
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        
        # Verify status changed
        record.refresh_from_db()
        self.assertEqual(record.status, 'COMPLETED')
        self.assertIsNotNone(record.completed_date)
    
    def test_cannot_complete_already_completed(self):
        """Test that you cannot re-complete a completed record"""
        record = TestDataFactory.create_cleaning_record(
            activity=self.activity,
            status='COMPLETED',
            completed_date=date.today()
        )
        
        self.login_as_manager()
        url = reverse('cleaning:cleaning_record_complete', kwargs={'pk': record.id})
        response = self.client.post(url)
        
        # Should handle gracefully (redirect or error)
        self.assertIn(response.status_code, [302, 400])


class ActivityCalendarViewTest(BaseTestCase, TestCase):
    """Test the activity calendar views"""
    
    def setUp(self):
        self.client = Client()
        self.create_test_users()
        self.create_test_hierarchy()
    
    def test_calendar_view_requires_login(self):
        """Test that calendar view requires authentication"""
        activity = TestDataFactory.create_activity(unit=self.unit)
        url = reverse('cleaning:cleaning_activity_calendar', kwargs={'pk': activity.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
    
    def test_calendar_shows_completed_days(self):
        """Test that calendar shows days marked as completed"""
        activity = TestDataFactory.create_activity(unit=self.unit)
        
        # Create a completed record for today
        today = date.today()
        TestDataFactory.create_cleaning_record(
            activity=activity,
            scheduled_date=today,
            status='COMPLETED'
        )
        
        self.login_as_manager()
        url = reverse('cleaning:cleaning_activity_calendar', kwargs={'pk': activity.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Should contain the completed day
        self.assertContains(response, str(today.day))


class RolePermissionTest(BaseTestCase, TestCase):
    """Test role-based permissions"""
    
    def setUp(self):
        self.client = Client()
        self.create_test_users()
        self.create_test_hierarchy()
        self.activity = TestDataFactory.create_activity(unit=self.unit)
    
    def test_assistant_cannot_create_activities(self):
        """Test that assistants cannot create activities"""
        self.login_as_assistant()
        url = reverse('cleaning:cleaning_activity_create')
        response = self.client.get(url)
        
        # Should deny access (403) or redirect
        self.assertIn(response.status_code, [302, 403])
    
    def test_manager_can_create_activities(self):
        """Test that managers can create activities"""
        self.login_as_manager()
        url = reverse('cleaning:cleaning_activity_create')
        response = self.client.get(url)
        
        # Should allow access
        self.assertEqual(response.status_code, 200)
    
    def test_dean_can_view_reports(self):
        """Test that dean office users can view reports"""
        self.login_as_dean()
        url = reverse('dean_office:dashboard')
        response = self.client.get(url)
        
        # Should allow access
        self.assertEqual(response.status_code, 200)


class FrequencyLimitTest(BaseTestCase, TestCase):
    """Test frequency limits for activities"""
    
    def setUp(self):
        self.client = Client()
        self.create_test_users()
        self.create_test_hierarchy()
        self.login_as_manager()
    
    def test_daily_activity_one_per_day(self):
        """Test that daily activities can only be marked once per day"""
        activity = TestDataFactory.create_activity(
            unit=self.unit,
            frequency='DAILY'
        )
        
        today = date.today()
        
        # Create first record
        url = reverse('cleaning:mark_activity_completed_day', kwargs={'pk': activity.id})
        response1 = self.client.post(url, {'date': today.isoformat()})
        self.assertEqual(response1.status_code, 200)
        
        # Try to create second record (should fail)
        response2 = self.client.post(url, {'date': today.isoformat()})
        self.assertEqual(response2.status_code, 400)
    
    def test_twice_daily_activity_two_per_day(self):
        """Test that twice daily activities can be marked twice per day"""
        activity = TestDataFactory.create_activity(
            unit=self.unit,
            frequency='TWICE_DAILY'
        )
        
        today = date.today()
        url = reverse('cleaning:mark_activity_completed_day', kwargs={'pk': activity.id})
        
        # First mark
        response1 = self.client.post(url, {'date': today.isoformat()})
        self.assertEqual(response1.status_code, 200)
        
        # Second mark (should succeed)
        response2 = self.client.post(url, {'date': today.isoformat()})
        self.assertEqual(response2.status_code, 200)
        
        # Third mark (should fail)
        response3 = self.client.post(url, {'date': today.isoformat()})
        self.assertEqual(response3.status_code, 400)
    
    def test_weekly_activity_one_per_week(self):
        """Test that weekly activities can only be marked once per week"""
        activity = TestDataFactory.create_activity(
            unit=self.unit,
            frequency='WEEKLY'
        )
        
        today = date.today()
        next_day = today + timedelta(days=1)
        
        url = reverse('cleaning:mark_activity_completed_day', kwargs={'pk': activity.id})
        
        # First mark
        response1 = self.client.post(url, {'date': today.isoformat()})
        self.assertEqual(response1.status_code, 200)
        
        # Try next day (should fail - same week)
        response2 = self.client.post(url, {'date': next_day.isoformat()})
        self.assertEqual(response2.status_code, 400)
