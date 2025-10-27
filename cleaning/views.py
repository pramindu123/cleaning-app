from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, datetime, time as dtime, timedelta
import calendar
from django.db.models import Q
from django.http import JsonResponse
from django.forms import inlineformset_factory, modelformset_factory
from .models import CleaningRecord, CleaningActivity, Unit, Faculty
from .forms import (
    CleaningRecordForm, 
    CleaningVerificationForm, 
    CleaningCompletionForm,
    CleaningRecordFilterForm,
    CleaningActivityForm
)

@login_required
def cleaning_record_list(request):
    """List all cleaning records with filtering"""
    records = CleaningRecord.objects.select_related(
        'unit', 'activity', 'assigned_to', 'verified_by'
    ).all()
    
    # Apply filters
    filter_form = CleaningRecordFilterForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('status'):
            records = records.filter(status=filter_form.cleaned_data['status'])
        if filter_form.cleaned_data.get('unit'):
            records = records.filter(unit=filter_form.cleaned_data['unit'])
        if filter_form.cleaned_data.get('assigned_to'):
            records = records.filter(assigned_to=filter_form.cleaned_data['assigned_to'])
        if filter_form.cleaned_data.get('date_from'):
            records = records.filter(scheduled_date__gte=filter_form.cleaned_data['date_from'])
        if filter_form.cleaned_data.get('date_to'):
            records = records.filter(scheduled_date__lte=filter_form.cleaned_data['date_to'])
    
    # Filter by user role
    if request.user.is_assistant():
        # Assistants see only their assigned tasks
        records = records.filter(assigned_to=request.user)
    
    context = {
        'records': records,
        'filter_form': filter_form,
    }
    return render(request, 'cleaning/cleaning_record_list.html', context)


