from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with role field"""
    
    ROLE_CHOICES = [
        ('MANAGER', 'Manager'),
        ('ASSISTANT', 'Assistant'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='ASSISTANT',
        help_text='User role in the system'
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
