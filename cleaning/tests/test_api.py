"""
API Tests for Cleaning App

This module tests the AJAX/API endpoints:
- get_activities_by_unit
- mark_activity_completed_day
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from cleaning.models import Unit, Zone, Faculty, CleaningActivity, CleaningRecord
import json
from datetime import date

User = get_user_model()


class APITestCase(TestCase):
    """Base test case with common setup for API tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create users
        self.manager = User.objects.create_user(
            username='manager1',
            password='testpass123',
            role='MANAGER',
            email='manager@test.com'
        )
        
        self.assistant = User.objects.create_user(
            username='assistant1',
            password='testpass123',
            role='ASSISTANT',
            email='assistant@test.com'
        )
        
        # Create zone
        self.zone = Zone.objects.create(
            zone_name='Test Zone',
            description='Test zone for API testing'
        )
        
        # Create faculty
        self.faculty = Faculty.objects.create(
            faculty_name='Test Faculty',
            zone=self.zone
        )
        
        # Create unit
        self.unit = Unit.objects.create(
            unit_name='Test Unit',
            zone=self.zone,
            faculty=self.faculty,
            is_active=True
        )
        
        # Create client
        self.client = Client()


class GetActivitiesByUnitAPITest(APITestCase):
    """Test the get_activities_by_unit API endpoint"""
    
    def test_get_activities_success(self):
        """Test retrieving activities for a unit"""
        # Create some activities
        activity1 = CleaningActivity.objects.create(
            unit=self.unit,
            activity_name='Sweep floor',
            frequency='DAILY',
            is_active=True
        )
        activity2 = CleaningActivity.objects.create(
            unit=self.unit,
            activity_name='Mop floor',
            frequency='TWICE_DAILY',
            is_active=True
        )
        
        # Login as manager
        self.client.login(username='manager1', password='testpass123')
        
        # Make API request
        url = reverse('cleaning:get_activities_by_unit', kwargs={'unit_id': self.unit.id})
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('activities', data)
        self.assertEqual(len(data['activities']), 2)
        
        # Check activity data (verify both activities are in response, regardless of order)
        activities = data['activities']
        activity_names = [act['activity_name'] for act in activities]
        self.assertIn('Sweep floor', activity_names)
        self.assertIn('Mop floor', activity_names)
    
    def test_get_activities_only_active(self):
        """Test that only active activities are returned"""
        # Create active and inactive activities
        CleaningActivity.objects.create(
            unit=self.unit,
            activity_name='Active Activity',
            frequency='DAILY',
            is_active=True
        )
        CleaningActivity.objects.create(
            unit=self.unit,
            activity_name='Inactive Activity',
            frequency='DAILY',
            is_active=False
        )
        
        self.client.login(username='manager1', password='testpass123')
        url = reverse('cleaning:get_activities_by_unit', kwargs={'unit_id': self.unit.id})
        response = self.client.get(url)
        
        data = response.json()
        self.assertEqual(len(data['activities']), 1)
        self.assertEqual(data['activities'][0]['activity_name'], 'Active Activity')
    
    def test_get_activities_requires_login(self):
        """Test that the endpoint requires authentication"""
        url = reverse('cleaning:get_activities_by_unit', kwargs={'unit_id': self.unit.id})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class MarkActivityCompletedDayAPITest(APITestCase):
    """Test the mark_activity_completed_day API endpoint"""
    
    def setUp(self):
        super().setUp()
        # Create an activity for marking
        self.activity = CleaningActivity.objects.create(
            unit=self.unit,
            activity_name='Daily Cleaning',
            frequency='DAILY',
            is_active=True
        )
    
    def test_mark_day_completed_success(self):
        """Test successfully marking a day as completed"""
        self.client.login(username='manager1', password='testpass123')
        
        url = reverse('cleaning:mark_activity_completed_day', kwargs={'pk': self.activity.id})
        response = self.client.post(url, {
            'date': '2025-10-30',
            'assigned_to': self.assistant.id
        })
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertIn('record_id', data)
        self.assertEqual(data['status'], 'COMPLETED')
        
        # Verify record was created
        record = CleaningRecord.objects.get(id=data['record_id'])
        self.assertEqual(record.status, 'COMPLETED')
        self.assertEqual(record.scheduled_date, date(2025, 10, 30))
        self.assertEqual(record.assigned_to, self.assistant)
    
    def test_mark_day_completed_twice_daily(self):
        """Test marking a twice daily activity"""
        activity = CleaningActivity.objects.create(
            unit=self.unit,
            activity_name='Twice Daily Clean',
            frequency='TWICE_DAILY',
            is_active=True
        )
        
        self.client.login(username='manager1', password='testpass123')
        url = reverse('cleaning:mark_activity_completed_day', kwargs={'pk': activity.id})
        
        # Mark first time
        response1 = self.client.post(url, {'date': '2025-10-30'})
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(response1.json()['ok'])
        
        # Mark second time (should work)
        response2 = self.client.post(url, {'date': '2025-10-30'})
        self.assertEqual(response2.status_code, 200)
        self.assertTrue(response2.json()['ok'])
        
        # Third time should fail
        response3 = self.client.post(url, {'date': '2025-10-30'})
        self.assertEqual(response3.status_code, 400)
        self.assertFalse(response3.json()['ok'])
    
    def test_mark_day_requires_manager(self):
        """Test that only managers can mark days"""
        self.client.login(username='assistant1', password='testpass123')
        
        url = reverse('cleaning:mark_activity_completed_day', kwargs={'pk': self.activity.id})
        response = self.client.post(url, {'date': '2025-10-30'})
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('Permission denied', data['error'])
    
    def test_mark_day_invalid_date(self):
        """Test marking with invalid date format"""
        self.client.login(username='manager1', password='testpass123')
        
        url = reverse('cleaning:mark_activity_completed_day', kwargs={'pk': self.activity.id})
        response = self.client.post(url, {'date': 'invalid-date'})
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('Invalid date', data['error'])
    
    def test_mark_day_monthly_limit(self):
        """Test monthly frequency limit"""
        activity = CleaningActivity.objects.create(
            unit=self.unit,
            activity_name='Monthly Clean',
            frequency='MONTHLY',
            is_active=True
        )
        
        self.client.login(username='manager1', password='testpass123')
        url = reverse('cleaning:mark_activity_completed_day', kwargs={'pk': activity.id})
        
        # Mark first day
        response1 = self.client.post(url, {'date': '2025-10-15'})
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(response1.json()['ok'])
        
        # Try to mark another day in same month (should fail)
        response2 = self.client.post(url, {'date': '2025-10-20'})
        self.assertEqual(response2.status_code, 400)
        self.assertFalse(response2.json()['ok'])
        self.assertIn('Monthly limit', response2.json()['error'])
    
    def test_mark_day_requires_post(self):
        """Test that GET requests are not allowed"""
        self.client.login(username='manager1', password='testpass123')
        
        url = reverse('cleaning:mark_activity_completed_day', kwargs={'pk': self.activity.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 405)
        self.assertFalse(response.json()['ok'])


class CleaningRecordAPIIntegrationTest(APITestCase):
    """Integration tests for the full workflow"""
    
    def test_create_activity_and_mark_completed_workflow(self):
        """Test the complete workflow of creating activity and marking it completed"""
        self.client.login(username='manager1', password='testpass123')
        
        # 1. Create an activity
        activity = CleaningActivity.objects.create(
            unit=self.unit,
            activity_name='Integration Test Activity',
            frequency='DAILY',
            is_active=True
        )
        
        # 2. Get activities for the unit
        get_url = reverse('cleaning:get_activities_by_unit', kwargs={'unit_id': self.unit.id})
        get_response = self.client.get(get_url)
        self.assertEqual(get_response.status_code, 200)
        activities = get_response.json()['activities']
        self.assertEqual(len(activities), 1)
        
        # 3. Mark a day as completed
        mark_url = reverse('cleaning:mark_activity_completed_day', kwargs={'pk': activity.id})
        mark_response = self.client.post(mark_url, {
            'date': '2025-10-30',
            'assigned_to': self.assistant.id
        })
        self.assertEqual(mark_response.status_code, 200)
        self.assertTrue(mark_response.json()['ok'])
        
        # 4. Verify the record was created with correct data
        record_id = mark_response.json()['record_id']
        record = CleaningRecord.objects.get(id=record_id)
        self.assertEqual(record.activity, activity)
        self.assertEqual(record.unit, self.unit)
        self.assertEqual(record.status, 'COMPLETED')
        self.assertIsNotNone(record.completed_date)
