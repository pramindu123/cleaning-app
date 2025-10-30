from django.urls import path
from . import views

app_name = 'dean_office'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reports/', views.reports, name='reports'),
    path('kpis/', views.kpis, name='kpis'),
    path('monitoring/', views.monitoring, name='monitoring'),
    path('templates/', views.templates_view, name='templates_list'),
]