@login_required
def cleaning_record_create(request):
    """Create a new cleaning record (Managers and Assistants)"""
    # Both managers and assistants can create records
    if not (request.user.is_manager() or request.user.is_assistant()):
        messages.error(request, 'You do not have permission to create cleaning records.')
        return redirect('cleaning:cleaning_record_list')
    
    # Support initial values from query params
    initial = {}
    if 'unit' in request.GET:
        initial['unit'] = request.GET.get('unit')
    if 'activity' in request.GET:
        initial['activity'] = request.GET.get('activity')
    if 'scheduled_date' in request.GET:
        initial['scheduled_date'] = request.GET.get('scheduled_date')
    
    # If assistant, set assigned_to to themselves
    if request.user.is_assistant():
        initial['assigned_to'] = request.user.id
    
    if request.method == 'POST':
        form = CleaningRecordForm(request.POST)
        if form.is_valid():
            try:
                # Read any calendar-selected days (comma-separated YYYY-MM-DD)
                raw_days = (request.POST.get('selected_days') or '').strip()
                selected_days = [s for s in (raw_days.split(',') if raw_days else []) if s]

                unit = form.cleaned_data['unit']
                activity = form.cleaned_data.get('activity')
                assigned_to = form.cleaned_data['assigned_to']
                status = form.cleaned_data['status']
                notes = form.cleaned_data.get('notes', '')

                # If assistant is creating, force assign to themselves
                if request.user.is_assistant():
                    assigned_to = request.user

                created_records = []
                if selected_days:
                    # Calendar-driven multi-day creation. Require an activity.
                    if not activity:
                        messages.error(request, 'Please select an activity to use the calendar selections.')
                        raise ValueError('Activity required for calendar selections')

                    # Establish biweekly anchor: earliest existing record date for the activity, or first selected date in this submission
                    existing_anchor = CleaningRecord.objects.filter(activity=activity).order_by('scheduled_date').values_list('scheduled_date', flat=True).first()
                    # Pre-parse selected dates to determine first selected anchor
                    parsed_selected = []
                    for s in selected_days:
                        try:
                            parsed_selected.append(datetime.strptime(s, '%Y-%m-%d').date())
                        except Exception:
                            continue
                    parsed_selected.sort()
                    session_anchor = existing_anchor or (parsed_selected[0] if parsed_selected else None)

                    # Helper to enforce frequency rules similar to AJAX endpoint
                    def can_create_for_day(act, scheduled_date):
                        first_day = date(scheduled_date.year, scheduled_date.month, 1)
                        _, dim = calendar.monthrange(scheduled_date.year, scheduled_date.month)
                        last_day = date(scheduled_date.year, scheduled_date.month, dim)

                        day_qs = CleaningRecord.objects.filter(activity=act, scheduled_date=scheduled_date)
                        day_count = day_qs.count()

                        month_completed = CleaningRecord.objects.filter(
                            activity=act,
                            scheduled_date__gte=first_day,
                            scheduled_date__lte=last_day,
                            status__in=['COMPLETED', 'VERIFIED']
                        ).count()

                        week_start = scheduled_date - timedelta(days=scheduled_date.weekday())
                        week_end = week_start + timedelta(days=6)
                        week_completed = CleaningRecord.objects.filter(
                            activity=act,
                            scheduled_date__gte=week_start,
                            scheduled_date__lte=week_end,
                            status__in=['COMPLETED', 'VERIFIED']
                        ).count()

                        freq = act.frequency
                        if freq == 'TWICE_DAILY':
                            return day_count < 2
                        elif freq == 'DAILY':
                            return day_count < 1
                        elif freq == 'EVERY_2_DAYS':
                            # Use existing anchor if available; otherwise allow first selected to establish anchor
                            if session_anchor:
                                return ((scheduled_date - session_anchor).days % 2) == 0 and day_count < 1
                            return day_count < 1
                        elif freq == 'WEEKLY':
                            return week_completed < 1 and day_count < 1
                        elif freq == 'BIWEEKLY':
                            if session_anchor:
                                return ((scheduled_date - session_anchor).days % 14) == 0 and day_count < 1
                            return day_count < 1
                        elif freq == 'MONTHLY':
                            return month_completed < 1 and day_count < 1
                        return False

                    for s in selected_days:
                        try:
                            sd = datetime.strptime(s, '%Y-%m-%d').date()
                        except Exception:
                            continue
                        # Ensure date is within the selected month from the form's scheduled_date
                        sched_month = form.cleaned_data['scheduled_date']
                        if sd.year != sched_month.year or sd.month != sched_month.month:
                            continue
                        if not can_create_for_day(activity, sd):
                            continue

                        # For TWICE_DAILY, create up to two records per day (fill missing ones)
                        if activity.frequency == 'TWICE_DAILY':
                            existing_for_day = list(CleaningRecord.objects.filter(activity=activity, scheduled_date=sd).order_by('id'))
                            missing = max(0, 2 - len(existing_for_day))
                            # Optional time slots to differentiate records
                            slots = [dtime(9, 0), dtime(15, 0)]
                            used_times = {r.scheduled_time for r in existing_for_day if r.scheduled_time}
                            for _ in range(missing):
                                rec = CleaningRecord(
                                    unit=unit,
                                    activity=activity,
                                    assigned_to=assigned_to,
                                    scheduled_date=sd,
                                    status=status,
                                    notes=notes,
                                )
                                # assign an unused slot if available
                                for t in slots:
                                    if t not in used_times:
                                        rec.scheduled_time = t
                                        used_times.add(t)
                                        break
                                if status in ['COMPLETED', 'VERIFIED']:
                                    rec.completed_date = timezone.now()
                                rec.save()
                                created_records.append(rec)
                        else:
                            rec = CleaningRecord(
                                unit=unit,
                                activity=activity,
                                assigned_to=assigned_to,
                                scheduled_date=sd,
                                status=status,
                                notes=notes,
                            )
                            if status in ['COMPLETED', 'VERIFIED']:
                                rec.completed_date = timezone.now()
                            rec.save()
                            created_records.append(rec)

                    if created_records:
                        messages.success(request, f'Created {len(created_records)} cleaning record(s) for the selected days.')
                        return redirect('cleaning:cleaning_record_list')
                    else:
                        messages.warning(request, 'No records were created from the selected days (may be due to frequency limits or invalid dates).')
                        # Fall through to create single record as configured below

                # Default single-record creation path
                record = form.save(commit=False)
                if request.user.is_assistant():
                    record.assigned_to = request.user
                record.save()
                messages.success(request, f'Cleaning record created successfully for {record.unit.unit_name}.')
                return redirect('cleaning:cleaning_record_detail', pk=record.pk)
            except Exception as e:
                # If we raised a handled validation above, the message already set
                if 'Activity required for calendar selections' not in str(e):
                    messages.error(request, f'Error creating cleaning record: {str(e)}')
    else:
        form = CleaningRecordForm(initial=initial)
        
        # If assistant, make assigned_to field read-only and hidden
        if request.user.is_assistant():
            form.fields['assigned_to'].disabled = True
            form.fields['assigned_to'].initial = request.user
            form.fields['assigned_to'].widget.attrs['style'] = 'display:none;'
    
    context = {
        'form': form,
        'action': 'Create',
        'is_assistant': request.user.is_assistant(),
    }
    return render(request, 'cleaning/cleaning_record_form.html', context)


