from django import forms
from cleaning.models import Zone, Section, Faculty, Unit


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
    class Meta:
        model = Faculty
        fields = ['faculty_name']
        widgets = {
            'faculty_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter faculty name'}),
        }


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['unit_name', 'zone', 'section', 'faculty', 'description', 'is_active']
        widgets = {
            'unit_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter unit name'}),
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description (optional)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make zone required, but section and faculty optional
        self.fields['zone'].required = True
        self.fields['section'].required = False
        self.fields['faculty'].required = False
        self.fields['section'].empty_label = "-- No Section (Optional) --"
        self.fields['faculty'].empty_label = "-- No Faculty (Optional) --"
    
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
