from django import forms
from django.contrib.auth import get_user_model
from .models import CleaningRecord, Unit, CleaningActivity

User = get_user_model()


class CleaningRecordForm(forms.ModelForm):
    """Form for creating and updating cleaning records"""
    
    class Meta:
        model = CleaningRecord
        fields = ['unit', 'activity', 'assigned_to', 'scheduled_date', 'notes']
        widgets = {
            'unit': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'id': 'id_unit'
            }),
            'activity': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_activity'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            # Render as month picker; format is set in __init__
            'scheduled_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'month',
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add any additional notes or special instructions...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter users to show only assistants
        self.fields['assigned_to'].queryset = User.objects.filter(role='ASSISTANT')
        self.fields['assigned_to'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} ({obj.username})"
        
        # Filter units to show only active units
        self.fields['unit'].queryset = Unit.objects.filter(is_active=True)
        self.fields['unit'].label_from_instance = lambda obj: obj.get_full_location()
        
        # Activity field - will be filtered by unit via JavaScript
        self.fields['activity'].queryset = CleaningActivity.objects.filter(is_active=True)
        self.fields['activity'].required = False
        self.fields['activity'].empty_label = "-- No specific activity (General cleaning) --"
        
        # Set help texts
        self.fields['unit'].help_text = "Select the unit to be cleaned"
        # Force month-only input for scheduled_date
        self.fields['scheduled_date'].widget = forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'month',
                'required': True,
            },
            format='%Y-%m'
        )
        # Accept both YYYY-MM (from the month picker) and YYYY-MM-DD (if provided via links)
        self.fields['scheduled_date'].input_formats = ['%Y-%m', '%Y-%m-%d']
        self.fields['scheduled_date'].label = "Scheduled Month"

        # Set help texts
        self.fields['unit'].help_text = "Select the unit to be cleaned"
        self.fields['activity'].help_text = "Select a specific cleaning activity (optional)"
        self.fields['assigned_to'].help_text = "Select the assistant responsible for cleaning"
        self.fields['scheduled_date'].help_text = "Month when cleaning should be performed"

class CleaningVerificationForm(forms.ModelForm):
    """Form for managers to verify completed cleaning records"""
    
    class Meta:
        fields = ['verification_notes']
        widgets = {
            'verification_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add verification notes (e.g., quality assessment, issues found)...',
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['verification_notes'].required = True
        self.fields['verification_notes'].label = "Verification Notes"


class CleaningCompletionForm(forms.ModelForm):
    """Form for assistants to mark cleaning as completed"""
    
    class Meta:
        model = CleaningRecord
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add any observations or notes about the cleaning...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].label = "Completion Notes"
        self.fields['notes'].help_text = "Add any notes about the cleaning task"


class CleaningRecordFilterForm(forms.Form):
    """Form for filtering cleaning records"""
    
    STATUS_CHOICES = [('', 'All Statuses')] + CleaningRecord.STATUS_CHOICES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.filter(is_active=True),
        required=False,
        empty_label="All Units",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(role='ASSISTANT'),
        required=False,
        empty_label="All Assistants",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'From Date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'To Date'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username}"
        self.fields['unit'].label_from_instance = lambda obj: obj.get_full_location()


class CleaningActivityForm(forms.ModelForm):
    """Form for creating and updating cleaning activities"""
    
    class Meta:
        model = CleaningActivity
        fields = ['unit', 'activity_name', 'description', 'frequency', 'budget_percentage', 'is_active', 'special_instructions']
        widgets = {
            'unit': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'activity_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Sweep floor, Mop floor, Clean windows',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detailed description of the activity (optional)'
            }),
            'frequency': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'budget_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '0.00'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Special instructions or requirements (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        unit = kwargs.pop('unit', None)
        super().__init__(*args, **kwargs)
        
        # Filter units to show only active units
        self.fields['unit'].queryset = Unit.objects.filter(is_active=True)
        self.fields['unit'].label_from_instance = lambda obj: obj.get_full_location()
        
        # If unit is provided, set it as initial and make it read-only
        if unit:
            self.fields['unit'].initial = unit
            self.fields['unit'].widget.attrs['readonly'] = True
        
        # Set help texts
        self.fields['activity_name'].help_text = "Name of the cleaning activity"
        self.fields['frequency'].help_text = "How often this activity should be performed"
        self.fields['budget_percentage'].help_text = "Budget working percentage (0-100)"
        self.fields['budget_percentage'].label = "Budget Percentage (%)"
        self.fields['is_active'].help_text = "Uncheck to deactivate this activity"

