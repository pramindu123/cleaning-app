from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.forms import formset_factory
from accounts.models import User
from cleaning.models import Zone, Section, Faculty, Unit, CleaningActivity
from .forms import ZoneForm, SectionForm, FacultyForm, UnitForm, MonthlyScheduleActivityForm


def is_manager(user):
    """Check if user is a manager"""
    return user.is_authenticated and user.role == 'MANAGER'


@login_required
@user_passes_test(is_manager, login_url='login')
def manager_dashboard(request):
    """Manager dashboard with overview statistics"""
    context = {
        'total_zones': Zone.objects.count(),
        'total_sections': Section.objects.count(),
        'total_faculties': Faculty.objects.count(),
        'total_units': Unit.objects.count(),
        'active_units': Unit.objects.filter(is_active=True).count(),
        'inactive_units': Unit.objects.filter(is_active=False).count(),
        'total_assistants': User.objects.filter(role='ASSISTANT').count(),
        'zones': Zone.objects.all()[:5],  # Latest 5 zones
        'recent_units': Unit.objects.select_related('section', 'faculty').order_by('-created_at')[:10],
    }
    return render(request, 'manager/dashboard.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def zones_list(request):
    """List all zones with their sections and units count"""
    zones = Zone.objects.all().order_by('zone_name')
    context = {
        'zones': zones,
    }
    return render(request, 'manager/zones_list.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def zone_detail(request, zone_id):
    """Detail view of a specific zone"""
    zone = get_object_or_404(Zone, pk=zone_id)
    sections = zone.sections.all().order_by('section_name')
    
    context = {
        'zone': zone,
        'sections': sections,
        'total_sections': sections.count(),
        'total_units': Unit.objects.filter(section__zone=zone).count(),
        'active_units': Unit.objects.filter(section__zone=zone, is_active=True).count(),
    }
    return render(request, 'manager/zone_detail.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def sections_list(request):
    """List all sections"""
    sections = Section.objects.select_related('zone').all().order_by('zone', 'section_name')
    context = {
        'sections': sections,
    }
    return render(request, 'manager/sections_list.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def section_detail(request, section_id):
    """Detail view of a specific section"""
    section = get_object_or_404(Section, pk=section_id)
    units = section.units.select_related('faculty').all().order_by('unit_name')
    
    context = {
        'section': section,
        'units': units,
        'total_units': units.count(),
        'active_units': units.filter(is_active=True).count(),
    }
    return render(request, 'manager/section_detail.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def faculties_list(request):
    """List all faculties"""
    faculties = Faculty.objects.all().order_by('faculty_name')
    context = {
        'faculties': faculties,
    }
    return render(request, 'manager/faculties_list.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def faculty_detail(request, faculty_id):
    """Detail view of a specific faculty"""
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    units = faculty.units.select_related('section', 'section__zone').all().order_by('section__zone', 'section', 'unit_name')
    
    context = {
        'faculty': faculty,
        'units': units,
        'total_units': units.count(),
        'active_units': units.filter(is_active=True).count(),
    }
    return render(request, 'manager/faculty_detail.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def units_list(request):
    """List all units with filtering options"""
    units = Unit.objects.select_related('section', 'section__zone', 'faculty').all()
    
    # Filter by zone
    zone_id = request.GET.get('zone')
    if zone_id:
        units = units.filter(zone_id=zone_id)
    
    # Filter by section
    section_id = request.GET.get('section')
    if section_id:
        units = units.filter(section_id=section_id)
    
    # Filter by faculty
    faculty_id = request.GET.get('faculty')
    if faculty_id:
        units = units.filter(faculty_id=faculty_id)
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'active':
        units = units.filter(is_active=True)
    elif status == 'inactive':
        units = units.filter(is_active=False)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        units = units.filter(
            Q(unit_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    units = units.order_by('zone', 'section', 'unit_name')
    
    context = {
        'units': units,
        'zones': Zone.objects.all(),
        'sections': Section.objects.all(),
        'faculties': Faculty.objects.all(),
        'current_filters': {
            'zone': zone_id,
            'section': section_id,
            'faculty': faculty_id,
            'status': status,
            'search': search_query,
        }
    }
    return render(request, 'manager/units_list.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def unit_detail(request, unit_id):
    """Detail view of a specific unit"""
    unit = get_object_or_404(Unit, pk=unit_id)
    
    context = {
        'unit': unit,
    }
    return render(request, 'manager/unit_detail.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def assistants_list(request):
    """List all assistants"""
    assistants = User.objects.filter(role='ASSISTANT').order_by('username')
    
    context = {
        'assistants': assistants,
    }
    return render(request, 'manager/assistants_list.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def reports(request):
    """Reports and analytics page"""
    # Faculty statistics
    faculty_stats = Faculty.objects.annotate(
        total_units=Count('units'),
        active_units=Count('units', filter=Q(units__is_active=True))
    ).order_by('-total_units')
    
    # Zone statistics
    zone_stats = Zone.objects.annotate(
        total_sections=Count('sections'),
        total_units=Count('sections__units')
    ).order_by('-total_units')
    
    context = {
        'faculty_stats': faculty_stats,
        'zone_stats': zone_stats,
        'total_units': Unit.objects.count(),
        'active_units': Unit.objects.filter(is_active=True).count(),
        'inactive_units': Unit.objects.filter(is_active=False).count(),
    }
    return render(request, 'manager/reports.html', context)


# ============= CRUD Operations for Units =============

@login_required
@user_passes_test(is_manager, login_url='login')
def unit_create(request):
    """Create a new unit"""
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            messages.success(request, f'Unit "{unit.unit_name}" created successfully!')
            return redirect('manager:unit_detail', unit_id=unit.pk)
    else:
        form = UnitForm()
    
    context = {
        'form': form,
        'title': 'Create New Unit',
        'action': 'Create'
    }
    return render(request, 'manager/unit_form.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def unit_update(request, unit_id):
    """Update an existing unit"""
    unit = get_object_or_404(Unit, pk=unit_id)
    
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            unit = form.save()
            messages.success(request, f'Unit "{unit.unit_name}" updated successfully!')
            return redirect('manager:unit_detail', unit_id=unit.pk)
    else:
        form = UnitForm(instance=unit)
    
    context = {
        'form': form,
        'unit': unit,
        'title': f'Edit Unit: {unit.unit_name}',
        'action': 'Update'
    }
    return render(request, 'manager/unit_form.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def unit_delete(request, unit_id):
    """Delete a unit"""
    unit = get_object_or_404(Unit, pk=unit_id)
    
    if request.method == 'POST':
        unit_name = unit.unit_name
        unit.delete()
        messages.success(request, f'Unit "{unit_name}" deleted successfully!')
        return redirect('manager:units_list')
    
    context = {
        'unit': unit,
    }
    return render(request, 'manager/unit_confirm_delete.html', context)


# ============= CRUD Operations for Zones =============

@login_required
@user_passes_test(is_manager, login_url='login')
def zone_create(request):
    """Create a new zone"""
    if request.method == 'POST':
        form = ZoneForm(request.POST)
        if form.is_valid():
            zone = form.save()
            messages.success(request, f'Zone "{zone.zone_name}" created successfully!')
            return redirect('manager:zone_detail', zone_id=zone.pk)
    else:
        form = ZoneForm()
    
    context = {
        'form': form,
        'title': 'Create New Zone',
        'action': 'Create'
    }
    return render(request, 'manager/zone_form.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def zone_update(request, zone_id):
    """Update an existing zone"""
    zone = get_object_or_404(Zone, pk=zone_id)
    
    if request.method == 'POST':
        form = ZoneForm(request.POST, instance=zone)
        if form.is_valid():
            zone = form.save()
            messages.success(request, f'Zone "{zone.zone_name}" updated successfully!')
            return redirect('manager:zone_detail', zone_id=zone.pk)
    else:
        form = ZoneForm(instance=zone)
    
    context = {
        'form': form,
        'zone': zone,
        'title': f'Edit Zone: {zone.zone_name}',
        'action': 'Update'
    }
    return render(request, 'manager/zone_form.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def zone_delete(request, zone_id):
    """Delete a zone"""
    zone = get_object_or_404(Zone, pk=zone_id)
    
    if request.method == 'POST':
        zone_name = zone.zone_name
        zone.delete()
        messages.success(request, f'Zone "{zone_name}" deleted successfully!')
        return redirect('manager:zones_list')
    
    context = {
        'zone': zone,
    }
    return render(request, 'manager/zone_confirm_delete.html', context)


# ============= CRUD Operations for Sections =============

@login_required
@user_passes_test(is_manager, login_url='login')
def section_create(request):
    """Create a new section"""
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save()
            messages.success(request, f'Section "{section.section_name}" created successfully!')
            return redirect('manager:section_detail', section_id=section.pk)
    else:
        form = SectionForm()
    
    context = {
        'form': form,
        'title': 'Create New Section',
        'action': 'Create'
    }
    return render(request, 'manager/section_form.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def section_update(request, section_id):
    """Update an existing section"""
    section = get_object_or_404(Section, pk=section_id)
    
    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            section = form.save()
            messages.success(request, f'Section "{section.section_name}" updated successfully!')
            return redirect('manager:section_detail', section_id=section.pk)
    else:
        form = SectionForm(instance=section)
    
    context = {
        'form': form,
        'section': section,
        'title': f'Edit Section: {section.section_name}',
        'action': 'Update'
    }
    return render(request, 'manager/section_form.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def section_delete(request, section_id):
    """Delete a section"""
    section = get_object_or_404(Section, pk=section_id)
    
    if request.method == 'POST':
        section_name = section.section_name
        section.delete()
        messages.success(request, f'Section "{section_name}" deleted successfully!')
        return redirect('manager:sections_list')
    
    context = {
        'section': section,
    }
    return render(request, 'manager/section_confirm_delete.html', context)


# ============= CRUD Operations for Faculties =============

@login_required
@user_passes_test(is_manager, login_url='login')
def faculty_create(request):
    """Create a new faculty"""
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            faculty = form.save()
            messages.success(request, f'Faculty "{faculty.faculty_name}" created successfully!')
            return redirect('manager:faculty_detail', faculty_id=faculty.pk)
    else:
        form = FacultyForm()
    
    context = {
        'form': form,
        'title': 'Create New Faculty',
        'action': 'Create'
    }
    return render(request, 'manager/faculty_form.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def faculty_update(request, faculty_id):
    """Update an existing faculty"""
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    
    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=faculty)
        if form.is_valid():
            faculty = form.save()
            messages.success(request, f'Faculty "{faculty.faculty_name}" updated successfully!')
            return redirect('manager:faculty_detail', faculty_id=faculty.pk)
    else:
        form = FacultyForm(instance=faculty)
    
    context = {
        'form': form,
        'faculty': faculty,
        'title': f'Edit Faculty: {faculty.faculty_name}',
        'action': 'Update'
    }
    return render(request, 'manager/faculty_form.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def faculty_delete(request, faculty_id):
    """Delete a faculty"""
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    
    if request.method == 'POST':
        faculty_name = faculty.faculty_name
        faculty.delete()
        messages.success(request, f'Faculty "{faculty_name}" deleted successfully!')
        return redirect('manager:faculties_list')
    
    context = {
        'faculty': faculty,
    }
    return render(request, 'manager/faculty_confirm_delete.html', context)


@login_required
@user_passes_test(is_manager, login_url='login')
def unit_schedule_monthly(request, unit_id):
    """Create monthly cleaning schedule for a unit"""
    unit = get_object_or_404(Unit, pk=unit_id)

    # Create a formset for multiple activities
    ActivityFormSet = formset_factory(
        MonthlyScheduleActivityForm,
        extra=1,  # Start with 1 row; users can add more dynamically
        can_delete=False
    )

    if request.method == 'POST':
        formset = ActivityFormSet(request.POST)

        if formset.is_valid():
            created_count = 0
            skipped_count = 0

            for form in formset:
                if form.cleaned_data and form.cleaned_data.get('activity_name'):
                    activity_name = form.cleaned_data['activity_name']

                    # Check if activity already exists for this unit
                    if CleaningActivity.objects.filter(unit=unit, activity_name__iexact=activity_name).exists():
                        skipped_count += 1
                        messages.warning(request, f'Activity "{activity_name}" already exists for this unit. Skipped.')
                        continue

                    # Create the activity
                    activity = form.save(commit=False)
                    activity.unit = unit
                    activity.is_active = True
                    activity.save()
                    created_count += 1

            if created_count > 0:
                messages.success(request, f'{created_count} cleaning activity(ies) added to "{unit.unit_name}" successfully!')

            if skipped_count > 0:
                messages.info(request, f'{skipped_count} duplicate activity(ies) were skipped.')

            if created_count == 0 and skipped_count == 0:
                messages.warning(request, 'No activities were added. Please fill in at least one form.')

            return redirect('manager:unit_detail', unit_id=unit.id)
    else:
        formset = ActivityFormSet()

    # Get existing activities for reference
    existing_activities = CleaningActivity.objects.filter(unit=unit).order_by('activity_name')

    context = {
        'unit': unit,
        'formset': formset,
        'existing_activities': existing_activities,
    }
    return render(request, 'manager/unit_schedule_monthly.html', context)

