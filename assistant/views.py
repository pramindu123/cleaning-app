from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import Q, Count
from cleaning.models import CleaningRecord, Unit, CleaningActivity
from .models import Schedule, ScheduleEntry, Assistant
from .forms import ScheduleEntryForm

@login_required
def dashboard(request):
    """Assistant dashboard showing their cleaning tasks and statistics"""
    # Check if user is an assistant
    if not request.user.is_assistant():
        messages.error(request, "You do not have permission to access the assistant dashboard.")
        return redirect('dashboard')
    
    today = timezone.localdate()
    
    # Get all records assigned to this assistant
    all_records = CleaningRecord.objects.filter(assigned_to=request.user).select_related(
        'unit', 'activity', 'unit__zone', 'unit__section', 'unit__faculty'
    )
    
    # Statistics
    total_assigned = all_records.count()
    total_completed = all_records.filter(status__in=['COMPLETED', 'VERIFIED']).count()
    total_pending = all_records.filter(status='PENDING').count()
    total_in_progress = all_records.filter(status='IN_PROGRESS').count()
    total_verified = all_records.filter(status='VERIFIED').count()
    
    # Assigned units
    assigned_unit_ids = all_records.values_list('unit_id', flat=True).distinct()
    assigned_units = Unit.objects.filter(id__in=assigned_unit_ids).select_related('zone', 'section', 'faculty')
    
    # Relevant cleaning activities for this assistant (from units assigned to them)
    my_activities_qs = CleaningActivity.objects.filter(
        unit__assigned_assistant=request.user,
        is_active=True
    ).select_related('unit').order_by('unit__unit_name', 'activity_name')
    activities_total = my_activities_qs.count()
    my_activities = list(my_activities_qs[:12])
    
    # Recent completed activities (completed/verified records)
    completed_activities = all_records.filter(
        status__in=['COMPLETED', 'VERIFIED']
    ).select_related('unit', 'activity').order_by('-completed_date')[:10]
    
    # Completion rate
    completion_rate = 0
    if total_assigned > 0:
        completion_rate = round((total_completed / total_assigned) * 100, 1)
    
    context = {
        'user': request.user,
        'assigned_units': assigned_units,
        'total_assigned': total_assigned,
        'total_completed': total_completed,
        'total_pending': total_pending,
        'total_in_progress': total_in_progress,
        'total_verified': total_verified,
        'completion_rate': completion_rate,
        'total_units': assigned_units.count(),
        'my_activities': my_activities,
        'activities_total': activities_total,
        'completed_activities': completed_activities,
    }
    return render(request, 'assistant/dashboard.html', context)

@login_required
def schedule_list(request):
    try:
        assistant = request.user.assistant
    except Assistant.DoesNotExist:
        messages.error(request, "You are not registered as an assistant.")
        return redirect('assistant:dashboard')
    
    status_filter = request.GET.get('status', 'all')
    
    schedules = Schedule.objects.filter(assigned_assistant=assistant)
    
    if status_filter != 'all':
        schedules = schedules.filter(status=status_filter)
    
    context = {
        'schedules': schedules.order_by('-month'),
        'status_filter': status_filter,
    }
    return render(request, 'assistant/schedule_list.html', context)

@login_required
def schedule_detail(request, pk):
    try:
        assistant = request.user.assistant
    except Assistant.DoesNotExist:
        messages.error(request, "You are not registered as an assistant.")
        return redirect('assistant:dashboard')
    
    schedule = get_object_or_404(Schedule, pk=pk, assigned_assistant=assistant)
    entries = schedule.entries.all()
    
    context = {
        'schedule': schedule,
        'entries': entries,
        'can_edit': schedule.status == 'draft',
    }
    return render(request, 'assistant/schedule_detail.html', context)

@login_required
def submit_schedule(request, pk):
    try:
        assistant = request.user.assistant
    except Assistant.DoesNotExist:
        messages.error(request, "You are not registered as an assistant.")
        return redirect('assistant:dashboard')
    
    schedule = get_object_or_404(Schedule, pk=pk, assigned_assistant=assistant)
    
    if schedule.status != 'draft':
        messages.error(request, "Only draft schedules can be submitted.")
        return redirect('assistant:schedule_detail', pk=pk)
    
    if not schedule.entries.exists():
        messages.error(request, "Cannot submit an empty schedule.")
        return redirect('assistant:schedule_detail', pk=pk)
    
    schedule.status = 'submitted'
    schedule.submitted_date = timezone.now()
    schedule.save()
    
    messages.success(request, "Schedule submitted for review successfully!")
    return redirect('assistant:schedule_list')

@login_required
def profile(request):
    """Assistant profile page"""
    if not request.user.is_assistant():
        messages.error(request, "You do not have permission to access the assistant profile.")
        return redirect('dashboard')
    
    # Get statistics for the profile
    all_records = CleaningRecord.objects.filter(assigned_to=request.user)
    total_assigned = all_records.count()
    total_completed = all_records.filter(status__in=['COMPLETED', 'VERIFIED']).count()
    total_verified = all_records.filter(status='VERIFIED').count()
    
    context = {
        'user': request.user,
        'total_assigned': total_assigned,
        'total_completed': total_completed,
        'total_verified': total_verified,
    }
    return render(request, 'assistant/profile.html', context)