from django import forms
from cleaning.models import Zone, Section, Faculty, Unit, CleaningActivity


class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ['zone_name', 'description']
        widgets = {
            'zone_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter zone name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description (optional)'}),
        }


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['section_name', 'zone', 'description']
        widgets = {
            'section_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter section name'}),
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description (optional)'}),
        }


class FacultyForm(forms.ModelForm):
    existing_faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all().order_by('faculty_name'),
        required=False,
        empty_label="-- Create New Faculty --",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'existing_faculty'}),
        label="Select Existing Faculty"
    )
    
    class Meta:
        model = Faculty
        fields = ['faculty_name', 'zone']
        widgets = {
            'faculty_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter new faculty name',
                'id': 'new_faculty_name'
            }),
            'zone': forms.Select(attrs={'class': 'form-select', 'id': 'faculty_zone_select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Editing existing faculty
            self.fields['existing_faculty'].widget = forms.HiddenInput()
            self.fields['faculty_name'].label = "Faculty Name"
        else:
            # Creating new faculty
            self.fields['faculty_name'].required = False
            self.fields['faculty_name'].label = "Or Enter New Faculty Name"
        # Zone selection is always optional
        self.fields['zone'].required = False
        self.fields['zone'].empty_label = "-- No Zone (Optional) --"
    
    def clean(self):
        cleaned_data = super().clean()
        existing_faculty = cleaned_data.get('existing_faculty')
        faculty_name = cleaned_data.get('faculty_name')
        
        # If editing, skip this validation
        if self.instance and self.instance.pk:
            return cleaned_data
        
        # For creation, require either existing or new faculty name
        if not existing_faculty and not faculty_name:
            raise forms.ValidationError('Please either select an existing faculty or enter a new faculty name.')
        
        # If both are provided, prioritize new faculty name
        if existing_faculty and faculty_name:
            raise forms.ValidationError('Please either select an existing faculty OR enter a new name, not both.')
        
        return cleaned_data
    
    
    def save(self, commit=True):
        existing_faculty = self.cleaned_data.get('existing_faculty')
        
        # If existing faculty is selected, return it instead of creating new
        if existing_faculty and not (self.instance and self.instance.pk):
            return existing_faculty
        
        # Otherwise, create/update as normal
        return super().save(commit=commit)


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['unit_name', 'zone', 'section', 'faculty', 'assigned_assistant', 'description', 'is_active']
        widgets = {
            'unit_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter unit name'}),
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'assigned_assistant': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description (optional)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import User
        
        # Make zone required, but section and faculty optional
        self.fields['zone'].required = True
        self.fields['section'].required = False
        self.fields['faculty'].required = False
        self.fields['assigned_assistant'].required = False
        self.fields['section'].empty_label = "-- No Section (Optional) --"
        self.fields['faculty'].empty_label = "-- No Faculty (Optional) --"
        self.fields['assigned_assistant'].empty_label = "-- No Assistant Assigned (Optional) --"
        
        # Filter assigned_assistant to show only users with ASSISTANT role
        self.fields['assigned_assistant'].queryset = User.objects.filter(role='ASSISTANT').order_by('username')
        self.fields['assigned_assistant'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} ({obj.username})"
    
    def clean(self):
        cleaned_data = super().clean()
        section = cleaned_data.get('section')
        faculty = cleaned_data.get('faculty')
        zone = cleaned_data.get('zone')
        
        # Validate at least section or faculty is provided
        if not section and not faculty:
            raise forms.ValidationError('Unit must have at least a Section or Faculty.')
        
        # Validate section belongs to the selected zone
        if section and zone and section.zone != zone:
            raise forms.ValidationError(f'Section "{section.section_name}" does not belong to the selected zone "{zone.zone_name}".')
        
        return cleaned_data


class MonthlyScheduleActivityForm(forms.ModelForm):
    """Form for creating cleaning activities as part of monthly schedule"""
    class Meta:
        model = CleaningActivity
        fields = ['activity_name', 'description', 'frequency', 'budget_percentage', 'special_instructions']
        widgets = {
            'activity_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Sweep floor, Mop floor, Clean windows',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Brief description of the activity'
            }),
            'frequency': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'budget_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0-100',
                'min': '0',
                'max': '100',
                'step': '0.01'
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any special instructions or requirements'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['activity_name'].required = True
        self.fields['frequency'].required = True
        self.fields['description'].required = False
        self.fields['budget_percentage'].required = False
        self.fields['special_instructions'].required = False

        # Set labels
        self.fields['activity_name'].label = "Activity Name"
        self.fields['description'].label = "Description"
        self.fields['frequency'].label = "Frequency"
        self.fields['budget_percentage'].label = "Budget Percentage"
        self.fields['special_instructions'].label = "Special Instructions"
