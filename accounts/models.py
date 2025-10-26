from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with role field"""
    
    ROLE_CHOICES = [
        ('MANAGER', 'Manager'),
        ('ASSISTANT', 'Assistant'),
        ('DEAN_OFFICE', 'Dean Office'),
    ]
    
    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default='ASSISTANT',
        help_text='User role in the system'
    )
    
    faculty = models.ForeignKey(
        'cleaning.Faculty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dean_users',
        help_text='Faculty this dean office user is associated with (for DEAN_OFFICE role)'
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_manager(self):
        """Check if user is a manager"""
        return self.role == 'MANAGER'
    
    def is_assistant(self):
        """Check if user is an assistant"""
        return self.role == 'ASSISTANT'
    
    def is_dean_office(self):
        """Check if user is from dean office"""
        return self.role == 'DEAN_OFFICE'
