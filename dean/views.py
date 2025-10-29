from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q, Avg
from cleaning.models import Faculty, Unit, CleaningActivity, CleaningRecord
from datetime import datetime, timedelta


def is_dean_office(user):
    """Check if user is from dean office"""
    return user.is_authenticated and user.role == 'DEAN_OFFICE'


@login_required
@user_passes_test(is_dean_office, login_url='login')
def dean_dashboard(request):
    """Dashboard for dean office users showing faculty cleaning details"""
    
    # Get the dean's faculty
    user_faculty = request.user.faculty
    
    if user_faculty:
        # Filter data for dean's specific faculty
        faculties = Faculty.objects.filter(id=user_faculty.id)
        units = Unit.objects.filter(faculty=user_faculty)
    else:
        # If no faculty assigned, show all (for admin purposes)
        faculties = Faculty.objects.all()
        units = Unit.objects.all()
    
    # Faculty statistics with cleaning data
    faculty_stats = faculties.annotate(
        total_units=Count('units'),
        active_units=Count('units', filter=Q(units__is_active=True)),
        total_activities=Count('units__cleaning_activities', distinct=True),
        total_records=Count('units__cleaning_records', distinct=True),
        completed_records=Count('units__cleaning_records', 
                               filter=Q(units__cleaning_records__status='COMPLETED'),
                               distinct=True),
        verified_records=Count('units__cleaning_records',
                              filter=Q(units__cleaning_records__status='VERIFIED'),
                              distinct=True),
    )
    
    # Recent cleaning records for the faculty
    if user_faculty:
        recent_records = CleaningRecord.objects.filter(
            unit__faculty=user_faculty
        ).select_related('unit', 'activity', 'assigned_to').order_by('-completed_date', '-created_at')[:10]
    else:
        recent_records = CleaningRecord.objects.all().select_related(
            'unit', 'activity', 'assigned_to'
        ).order_by('-completed_date', '-created_at')[:10]
    
    # Cleaning activities for the faculty
    if user_faculty:
        activities = CleaningActivity.objects.filter(
            unit__faculty=user_faculty,
            is_active=True
        ).select_related('unit').order_by('unit__unit_name', 'activity_name')[:20]
    else:
        activities = CleaningActivity.objects.filter(
            is_active=True
        ).select_related('unit').order_by('unit__unit_name', 'activity_name')[:20]
    
    # Overall statistics
    total_units = units.count()
    active_units = units.filter(is_active=True).count()
    
    if user_faculty:
        total_activities = CleaningActivity.objects.filter(unit__faculty=user_faculty).count()
        total_records = CleaningRecord.objects.filter(unit__faculty=user_faculty).count()
        completed_count = CleaningRecord.objects.filter(
            unit__faculty=user_faculty, 
            status='COMPLETED'
        ).count()
        verified_count = CleaningRecord.objects.filter(
            unit__faculty=user_faculty,
            status='VERIFIED'
        ).count()
        pending_count = CleaningRecord.objects.filter(
            unit__faculty=user_faculty,
            status='PENDING'
        ).count()
    else:
        total_activities = CleaningActivity.objects.count()
        total_records = CleaningRecord.objects.count()
        completed_count = CleaningRecord.objects.filter(status='COMPLETED').count()
        verified_count = CleaningRecord.objects.filter(status='VERIFIED').count()
        pending_count = CleaningRecord.objects.filter(status='PENDING').count()
    
    # Completion rate
    completion_rate = 0
    if total_records > 0:
        completion_rate = round(((completed_count + verified_count) / total_records) * 100, 1)
    
    # Units by status
    units_by_status = []
    for unit in units.filter(is_active=True)[:15]:
        unit_records = CleaningRecord.objects.filter(unit=unit)
        unit_completed = unit_records.filter(status__in=['COMPLETED', 'VERIFIED']).count()
        unit_total = unit_records.count()
        unit_rate = 0
        if unit_total > 0:
            unit_rate = round((unit_completed / unit_total) * 100, 1)
        
        units_by_status.append({
            'unit': unit,
            'total_records': unit_total,
            'completed': unit_completed,
            'completion_rate': unit_rate
        })
    
    context = {
        'user_faculty': user_faculty,
        'faculty_stats': faculty_stats,
        'recent_records': recent_records,
        'activities': activities,
        'total_units': total_units,
        'active_units': active_units,
        'total_activities': total_activities,
        'total_records': total_records,
        'completed_count': completed_count,
        'verified_count': verified_count,
        'pending_count': pending_count,
        'completion_rate': completion_rate,
        'units_by_status': units_by_status,
    }
    
    return render(request, 'dean/dashboard.html', context)


