from django.urls import path
from . import views

app_name = 'manager'

urlpatterns = [
    path('dashboard/', views.manager_dashboard, name='dashboard'),
    
    # Zones
    path('zones/', views.zones_list, name='zones_list'),
    path('zones/create/', views.zone_create, name='zone_create'),
    path('zones/<int:zone_id>/', views.zone_detail, name='zone_detail'),
    path('zones/<int:zone_id>/edit/', views.zone_update, name='zone_update'),
    path('zones/<int:zone_id>/delete/', views.zone_delete, name='zone_delete'),
    
    # Sections
    path('sections/', views.sections_list, name='sections_list'),
    path('sections/create/', views.section_create, name='section_create'),
    path('sections/<int:section_id>/', views.section_detail, name='section_detail'),
    path('sections/<int:section_id>/edit/', views.section_update, name='section_update'),
    path('sections/<int:section_id>/delete/', views.section_delete, name='section_delete'),
    
    # Faculties
    path('faculties/', views.faculties_list, name='faculties_list'),
    path('faculties/create/', views.faculty_create, name='faculty_create'),
    path('faculties/<int:faculty_id>/', views.faculty_detail, name='faculty_detail'),
    path('faculties/<int:faculty_id>/edit/', views.faculty_update, name='faculty_update'),
    path('faculties/<int:faculty_id>/delete/', views.faculty_delete, name='faculty_delete'),
    
    # Units
    path('units/', views.units_list, name='units_list'),
    path('units/create/', views.unit_create, name='unit_create'),
    path('units/<int:unit_id>/', views.unit_detail, name='unit_detail'),
    path('units/<int:unit_id>/edit/', views.unit_update, name='unit_update'),
    path('units/<int:unit_id>/delete/', views.unit_delete, name='unit_delete'),
        path('units/<int:unit_id>/schedule/', views.unit_schedule_monthly, name='unit_schedule_monthly'),
    
    # Assistants
    path('assistants/', views.assistants_list, name='assistants_list'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
]

