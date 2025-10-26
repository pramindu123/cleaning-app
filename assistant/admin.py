from django.contrib import admin
from .models import Assistant, Schedule, ScheduleEntry

@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('unit', 'month', 'assigned_assistant', 'status', 'created_date')
    list_filter = ('status', 'created_date')
    search_fields = ('unit__name', 'assigned_assistant__user__username')

@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'entry_date', 'tasks')
    list_filter = ('entry_date',)
    search_fields = ('schedule__unit__name', 'tasks')