@login_required
def cleaning_record_update(request, pk):
    """Update an existing cleaning record (Managers and Assistants)"""
    record = get_object_or_404(CleaningRecord, pk=pk)
    
    # Check permissions
    if request.user.is_assistant():
        # Assistants can only edit their own records
        if record.assigned_to != request.user:
            messages.error(request, 'You can only edit your own cleaning records.')
            return redirect('cleaning:cleaning_record_detail', pk=pk)
    elif not request.user.is_manager():
        messages.error(request, 'You do not have permission to edit cleaning records.')
        return redirect('cleaning:cleaning_record_detail', pk=pk)
    
    if not record.can_be_edited():
        messages.error(request, 'This cleaning record cannot be edited.')
        return redirect('cleaning:cleaning_record_detail', pk=pk)
    
    if request.method == 'POST':
        form = CleaningRecordForm(request.POST, instance=record)
        if form.is_valid():
            try:
                updated_record = form.save(commit=False)
                
                # If assistant is editing, ensure assigned_to doesn't change
                if request.user.is_assistant():
                    updated_record.assigned_to = request.user
                
                updated_record.save()
                messages.success(request, 'Cleaning record updated successfully.')
                return redirect('cleaning:cleaning_record_detail', pk=updated_record.pk)
            except Exception as e:
                messages.error(request, f'Error updating cleaning record: {str(e)}')
    else:
        form = CleaningRecordForm(instance=record)
        
        # If assistant, make assigned_to field read-only and hidden
        if request.user.is_assistant():
            form.fields['assigned_to'].disabled = True
            form.fields['assigned_to'].initial = request.user
            form.fields['assigned_to'].widget.attrs['style'] = 'display:none;'
    
    context = {
        'form': form,
        'record': record,
        'action': 'Update',
        'is_assistant': request.user.is_assistant(),
    }
    return render(request, 'cleaning/cleaning_record_form.html', context)


@login_required
def cleaning_record_detail(request, pk):
    """View details of a cleaning record"""
    record = get_object_or_404(
        CleaningRecord.objects.select_related('unit', 'activity', 'assigned_to', 'verified_by'),
        pk=pk
    )
    
    # Check permissions
    if request.user.is_assistant() and record.assigned_to != request.user:
        messages.error(request, 'You can only view your own cleaning records.')
        return redirect('cleaning:cleaning_record_list')
    
    context = {
        'record': record,
    }
    return render(request, 'cleaning/cleaning_record_detail.html', context)


@login_required
def cleaning_record_complete(request, pk):
    """Mark a cleaning record as completed (Assistant only)"""
    record = get_object_or_404(CleaningRecord, pk=pk)
    
    # Check if user is the assigned assistant
    if record.assigned_to != request.user:
        messages.error(request, 'You can only complete your own cleaning tasks.')
        return redirect('cleaning:cleaning_record_detail', pk=pk)
    
    if record.status not in ['PENDING', 'IN_PROGRESS']:
        messages.error(request, 'This cleaning record cannot be marked as completed.')
        return redirect('cleaning:cleaning_record_detail', pk=pk)
    
    if request.method == 'POST':
        form = CleaningCompletionForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save(commit=False)
            record.status = 'COMPLETED'
            record.completed_date = timezone.now()
            record.save()
            messages.success(request, 'Cleaning task marked as completed.')
            return redirect('cleaning:cleaning_record_detail', pk=record.pk)
    else:
        form = CleaningCompletionForm(instance=record)
    
    context = {
        'form': form,
        'record': record,
    }
    return render(request, 'cleaning/cleaning_record_complete.html', context)


@login_required
def cleaning_record_verify(request, pk):
    """Verify a completed cleaning record (Manager only)"""
    record = get_object_or_404(CleaningRecord, pk=pk)
    
    if not request.user.is_manager():
        messages.error(request, 'Only managers can verify cleaning records.')
        return redirect('cleaning:cleaning_record_detail', pk=pk)
    
    if not record.can_be_verified():
        messages.error(request, 'This cleaning record cannot be verified yet.')
        return redirect('cleaning:cleaning_record_detail', pk=pk)
    
    if request.method == 'POST':
        form = CleaningVerificationForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save(commit=False)
            record.status = 'VERIFIED'
            record.verified_by = request.user
            record.verified_date = timezone.now()
            record.save()
            messages.success(request, 'Cleaning record verified successfully.')
            return redirect('cleaning:cleaning_record_detail', pk=record.pk)
    else:
        form = CleaningVerificationForm(instance=record)
    
    context = {
        'form': form,
        'record': record,
    }
    return render(request, 'cleaning/cleaning_record_verify.html', context)


@login_required
def cleaning_record_delete(request, pk):
    """Delete a cleaning record (Manager only)"""
    record = get_object_or_404(CleaningRecord, pk=pk)
    
    if not request.user.is_manager():
        messages.error(request, 'Only managers can delete cleaning records.')
        return redirect('cleaning:cleaning_record_detail', pk=pk)
    
    if request.method == 'POST':
        unit_name = record.unit.unit_name
        record.delete()
        messages.success(request, f'Cleaning record for {unit_name} has been deleted.')
        return redirect('cleaning:cleaning_record_list')
    
    context = {
        'record': record,
    }
    return render(request, 'cleaning/cleaning_record_confirm_delete.html', context)


# ========== Cleaning Activity Views ==========

@login_required
def cleaning_activity_list(request):
    """List all cleaning activities"""
    activities = CleaningActivity.objects.select_related('unit').all()
    
    # Filter by unit if provided
    unit_id = request.GET.get('unit')
    if unit_id:
        activities = activities.filter(unit_id=unit_id)
    
    # Filter by active status
    is_active = request.GET.get('is_active')
    if is_active == 'true':
        activities = activities.filter(is_active=True)
    elif is_active == 'false':
        activities = activities.filter(is_active=False)
    
    units = Unit.objects.filter(is_active=True)
    
    context = {
        'activities': activities,
        'units': units,
        'selected_unit': unit_id,
        'selected_active': is_active,
    }
    return render(request, 'cleaning/cleaning_activity_list.html', context)


