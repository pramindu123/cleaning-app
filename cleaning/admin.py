from django.contrib import admin
from .models import Zone, Section, Faculty, Unit, CleaningActivity, CleaningRecord


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['zone_name', 'description', 'get_sections_count', 'get_units_count', 'get_faculties_count', 'created_at']
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
    
    def get_faculties_count(self, obj):
        return obj.get_faculties_count()
    get_faculties_count.short_description = 'Faculties'


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
    list_display = ['faculty_name', 'zone', 'get_units_count', 'get_active_units_count', 'created_at']
    search_fields = ['faculty_name', 'zone__zone_name']
    list_filter = ['zone', 'created_at']
    list_select_related = ['zone']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'faculty_name', 'zone')
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
        'unit_name', 'zone', 'section', 'faculty', 'assigned_assistant', 'is_active', 'created_at'
    ]
    search_fields = ['unit_name', 'description', 'zone__zone_name', 'section__section_name', 'faculty__faculty_name', 'assigned_assistant__username', 'assigned_assistant__first_name', 'assigned_assistant__last_name']
    list_filter = [
        'is_active', 'zone', 'section', 'faculty', 'assigned_assistant', 'created_at'
    ]
    list_select_related = ['zone', 'section', 'section__zone', 'faculty', 'assigned_assistant']
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
        ('Assignment', {
            'fields': ('assigned_assistant',),
            'description': 'Assistant responsible for cleaning this unit (optional)'
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


@admin.register(CleaningActivity)
class CleaningActivityAdmin(admin.ModelAdmin):
    list_display = [
        'activity_name',
        'unit',
        'frequency',
        'budget_percentage',
        'is_active',
        'created_at'
    ]
    search_fields = [
        'activity_name',
        'description',
        'unit__unit_name',
        'special_instructions'
    ]
    list_filter = ['frequency', 'is_active', 'created_at', 'unit__zone']
    list_select_related = ['unit']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'unit', 'activity_name', 'description')
        }),
        ('Schedule & Budget', {
            'fields': ('frequency', 'budget_percentage')
        }),
        ('Status & Instructions', {
            'fields': ('is_active', 'special_instructions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_activities', 'deactivate_activities']
    
    def activate_activities(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} activity(ies) activated successfully.')
    activate_activities.short_description = 'Activate selected activities'
    
    def deactivate_activities(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} activity(ies) deactivated successfully.')
    deactivate_activities.short_description = 'Deactivate selected activities'


@admin.register(CleaningRecord)
class CleaningRecordAdmin(admin.ModelAdmin):
    list_display = [
        'unit',
        'activity',
        'assigned_to', 
        'status', 
        'scheduled_date', 
        
        'completed_date',
        'verified_by',
        'created_at'
    ]
    search_fields = [
        'unit__unit_name',
        'activity__activity_name',
        'assigned_to__username',
        'assigned_to__first_name',
        'assigned_to__last_name',
        'notes',
        'verification_notes'
    ]
    list_filter = ['status', 'scheduled_date', 'created_at', 'unit__zone', 'activity']
    list_select_related = ['unit', 'activity', 'assigned_to', 'verified_by']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_date', 'verified_date']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Assignment Information', {
            'fields': ('id', 'unit', 'activity', 'assigned_to', 'status')
        }),
        ('Schedule', {
            'fields': ('scheduled_date',)
        }),
        ('Completion Details', {
            'fields': ('completed_date', 'notes'),
            'classes': ('collapse',)
        }),
        ('Verification Details', {
            'fields': ('verified_by', 'verified_date', 'verification_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_verified']
    
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        queryset = queryset.filter(status__in=['PENDING', 'IN_PROGRESS'])
        updated = queryset.update(status='COMPLETED', completed_date=timezone.now())
        self.message_user(request, f'{updated} record(s) marked as completed.')
    mark_as_completed.short_description = 'Mark selected records as completed'
    
    def mark_as_verified(self, request, queryset):
        from django.utils import timezone
        queryset = queryset.filter(status='COMPLETED')
        updated = queryset.update(
            status='VERIFIED',
            verified_by=request.user,
            verified_date=timezone.now()
        )
        self.message_user(request, f'{updated} record(s) marked as verified.')
    mark_as_verified.short_description = 'Mark selected records as verified'

