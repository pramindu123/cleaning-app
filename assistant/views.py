from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from .models import Schedule, ScheduleEntry, Assistant
from .forms import ScheduleEntryForm

@login_required
def dashboard(request):
    try:
        assistant = request.user.assistant
    except Assistant.DoesNotExist:
        messages.error(request, "You are not registered as an assistant.")
        return render(request, 'assistant/not_assistant.html')
    
    schedules = Schedule.objects.filter(assigned_assistant=assistant)
    
    # Get unique units assigned to this assistant
    assigned_units = schedules.values('unit').distinct()
    from cleaning.models import Unit
    allocated_areas = Unit.objects.filter(id__in=[s['unit'] for s in assigned_units])
    
    context = {
        'assistant': assistant,
        'allocated_areas': allocated_areas,
        'draft_schedules': schedules.filter(status='draft')[:5],
        'submitted_schedules': schedules.filter(status='submitted')[:5],
        'total_draft': schedules.filter(status='draft').count(),
        'total_submitted': schedules.filter(status='submitted').count(),
        'total_approved': schedules.filter(status='approved').count(),
        'total_areas': allocated_areas.count(),
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
    try:
        assistant = request.user.assistant
    except Assistant.DoesNotExist:
        messages.error(request, "You are not registered as an assistant.")
        return redirect('assistant:dashboard')
    
    return render(request, 'assistant/profile.html', {'assistant': assistant})