@login_required
def cleaning_activity_create(request):
    """Create a new cleaning activity (Manager only)"""
    if not request.user.is_manager():
        messages.error(request, 'Only managers can create cleaning activities.')
        return redirect('cleaning:cleaning_activity_list')
    
    unit_id = request.GET.get('unit')
    unit = None
    if unit_id:
        unit = get_object_or_404(Unit, pk=unit_id)
    
    if request.method == 'POST':
        form = CleaningActivityForm(request.POST, unit=unit)
        if form.is_valid():
            try:
                activity = form.save()
                messages.success(request, f'Cleaning activity "{activity.activity_name}" created successfully.')
                return redirect('cleaning:cleaning_activity_detail', pk=activity.pk)
            except Exception as e:
                messages.error(request, f'Error creating cleaning activity: {str(e)}')
    else:
        form = CleaningActivityForm(unit=unit)
    
    context = {
        'form': form,
        'action': 'Create',
        'unit': unit,
    }
    return render(request, 'cleaning/cleaning_activity_form.html', context)


@login_required
def cleaning_activity_update(request, pk):
    """Update an existing cleaning activity (Manager only)"""
    activity = get_object_or_404(CleaningActivity, pk=pk)
    
    if not request.user.is_manager():
        messages.error(request, 'Only managers can edit cleaning activities.')
        return redirect('cleaning:cleaning_activity_detail', pk=pk)
    
    if request.method == 'POST':
        form = CleaningActivityForm(request.POST, instance=activity)
        if form.is_valid():
            try:
                activity = form.save()
                messages.success(request, 'Cleaning activity updated successfully.')
                return redirect('cleaning:cleaning_activity_detail', pk=activity.pk)
            except Exception as e:
                messages.error(request, f'Error updating cleaning activity: {str(e)}')
    else:
        form = CleaningActivityForm(instance=activity)
    
    context = {
        'form': form,
        'activity': activity,
        'action': 'Update',
    }
    return render(request, 'cleaning/cleaning_activity_form.html', context)


@login_required
def cleaning_activity_detail(request, pk):
    """View details of a cleaning activity"""
    activity = get_object_or_404(
        CleaningActivity.objects.select_related('unit'),
        pk=pk
    )
    
    # Get recent cleaning records for this activity
    recent_records = CleaningRecord.objects.filter(
        activity=activity
    ).select_related('assigned_to', 'verified_by').order_by('-scheduled_date')[:10]
    
    context = {
        'activity': activity,
        'recent_records': recent_records,
    }
    return render(request, 'cleaning/cleaning_activity_detail.html', context)


@login_required
def cleaning_activity_delete(request, pk):
    """Delete a cleaning activity (Manager only)"""
    activity = get_object_or_404(CleaningActivity, pk=pk)
    
    if not request.user.is_manager():
        messages.error(request, 'Only managers can delete cleaning activities.')
        return redirect('cleaning:cleaning_activity_detail', pk=pk)
    
    if request.method == 'POST':
        activity_name = activity.activity_name
        unit_name = activity.unit.unit_name
        activity.delete()
        messages.success(request, f'Cleaning activity "{activity_name}" for {unit_name} has been deleted.')
        return redirect('cleaning:cleaning_activity_list')
    
    context = {
        'activity': activity,
    }
    return render(request, 'cleaning/cleaning_activity_confirm_delete.html', context)


@login_required
def unit_activities_bulk(request, unit_id):
    """Create or edit multiple activities for a unit in one form (Manager only)."""
    if not request.user.is_manager():
        messages.error(request, 'Only managers can manage activities in bulk.')
        return redirect('cleaning:cleaning_activity_list')

    unit = get_object_or_404(Unit, pk=unit_id)

    # Allow ?extra=N to control number of blank forms
    try:
        extra = max(1, min(20, int(request.GET.get('extra', '5'))))
    except ValueError:
        extra = 5

    ActivityFormSet = inlineformset_factory(
        parent_model=Unit,
        model=CleaningActivity,
        fields=['activity_name', 'description', 'frequency', 'is_active', 'special_instructions'],
        extra=extra,
        can_delete=True
    )

    if request.method == 'POST':
        formset = ActivityFormSet(request.POST, instance=unit)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Activities updated successfully.')
            return redirect(f"{redirect('cleaning:cleaning_activity_list').url}?unit={unit.id}")
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        formset = ActivityFormSet(instance=unit)

    context = {
        'unit': unit,
        'formset': formset,
    }
    return render(request, 'cleaning/unit_activities_bulk_form.html', context)


