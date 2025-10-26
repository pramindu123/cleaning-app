from django import forms
from .models import ScheduleEntry

class ScheduleEntryForm(forms.ModelForm):
    class Meta:
        model = ScheduleEntry
        fields = ['entry_date', 'tasks', 'notes', 'attachments']
        widgets = {
            'entry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tasks': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'attachments': forms.FileInput(attrs={'class': 'form-control'}),
        }