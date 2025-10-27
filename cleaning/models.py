from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Zone(models.Model):
    """
    Represents a specific area within the university
    Example: Main Campus, Medical Campus, Engineering Campus
    """
    zone_name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the zone (e.g., Main Campus)"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of the zone"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Zone'
        verbose_name_plural = 'Zones'
        ordering = ['zone_name']
    
    def __str__(self):
        return self.zone_name
    
    def get_sections_count(self):
        """Return the number of sections in this zone"""
        return self.sections.count()
    
    def get_units_count(self):
        """Return the total number of units across all sections in this zone"""
        return Unit.objects.filter(section__zone=self).count()

    def get_faculties_count(self):
        """Return the number of faculties associated with this zone"""
        return self.faculties.count()


class Section(models.Model):
    """
    A physical building or sub-area belonging to a zone
    Example: Science Building, Library Block, Canteen Area
    """
    section_name = models.CharField(
        max_length=100,
        help_text="Name of the section (e.g., Science Building)"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of the section"
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='sections',
        help_text="The zone this section belongs to"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        ordering = ['zone', 'section_name']
        unique_together = [['zone', 'section_name']]
    
    def __str__(self):
        return f"{self.section_name} - {self.zone.zone_name}"
    
    def get_units_count(self):
        """Return the number of units in this section"""
        return self.units.count()
    
    def get_active_units_count(self):
        """Return the number of active units in this section"""
        return self.units.filter(is_active=True).count()


class Faculty(models.Model):
    """
    Academic or administrative division responsible for certain units
    Example: Faculty of Science, Faculty of Engineering
    """
    faculty_name = models.CharField(
        max_length=150,
        unique=True,
        help_text="Full name of the faculty"
    )
    # Optional association to a Zone (a zone can have many faculties)
    zone = models.ForeignKey(
        'Zone',
        on_delete=models.PROTECT,
        related_name='faculties',
        null=True,
        blank=True,
        help_text="Zone this faculty belongs to (optional)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculties'
        ordering = ['faculty_name']
    
    def __str__(self):
        if self.zone:
            return f"{self.faculty_name} ({self.zone.zone_name})"
        return self.faculty_name
    
    def get_units_count(self):
        """Return the number of units under this faculty"""
        return self.units.count()
    
    def get_active_units_count(self):
        """Return the number of active units under this faculty"""
        return self.units.filter(is_active=True).count()


class Unit(models.Model):
    """
    The smallest operational cleaning area.
    Must belong to a zone. Can optionally belong to a section and/or faculty.
    Example: Lecture Hall 1, Lab A, Office Room 12
    """
    unit_name = models.CharField(
        max_length=100,
        help_text="Name of the unit (e.g., Lecture Hall 1)"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of the unit"
    )
    
    # Physical hierarchy links
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='units',
        help_text="The zone this unit belongs to (required)"
    )
    
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='units',
        null=True,
        blank=True,
        help_text="The section this unit belongs to (optional)"
    )
    
    # Administrative hierarchy link
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.PROTECT,
        related_name='units',
        null=True,
        blank=True,
        help_text="The faculty responsible for this unit (optional)"
    )
    
    # Assistant assignment
    assigned_assistant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_units',
        limit_choices_to={'role': 'ASSISTANT'},
        help_text="The assistant assigned to clean this unit (optional)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this unit is currently in use or under maintenance"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Unit'
        verbose_name_plural = 'Units'
        ordering = ['zone', 'unit_name']
        unique_together = [['zone', 'unit_name']]
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.unit_name} - {status}"
    
    def clean(self):
        """Validate that unit has at least section or faculty"""
        from django.core.exceptions import ValidationError
        if not self.section and not self.faculty:
            raise ValidationError('Unit must belong to at least a Section or Faculty.')
        
        # If section is provided, validate it belongs to the same zone
        if self.section and self.section.zone_id != self.zone_id:
            raise ValidationError(f'Section "{self.section.section_name}" does not belong to zone "{self.zone.zone_name}".')
        
        # If faculty has a zone, ensure it matches the unit's zone
        if self.faculty and self.faculty.zone_id and self.faculty.zone_id != self.zone_id:
            raise ValidationError(f'Faculty "{self.faculty.faculty_name}" is associated with zone "{self.faculty.zone.zone_name}", which does not match the unit zone "{self.zone.zone_name}".')
    
    def get_zone(self):
        """Get the zone this unit belongs to"""
        return self.zone
    
    def get_full_location(self):
        """Return the complete location hierarchy"""
        if self.section:
            return f"{self.zone.zone_name} → {self.section.section_name} → {self.unit_name}"
        return f"{self.zone.zone_name} → {self.unit_name}"
    
    def get_administrative_info(self):
        """Return administrative information"""
        if self.faculty:
            return f"Faculty: {self.faculty.faculty_name}"
        return "No faculty assigned"


