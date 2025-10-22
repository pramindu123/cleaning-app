from django.contrib import admin
from .models import Zone, Section, Faculty, Unit


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['zone_name', 'description', 'get_sections_count', 'get_units_count', 'created_at']
    search_fields = ['zone_name', 'description']
    list_filter = ['created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'zone_name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_sections_count(self, obj):
        return obj.get_sections_count()
    get_sections_count.short_description = 'Sections'
    
    def get_units_count(self, obj):
        return obj.get_units_count()
    get_units_count.short_description = 'Total Units'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['section_name', 'zone', 'description', 'get_units_count', 'get_active_units_count', 'created_at']
    search_fields = ['section_name', 'description', 'zone__zone_name']
    list_filter = ['zone', 'created_at']
    list_select_related = ['zone']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'section_name', 'zone')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_units_count(self, obj):
        return obj.get_units_count()
    get_units_count.short_description = 'Total Units'
    
    def get_active_units_count(self, obj):
        return obj.get_active_units_count()
    get_active_units_count.short_description = 'Active Units'


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['faculty_name', 'get_units_count', 'get_active_units_count', 'created_at']
    search_fields = ['faculty_name']
    list_filter = ['created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'faculty_name')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_units_count(self, obj):
        return obj.get_units_count()
    get_units_count.short_description = 'Total Units'
    
    def get_active_units_count(self, obj):
        return obj.get_active_units_count()
    get_active_units_count.short_description = 'Active Units'


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = [
        'unit_name', 'zone', 'section', 'faculty', 'is_active', 'created_at'
    ]
    search_fields = ['unit_name', 'description', 'zone__zone_name', 'section__section_name', 'faculty__faculty_name']
    list_filter = [
        'is_active', 'zone', 'section', 'faculty', 'created_at'
    ]
    list_select_related = ['zone', 'section', 'section__zone', 'faculty']
    readonly_fields = ['id', 'created_at', 'updated_at', 'get_full_location']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Location (Physical Hierarchy)', {
            'fields': ('zone', 'section', 'get_full_location'),
            'description': 'Physical location: Zone (required) → Section (optional) → Unit'
        }),
        ('Administration', {
            'fields': ('faculty',),
            'description': 'Administrative responsibility (optional)'
        }),
        ('Basic Information', {
            'fields': ('id', 'unit_name', 'description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_location(self, obj):
        return obj.get_full_location()
    get_full_location.short_description = 'Full Location Path'
    
    actions = ['activate_units', 'deactivate_units']
    
    def activate_units(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} unit(s) activated successfully.')
    activate_units.short_description = 'Activate selected units'
    
    def deactivate_units(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} unit(s) deactivated successfully.')
    deactivate_units.short_description = 'Deactivate selected units'
