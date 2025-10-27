from django.urls import path
from . import views

app_name = 'assistant'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedule/<int:pk>/', views.schedule_detail, name='schedule_detail'),
    path('schedule/<int:pk>/submit/', views.submit_schedule, name='submit_schedule'),
]