@login_required
def cleaning_activity_create_multiple(request):
    """Create multiple activities under a selected unit in one form (Manager only)."""
    if not request.user.is_manager():
        messages.error(request, 'Only managers can create cleaning activities.')
        return redirect('cleaning:cleaning_activity_list')

    # Units to choose from
    units = Unit.objects.filter(is_active=True)
    selected_unit_id = request.GET.get('unit') or request.POST.get('unit')
    selected_unit = None
    if selected_unit_id:
        try:
            selected_unit = units.get(pk=int(selected_unit_id))
        except (Unit.DoesNotExist, ValueError):
            selected_unit = None

    try:
        extra = max(1, min(20, int(request.GET.get('extra', '5'))))
    except ValueError:
        extra = 5

    ActivityFormSet = modelformset_factory(
        CleaningActivity,
        fields=['activity_name', 'description', 'frequency', 'is_active', 'special_instructions'],
        extra=extra,
        can_delete=False
    )

    if request.method == 'POST':
        if not selected_unit:
            messages.error(request, 'Please select a unit.')
            formset = ActivityFormSet(request.POST, queryset=CleaningActivity.objects.none())
        else:
            formset = ActivityFormSet(request.POST, queryset=CleaningActivity.objects.none())
            if formset.is_valid():
                created = 0
                for form in formset:
                    if not form.has_changed():
                        continue
                    cd = form.cleaned_data
                    name = cd.get('activity_name')
                    if not name:
                        continue
                    obj = form.save(commit=False)
                    obj.unit = selected_unit
                    obj.save()
                    created += 1
                messages.success(request, f'{created} activities created for {selected_unit.get_full_location()}')
                return redirect('cleaning:cleaning_activity_list')
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        formset = ActivityFormSet(queryset=CleaningActivity.objects.none())

    context = {
        'units': units,
        'selected_unit': selected_unit,
        'formset': formset,
    }
    return render(request, 'cleaning/cleaning_activity_create_multiple.html', context)


@login_required
def get_activities_by_unit(request, unit_id):
    """AJAX endpoint to get activities for a specific unit"""
    activities = CleaningActivity.objects.filter(
        unit_id=unit_id,
        is_active=True
    ).values('id', 'activity_name', 'frequency')
    
    return JsonResponse({
        'activities': list(activities)
    })


@login_required
def cleaning_activity_calendar(request, pk, year=None, month=None):
    """Monthly calendar for scheduling an activity according to its frequency"""
    activity = get_object_or_404(CleaningActivity.objects.select_related('unit'), pk=pk)

    # Only managers schedule
    if not request.user.is_manager():
        messages.error(request, 'Only managers can access the scheduling calendar.')
        return redirect('cleaning:cleaning_activity_detail', pk=pk)

    today = timezone.localdate()
    year = int(year) if year else today.year
    month = int(month) if month else today.month

    first_day = date(year, month, 1)
    _, days_in_month = calendar.monthrange(year, month)
    last_day = date(year, month, days_in_month)

    # Anchor for repeating schedules - use activity.created_at as seed if available
    anchor_dt = activity.created_at.date() if hasattr(activity, 'created_at') else first_day
    if anchor_dt > last_day:
        anchor_dt = first_day

    # Helper to decide if a date is expected per frequency
    def expected_dates_for_month():
        expected = {}
        # Define default schedule times
        am_time = dtime(9, 0)
        pm_time = dtime(15, 0)

        d = first_day
        while d <= last_day:
            slots = []
            if activity.frequency == 'TWICE_DAILY':
                slots = [am_time, pm_time]
            elif activity.frequency == 'DAILY':
                slots = [am_time]
            elif activity.frequency == 'EVERY_2_DAYS':
                if (d - anchor_dt).days % 2 == 0:
                    slots = [am_time]
            elif activity.frequency == 'WEEKLY':
                if (d - anchor_dt).days % 7 == 0:
                    slots = [am_time]
            elif activity.frequency == 'BIWEEKLY':
                if (d - anchor_dt).days % 14 == 0:
                    slots = [am_time]
            elif activity.frequency == 'MONTHLY':
                # Occurs once per month near the anchor day
                anchor_dom = min(anchor_dt.day, days_in_month)
                if d.day == anchor_dom:
                    slots = [am_time]

            if slots:
                expected[d] = slots
            d += timedelta(days=1)
        return expected

    expected = expected_dates_for_month()

    # Fetch existing records for this activity in the month
    existing_qs = CleaningRecord.objects.filter(
        activity=activity,
        scheduled_date__gte=first_day,
        scheduled_date__lte=last_day,
    ).values('id', 'scheduled_date', 'scheduled_time', 'status', 'assigned_to_id')

    existing_by_day = {}
    for r in existing_qs:
        sd = r['scheduled_date']
        existing_by_day.setdefault(sd, []).append(r)

    # Build calendar matrix
    cal = calendar.Calendar().monthdatescalendar(year, month)
    month_weeks_data = []
    for week in cal:
        row = []
        for d in week:
            is_current = (d.month == month)
            expected_slots = []
            if d in expected:
                # Convert times to HH:MM strings
                expected_slots = [t.strftime('%H:%M') for t in expected[d]]
            existing_list = []
            if d in existing_by_day:
                # Normalize times to HH:MM strings for easy comparison
                for r in existing_by_day[d]:
                    existing_list.append({
                        'id': r['id'],
                        'status': r['status'],
                        'scheduled_time_str': r['scheduled_time'].strftime('%H:%M') if r['scheduled_time'] else '',
                    })
            row.append({
                'date': d,
                'is_current': is_current,
                'expected_slots': expected_slots,
                'existing': existing_list,
            })
        month_weeks_data.append(row)

    # Prev/next month
    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)

    context = {
        'activity': activity,
        'unit': activity.unit,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'month_weeks': month_weeks_data,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
    }
    return render(request, 'cleaning/cleaning_activity_calendar.html', context)


