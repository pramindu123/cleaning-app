from django.urls import path
from . import views

app_name = 'cleaning'

urlpatterns = [
    # Cleaning Record URLs
    path('records/', views.cleaning_record_list, name='cleaning_record_list'),
    path('records/create/', views.cleaning_record_create, name='cleaning_record_create'),
    path('records/<int:pk>/', views.cleaning_record_detail, name='cleaning_record_detail'),
    path('records/<int:pk>/update/', views.cleaning_record_update, name='cleaning_record_update'),
    path('records/<int:pk>/delete/', views.cleaning_record_delete, name='cleaning_record_delete'),
    path('records/<int:pk>/complete/', views.cleaning_record_complete, name='cleaning_record_complete'),
    path('records/<int:pk>/verify/', views.cleaning_record_verify, name='cleaning_record_verify'),
    
    # Performance Reports
    path('reports/performance/', views.activity_performance_report, name='activity_performance_report'),
    path('reports/faculties/', views.faculty_list_report, name='faculty_list_report'),
    path('reports/faculty/<int:faculty_id>/', views.faculty_cleaning_report, name='faculty_cleaning_report'),
    
    # Cleaning Activity URLs
    path('activities/', views.cleaning_activity_list, name='cleaning_activity_list'),
    path('activities/create/', views.cleaning_activity_create, name='cleaning_activity_create'),
    path('activities/create/multiple/', views.cleaning_activity_create_multiple, name='cleaning_activity_create_multiple'),
    path('activities/<int:pk>/', views.cleaning_activity_detail, name='cleaning_activity_detail'),
    path('activities/<int:pk>/update/', views.cleaning_activity_update, name='cleaning_activity_update'),
    path('activities/<int:pk>/delete/', views.cleaning_activity_delete, name='cleaning_activity_delete'),
    path('activities/<int:pk>/calendar/', views.cleaning_activity_calendar, name='cleaning_activity_calendar'),
    path('activities/<int:pk>/calendar/<int:year>/<int:month>/', views.cleaning_activity_calendar, name='cleaning_activity_calendar_month'),
    # Bulk add activities under a unit
    path('units/<int:unit_id>/activities/bulk/', views.unit_activities_bulk, name='unit_activities_bulk'),
    # Calendar partial for embedding in forms
    path('activities/<int:pk>/calendar/partial/', views.cleaning_activity_calendar_partial, name='cleaning_activity_calendar_partial'),
    # API to mark a day completed for an activity
    path('api/activities/<int:pk>/complete-day/', views.mark_activity_completed_day, name='mark_activity_completed_day'),
    
    # AJAX endpoints
    path('api/activities/unit/<int:unit_id>/', views.get_activities_by_unit, name='get_activities_by_unit'),
]
