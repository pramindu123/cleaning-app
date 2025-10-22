from django.db import models
from django.core.exceptions import ValidationError


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculties'
        ordering = ['faculty_name']
    
    def __str__(self):
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