@login_required
def cleaning_activity_calendar_partial(request, pk):
    """Return a simplified month calendar for an activity (HTML fragment) for embedding."""
    activity = get_object_or_404(CleaningActivity.objects.select_related('unit'), pk=pk)

    today = timezone.localdate()
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except ValueError:
        year, month = today.year, today.month
    lock_nav = request.GET.get('lock') in ('1', 'true', 'yes')

    first_day = date(year, month, 1)
    _, days_in_month = calendar.monthrange(year, month)
    last_day = date(year, month, days_in_month)

    # Existing records for the month
    existing_qs = CleaningRecord.objects.filter(
        activity=activity,
        scheduled_date__gte=first_day,
        scheduled_date__lte=last_day,
    ).values('id', 'scheduled_date', 'status')

    by_day = {}
    for r in existing_qs:
        d = r['scheduled_date']
        lst = by_day.setdefault(d, [])
        lst.append(r)

    # Count completed/verified within month (used to lock MONTHLY marking)
    monthly_completed_count = sum(
        1 for r in CleaningRecord.objects.filter(
            activity=activity,
            scheduled_date__gte=first_day,
            scheduled_date__lte=last_day,
            status__in=['COMPLETED', 'VERIFIED']
        )
    )

    # Build calendar matrix
    cal = calendar.Calendar().monthdatescalendar(year, month)
    month_weeks = []
    for week in cal:
        row = []
        for d in week:
            if d.month != month:
                row.append({'date': d, 'is_current': False, 'records': [], 'has_completed': False})
                continue
            records = by_day.get(d, [])
            has_completed = any(r['status'] in ('COMPLETED', 'VERIFIED') for r in records)
            completed_count = sum(1 for r in records if r['status'] in ('COMPLETED', 'VERIFIED'))
            row.append({
                'date': d,
                'is_current': True,
                'records': records,
                'has_completed': has_completed,
                'completed_count': completed_count,
            })
        month_weeks.append(row)

    # Determine biweekly anchor date: earliest existing scheduled_date for this activity (global), if any
    earliest = CleaningRecord.objects.filter(activity=activity).order_by('scheduled_date').values_list('scheduled_date', flat=True).first()

    context = {
        'activity': activity,
        'unit': activity.unit,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'month_weeks': month_weeks,
        'lock_nav': lock_nav,
        'monthly_completed_count': monthly_completed_count,
        'anchor_date': earliest,
    }
    return render(request, 'cleaning/partials/activity_calendar_partial.html', context)


