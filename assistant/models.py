from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

User = get_user_model()

class Assistant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()}"
    
    def get_assigned_schedules(self):
        return Schedule.objects.filter(assigned_assistant=self)

class Schedule(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Review'),
        ('approved', 'Approved'),
        ('changes_requested', 'Changes Requested'),
    ]
    
    unit = models.ForeignKey('cleaning.Unit', on_delete=models.CASCADE, related_name='assistant_schedules')
    month = models.DateField()
    assigned_assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_date = models.DateTimeField(auto_now_add=True)
    submitted_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['unit', 'month']
    
    def __str__(self):
        return f"{self.unit.name} - {self.month.strftime('%B %Y')}"
    
    def get_absolute_url(self):
        return reverse('assistant:schedule_detail', kwargs={'pk': self.pk})
    
    def can_edit(self):
        return self.status == 'draft'

class ScheduleEntry(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='entries')
    entry_date = models.DateField()
    tasks = models.TextField()
    notes = models.TextField(blank=True)
    attachments = models.FileField(upload_to='schedule_attachments/', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['entry_date']
        verbose_name_plural = "Schedule entries"
    
    def __str__(self):
        return f"Entry for {self.entry_date} - {self.schedule}"