class CleaningActivity(models.Model):
    """
    Represents specific cleaning activities/tasks for a unit
    Example: Sweep floor, Mop floor, Clean windows, Empty trash bins
    """
    FREQUENCY_CHOICES = [
        ('TWICE_DAILY', 'Twice Per Day'),
        ('DAILY', 'Daily'),
        ('EVERY_2_DAYS', 'Every 2 Days'),
        ('WEEKLY', 'Weekly'),
        ('BIWEEKLY', 'Every 2 Weeks'),
        ('MONTHLY', 'Monthly'),
    ]
    
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='cleaning_activities',
        help_text="The unit this activity belongs to"
    )
    
    activity_name = models.CharField(
        max_length=200,
        help_text="Name of the cleaning activity (e.g., Sweep floor, Mop floor)"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the activity"
    )
    
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='DAILY',
        help_text="How often this activity should be performed"
    )
    
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this activity is currently required"
    )
    
    special_instructions = models.TextField(
        blank=True,
        help_text="Special instructions or requirements for this activity"
    )
    
    budget_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Budget working percentage (0-100)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cleaning Activity'
        verbose_name_plural = 'Cleaning Activities'
        ordering = ['unit', 'activity_name']
        unique_together = [['unit', 'activity_name']]
    
    def __str__(self):
        return f"{self.activity_name} - {self.unit.unit_name} ({self.get_frequency_display()})"
    
    def get_frequency_per_week(self):
        """Calculate how many times per week this activity occurs"""
        frequency_map = {
            'TWICE_DAILY': 14,  # 2 times a day * 7 days
            'DAILY': 7,
            'EVERY_2_DAYS': 3.5,
            'WEEKLY': 1,
            'BIWEEKLY': 0.5,
            'MONTHLY': 0.25,  # Approximately 1/4 per week
        }
        return frequency_map.get(self.frequency, 0)
    
    def get_expected_completions_for_month(self, year, month):
        """Calculate expected number of completions for a given month based on frequency"""
        import calendar as cal
        _, days_in_month = cal.monthrange(year, month)
        
        frequency_map = {
            'TWICE_DAILY': days_in_month * 2,
            'DAILY': days_in_month,
            'EVERY_2_DAYS': days_in_month // 2,
            'WEEKLY': 4,  # Approximately 4 weeks per month
            'BIWEEKLY': 2,
            'MONTHLY': 1,
        }
        return frequency_map.get(self.frequency, 0)
    
    def get_actual_completions_for_month(self, year, month):
        """Get actual number of completed records for a given month"""
        from datetime import date
        import calendar as cal
        
        first_day = date(year, month, 1)
        _, dim = cal.monthrange(year, month)
        last_day = date(year, month, dim)
        
        return self.cleaning_records.filter(
            scheduled_date__gte=first_day,
            scheduled_date__lte=last_day,
            status__in=['COMPLETED', 'VERIFIED']
        ).count()
    
    def get_completion_percentage_for_month(self, year, month):
        """Calculate actual completion percentage for a given month"""
        expected = self.get_expected_completions_for_month(year, month)
        if expected == 0:
            return 0
        actual = self.get_actual_completions_for_month(year, month)
        return round((actual / expected) * 100, 2)
    
    def get_variance_percentage_for_month(self, year, month):
        """Calculate variance between actual completion % and budgeted %"""
        actual_pct = self.get_completion_percentage_for_month(year, month)
        budgeted_pct = float(self.budget_percentage)
        return round(actual_pct - budgeted_pct, 2)


class CleaningRecord(models.Model):
    """
    Records cleaning activities performed by assistants
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('VERIFIED', 'Verified'),
    ]
    
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='cleaning_records',
        help_text="The unit that was cleaned"
    )
    
    activity = models.ForeignKey(
        CleaningActivity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cleaning_records',
        help_text="The specific activity performed (optional)"
    )
    
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_cleaning_records',
        help_text="The assistant assigned to clean this unit"
    )
    
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_cleaning_records',
        help_text="The manager who verified this cleaning"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Current status of the cleaning task"
    )
    
    scheduled_date = models.DateField(
        help_text="Date when cleaning is scheduled"
    )
    
    scheduled_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Time when cleaning is scheduled (optional)"
    )
    
    completed_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when cleaning was completed"
    )
    
    verified_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when cleaning was verified"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes or observations"
    )
    
    verification_notes = models.TextField(
        blank=True,
        help_text="Notes added by manager during verification"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cleaning Record'
        verbose_name_plural = 'Cleaning Records'
        ordering = ['-scheduled_date', '-scheduled_time']
    
    def __str__(self):
        return f"{self.unit.unit_name} - {self.scheduled_date} ({self.get_status_display()})"
    
    def clean(self):
        """Validate the cleaning record"""
        # Validate that assigned_to is an assistant
        if self.assigned_to and not self.assigned_to.is_assistant():
            raise ValidationError('Only assistants can be assigned to cleaning tasks.')
        
        # Validate that verified_by is a manager
        if self.verified_by and not self.verified_by.is_manager():
            raise ValidationError('Only managers can verify cleaning tasks.')
    
    def can_be_verified(self):
        """Check if the record can be verified"""
        return self.status == 'COMPLETED'
    
    def can_be_edited(self):
        """Check if the record can be edited"""
        return self.status in ['PENDING', 'IN_PROGRESS']