@login_required
@user_passes_test(is_dean_office, login_url='login')
def faculty_reports(request):
    """Detailed reports for dean's faculty"""
    
    # Get the dean's faculty
    user_faculty = request.user.faculty
    
    if user_faculty:
        # Filter data for dean's specific faculty
        faculties = Faculty.objects.filter(id=user_faculty.id)
        units = Unit.objects.filter(faculty=user_faculty)
    else:
        # If no faculty assigned, show all
        faculties = Faculty.objects.all()
        units = Unit.objects.all()
    
    # Detailed faculty statistics
    faculty_reports = []
    for faculty in faculties:
        faculty_units = Unit.objects.filter(faculty=faculty)
        total_units = faculty_units.count()
        active_units = faculty_units.filter(is_active=True).count()
        
        # Activity stats
        activities = CleaningActivity.objects.filter(unit__faculty=faculty)
        total_activities = activities.count()
        active_activities = activities.filter(is_active=True).count()
        
        # Record stats by status
        records = CleaningRecord.objects.filter(unit__faculty=faculty)
        total_records = records.count()
        pending = records.filter(status='PENDING').count()
        in_progress = records.filter(status='IN_PROGRESS').count()
        completed = records.filter(status='COMPLETED').count()
        verified = records.filter(status='VERIFIED').count()
        
        # Completion rate
        completion_rate = 0
        if total_records > 0:
            completion_rate = round(((completed + verified) / total_records) * 100, 1)
        
        # Activities by frequency
        daily_activities = activities.filter(frequency='DAILY').count()
        weekly_activities = activities.filter(frequency='WEEKLY').count()
        monthly_activities = activities.filter(frequency='MONTHLY').count()
        quarterly_activities = activities.filter(frequency='QUARTERLY').count()
        
        # Unit performance details
        unit_details = []
        for unit in faculty_units:
            unit_records = CleaningRecord.objects.filter(unit=unit)
            unit_total = unit_records.count()
            unit_completed = unit_records.filter(status__in=['COMPLETED', 'VERIFIED']).count()
            unit_pending = unit_records.filter(status='PENDING').count()
            unit_rate = 0
            if unit_total > 0:
                unit_rate = round((unit_completed / unit_total) * 100, 1)
            
            unit_details.append({
                'unit': unit,
                'total_records': unit_total,
                'completed': unit_completed,
                'pending': unit_pending,
                'completion_rate': unit_rate,
                'activities_count': CleaningActivity.objects.filter(unit=unit).count(),
            })
        
        faculty_reports.append({
            'faculty': faculty,
            'total_units': total_units,
            'active_units': active_units,
            'total_activities': total_activities,
            'active_activities': active_activities,
            'total_records': total_records,
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'verified': verified,
            'completion_rate': completion_rate,
            'daily_activities': daily_activities,
            'weekly_activities': weekly_activities,
            'monthly_activities': monthly_activities,
            'quarterly_activities': quarterly_activities,
            'unit_details': unit_details,
        })
    
    context = {
        'user_faculty': user_faculty,
        'faculty_reports': faculty_reports,
    }
    
    return render(request, 'dean/faculty_reports.html', context)