@login_required
def mark_activity_completed_day(request, pk):
    """AJAX: Mark a specific day as completed for an activity by creating/updating a record."""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Invalid method'}, status=405)

    if not request.user.is_manager():
        return JsonResponse({'ok': False, 'error': 'Permission denied'}, status=403)

    activity = get_object_or_404(CleaningActivity.objects.select_related('unit'), pk=pk)

    try:
        date_str = request.POST.get('date')
        scheduled_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Invalid date'}, status=400)

    assigned_to_id = request.POST.get('assigned_to')
    assigned_to = None
    if assigned_to_id:
        try:
            assigned_to = get_object_or_404(get_user_model(), pk=int(assigned_to_id))
        except Exception:
            assigned_to = None

    # Frequency-based rules
    # Helper: get month range
    first_day = date(scheduled_date.year, scheduled_date.month, 1)
    _, dim = calendar.monthrange(scheduled_date.year, scheduled_date.month)
    last_day = date(scheduled_date.year, scheduled_date.month, dim)

    # Count existing records for the day/month/week
    day_qs = CleaningRecord.objects.filter(activity=activity, scheduled_date=scheduled_date)
    day_count = day_qs.count()

    month_completed = CleaningRecord.objects.filter(
        activity=activity,
        scheduled_date__gte=first_day,
        scheduled_date__lte=last_day,
        status__in=['COMPLETED', 'VERIFIED']
    ).count()

    # Week calculation (Monday start)
    week_start = scheduled_date - timedelta(days=scheduled_date.weekday())
    week_end = week_start + timedelta(days=6)
    week_completed = CleaningRecord.objects.filter(
        activity=activity,
        scheduled_date__gte=week_start,
        scheduled_date__lte=week_end,
        status__in=['COMPLETED', 'VERIFIED']
    ).count()

    # Anchor for modulo-based schedules
    # For biweekly logic, anchor to earliest existing scheduled_date for this activity if available; otherwise allow first selection to establish anchor
    earliest_existing = CleaningRecord.objects.filter(activity=activity).order_by('scheduled_date').values_list('scheduled_date', flat=True).first()
    anchor_date = earliest_existing or first_day

    freq = activity.frequency
    # Enforce according to frequency
    if freq == 'TWICE_DAILY':
        if day_count >= 2:
            return JsonResponse({'ok': False, 'error': 'Already marked twice for this day.'}, status=400)
    elif freq == 'DAILY':
        if day_count >= 1:
            return JsonResponse({'ok': False, 'error': 'Already marked for this day.'}, status=400)
    elif freq == 'EVERY_2_DAYS':
        # If we have an anchor (earliest existing record), enforce every 2 days from that anchor.
        # If no anchor yet, allow this selection (it will implicitly establish the start date).
        if earliest_existing:
            if ((scheduled_date - anchor_date).days % 2) != 0:
                return JsonResponse({'ok': False, 'error': f'This day is not part of the 2-day cycle starting on {anchor_date}.'}, status=400)
        if day_count >= 1:
            return JsonResponse({'ok': False, 'error': 'Already marked for this day.'}, status=400)
    elif freq == 'WEEKLY':
        # Allow only one per week
        if week_completed >= 1:
            return JsonResponse({'ok': False, 'error': 'Weekly limit reached for this week.'}, status=400)
        if day_count >= 1:
            return JsonResponse({'ok': False, 'error': 'Already marked for this day.'}, status=400)
    elif freq == 'BIWEEKLY':
        # Allow only every 14 days from the start date. If no previous records exist, accept any date (it becomes the start).
        if earliest_existing:
            if ((scheduled_date - anchor_date).days % 14) != 0:
                return JsonResponse({'ok': False, 'error': f'This day is not part of the 14-day cycle starting on {anchor_date}.'}, status=400)
        if day_count >= 1:
            return JsonResponse({'ok': False, 'error': 'Already marked for this day.'}, status=400)
    elif freq == 'MONTHLY':
        # Only one completion per month (any day)
        if month_completed >= 1:
            return JsonResponse({'ok': False, 'error': 'Monthly limit reached for this month.'}, status=400)
        if day_count >= 1:
            return JsonResponse({'ok': False, 'error': 'Already marked for this day.'}, status=400)

    # Create or update the record as completed
    # For TWICE_DAILY, prefer completing an existing non-completed record; otherwise create a new one
    if freq == 'TWICE_DAILY':
        # Try to find an existing non-completed record for this day
        record = day_qs.exclude(status__in=['COMPLETED', 'VERIFIED']).order_by('id').first()
        if not record:
            # Create a new record (second mark)
            record = CleaningRecord(
                unit=activity.unit,
                activity=activity,
                assigned_to=assigned_to or request.user,
                scheduled_date=scheduled_date,
            )
            # Assign a time slot if available to differentiate
            existing_times = set(day_qs.values_list('scheduled_time', flat=True))
            for slot in (dtime(9, 0), dtime(15, 0)):
                if slot not in existing_times:
                    record.scheduled_time = slot
                    break
        else:
            if assigned_to and not record.assigned_to:
                record.assigned_to = assigned_to

        record.status = 'COMPLETED'
        record.completed_date = timezone.now()
        record.save()
        return JsonResponse({'ok': True, 'record_id': record.id, 'status': record.status})

    # Default behavior for other frequencies: create or update single record
    record = day_qs.order_by('id').first()
    if not record:
        record = CleaningRecord(
            unit=activity.unit,
            activity=activity,
            assigned_to=assigned_to or request.user,
            scheduled_date=scheduled_date,
        )
    else:
        if assigned_to and not record.assigned_to:
            record.assigned_to = assigned_to

    record.status = 'COMPLETED'
    record.completed_date = timezone.now()
    record.save()
    return JsonResponse({'ok': True, 'record_id': record.id, 'status': record.status})


