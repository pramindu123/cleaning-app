from django.contrib import admin
from django.apps import apps


# Try to register admin classes for models that live in other apps (cleaning)
def _get_model(app_label, model_name):
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None


CleaningSchedule = _get_model('cleaning', 'CleaningSchedule')
Template = _get_model('cleaning', 'Template')
Report = _get_model('cleaning', 'Report')


if CleaningSchedule is not None:
    @admin.register(CleaningSchedule)
    class CleaningScheduleAdmin(admin.ModelAdmin):
        list_display = ('date', 'time', 'location', 'status')
        search_fields = ('location', 'status')


if Template is not None:
    @admin.register(Template)
    class TemplateAdmin(admin.ModelAdmin):
        list_display = ('name', 'created_at')
        search_fields = ('name',)


if Report is not None:
    @admin.register(Report)
    class ReportAdmin(admin.ModelAdmin):
        list_display = ('title', 'created_at')
        search_fields = ('title',)