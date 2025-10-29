from django.urls import path
from . import views

app_name = 'dean'

urlpatterns = [
    path('dashboard/', views.dean_dashboard, name='dashboard'),
    path('reports/', views.faculty_reports, name='faculty_reports'),
]