@login_required
def activity_performance_report(request):
    """Display activity performance report showing actual vs budgeted completion percentages"""
    if not request.user.is_manager():
        messages.error(request, 'Only managers can view performance reports.')
        return redirect('cleaning:cleaning_record_list')
    
    # Get year and month from query params, default to current month
    from datetime import date
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Get optional unit filter
    unit_id = request.GET.get('unit')
    
    # Get all active activities
    activities = CleaningActivity.objects.filter(is_active=True).select_related('unit')
    
    if unit_id:
        activities = activities.filter(unit_id=unit_id)
    
    # Calculate statistics for each activity
    activity_stats = []
    for activity in activities:
        expected = activity.get_expected_completions_for_month(year, month)
        actual = activity.get_actual_completions_for_month(year, month)
        actual_pct = activity.get_completion_percentage_for_month(year, month)
        budgeted_pct = float(activity.budget_percentage)
        variance = activity.get_variance_percentage_for_month(year, month)
        
        activity_stats.append({
            'activity': activity,
            'unit': activity.unit,
            'frequency': activity.get_frequency_display(),
            'expected_completions': expected,
            'actual_completions': actual,
            'actual_percentage': actual_pct,
            'budgeted_percentage': budgeted_pct,
            'variance': variance,
            'variance_class': 'text-success' if variance >= 0 else 'text-danger',
        })
    
    # Sort by unit name then activity name
    activity_stats.sort(key=lambda x: (x['unit'].get_full_location(), x['activity'].activity_name))
    
    # Get list of units for filter
    units = Unit.objects.filter(is_active=True).select_related('zone', 'section')
    
    # Generate month/year options for selection
    from datetime import timedelta
    months = []
    for i in range(12):  # Last 12 months
        d = today.replace(day=1) - timedelta(days=30*i)
        months.append({'year': d.year, 'month': d.month, 'display': d.strftime('%B %Y')})
    
    context = {
        'activity_stats': activity_stats,
        'selected_year': year,
        'selected_month': month,
        'selected_month_display': date(year, month, 1).strftime('%B %Y'),
        'selected_unit': unit_id,
        'units': units,
        'months': months,
    }
    return render(request, 'cleaning/activity_performance_report.html', context)


@login_required
def faculty_cleaning_report(request, faculty_id):
    """Display cleaning details for all units associated with a faculty"""
    if not request.user.is_manager():
        messages.error(request, 'Only managers can view faculty reports.')
        return redirect('cleaning:cleaning_record_list')
    
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    
    # Get year and month from query params, default to current month
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Get all units associated with this faculty
    units = faculty.units.filter(is_active=True).select_related('zone', 'section').prefetch_related('cleaning_activities')
    
    # Prepare data for each unit
    units_data = []
    total_activities = 0
    total_expected = 0
    total_actual = 0
    
    for unit in units:
        activities = unit.cleaning_activities.filter(is_active=True)
        activity_stats = []
        
        unit_expected = 0
        unit_actual = 0
        
        for activity in activities:
            expected = activity.get_expected_completions_for_month(year, month)
            actual = activity.get_actual_completions_for_month(year, month)
            actual_pct = activity.get_completion_percentage_for_month(year, month)
            budgeted_pct = float(activity.budget_percentage)
            variance = activity.get_variance_percentage_for_month(year, month)
            
            activity_stats.append({
                'activity': activity,
                'frequency': activity.get_frequency_display(),
                'expected_completions': expected,
                'actual_completions': actual,
                'actual_percentage': actual_pct,
                'budgeted_percentage': budgeted_pct,
                'variance': variance,
                'variance_class': 'text-success' if variance >= 0 else 'text-danger',
            })
            
            unit_expected += expected
            unit_actual += actual
        
        # Calculate unit-level completion percentage
        unit_completion_pct = round((unit_actual / unit_expected * 100), 2) if unit_expected > 0 else 0
        
        units_data.append({
            'unit': unit,
            'activities': activity_stats,
            'activity_count': activities.count(),
            'total_expected': unit_expected,
            'total_actual': unit_actual,
            'completion_percentage': unit_completion_pct,
        })
        
        total_activities += activities.count()
        total_expected += unit_expected
        total_actual += unit_actual
    
    # Calculate faculty-level statistics
    faculty_completion_pct = round((total_actual / total_expected * 100), 2) if total_expected > 0 else 0
    
    # Generate month/year options for selection
    months = []
    for i in range(12):  # Last 12 months
        d = today.replace(day=1) - timedelta(days=30*i)
        months.append({'year': d.year, 'month': d.month, 'display': d.strftime('%B %Y')})
    
    context = {
        'faculty': faculty,
        'units_data': units_data,
        'selected_year': year,
        'selected_month': month,
        'selected_month_display': date(year, month, 1).strftime('%B %Y'),
        'months': months,
        'total_units': units.count(),
        'total_activities': total_activities,
        'total_expected': total_expected,
        'total_actual': total_actual,
        'faculty_completion_pct': faculty_completion_pct,
    }
    return render(request, 'cleaning/faculty_cleaning_report.html', context)


@login_required
def faculty_list_report(request):
    """List all faculties for cleaning report access"""
    if not request.user.is_manager():
        messages.error(request, 'Only managers can view faculty reports.')
        return redirect('cleaning:cleaning_record_list')
    
    faculties = Faculty.objects.all().order_by('faculty_name')
    
    # Add unit counts to each faculty
    faculties_data = []
    for faculty in faculties:
        unit_count = faculty.units.filter(is_active=True).count()
        activity_count = CleaningActivity.objects.filter(
            unit__faculty=faculty,
            is_active=True
        ).count()
        
        faculties_data.append({
            'faculty': faculty,
            'unit_count': unit_count,
            'activity_count': activity_count,
        })
    
    context = {
        'faculties_data': faculties_data,
    }
    return render(request, 'cleaning/faculty_list_report.html', context)




