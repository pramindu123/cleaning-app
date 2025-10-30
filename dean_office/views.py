from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.apps import apps
import logging
from datetime import datetime, date, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


def _resolve_selected_faculty(FacultyModel, request):
    """Resolve selected faculty from request GET params.

    Accepts either `faculty` (name) or `faculty_id` (numeric id) for
    backwards compatibility. Returns a Faculty instance or None.
    """
    if FacultyModel is None:
        return None
    f_param = request.GET.get('faculty') or request.GET.get('faculty_id')
    if not f_param:
        return None
    # try numeric id first
    try:
        f_id = int(f_param)
        try:
            return FacultyModel.objects.get(pk=f_id)
        except FacultyModel.DoesNotExist:
            return None
    except Exception:
        # treat as name; accept hyphenated slugs too
        name = f_param.replace('-', ' ').strip()
        try:
            return FacultyModel.objects.filter(faculty_name__iexact=name).first()
        except Exception:
            return None


def _faculties_for_user(FacultyModel, user, request):
    """Return (faculties_list, selected_faculty) scoped for the current user.

    - Dean Office users with an associated faculty only see their faculty by default
      and cannot switch to others unless they are staff/superuser.
    - Managers/staff can see all faculties and may filter via GET params.
    - If FacultyModel is missing, returns ([], None).
    """
    if FacultyModel is None:
        return [], None

    try:
        all_faculties = list(FacultyModel.objects.all().order_by('faculty_name'))
    except Exception:
        return [], None

    selected = _resolve_selected_faculty(FacultyModel, request)

    # Restrict dean office users (non-staff) to their own faculty
    try:
        user_role = getattr(user, 'role', None)
        user_faculty = getattr(user, 'faculty', None)
        is_privileged = bool(getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False))
    except Exception:
        user_role = None
        user_faculty = None
        is_privileged = False

    if user_role == 'DEAN_OFFICE' and user_faculty and not is_privileged:
        faculties_scoped = [user_faculty]
        # Force selected to user's faculty, ignore mismatched GET params
        selected = user_faculty
    else:
        faculties_scoped = all_faculties

    return faculties_scoped, selected


def _build_faculty_options(FacultyModel, faculties):
    """Return ordered option dicts for the filter dropdown.

    Each option is a dict: {label, value, faculty_obj}
    - value is the Faculty id (int) when a matching Faculty exists in DB,
      otherwise it's the label string so the name can still be resolved.
    """
    options = []
    if not faculties:
        return options
    # build lookup by lower-cased name for quick matching
    lookup = {}
    try:
        for f in faculties:
            lookup[f.faculty_name.strip().lower()] = f
    except Exception:
        lookup = {}

    for f in faculties:
        name = f.faculty_name.strip()
        key = name.strip().lower()
        faculty_obj = lookup.get(key)
        if faculty_obj:
            value = str(faculty_obj.id)
        else:
            value = name
        options.append({'label': name, 'value': value, 'faculty_obj': faculty_obj})
    return options


@login_required
def dashboard(request):
    """Render the Dean Office dashboard.

    We avoid importing models from other apps at module import time to prevent
    circular imports or failures when the `cleaning` app is not available.
    """
    cleaning_operations = []
    faculties = []
    selected_faculty = None
    # ensure kpis is always defined even if an exception occurs below
    kpis = {}
    # Precompute safe defaults for month context so context build never fails
    now_dt = timezone.localtime(timezone.now()) if hasattr(timezone, 'localtime') else datetime.now()
    year = now_dt.year
    month = now_dt.month
    start_of_month = date(year, month, 1)
    if month == 12:
        end_of_month = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_month = date(year, month + 1, 1) - timedelta(days=1)
    monthly_records = []
    month_stats = {'total': 0, 'pending': 0, 'in_progress': 0, 'completed': 0, 'verified': 0}
    show_faculty_filter = True  # Always initialize before try block

    # Pre-scope for dean users: ensure their own faculty is selected and filter hidden
    try:
        user_role = getattr(request.user, 'role', None)
        user_faculty = getattr(request.user, 'faculty', None)
        is_privileged = bool(getattr(request.user, 'is_superuser', False) or getattr(request.user, 'is_staff', False))
        if user_role == 'DEAN_OFFICE' and user_faculty and not is_privileged:
            faculties = [user_faculty]
            selected_faculty = user_faculty
            show_faculty_filter = False
    except Exception:
        # If anything goes wrong here, fall back to later logic
        pass
    try:
        Faculty = apps.get_model('cleaning', 'Faculty')
        CleaningRecord = apps.get_model('cleaning', 'CleaningRecord')

        # Handle CleaningOperation separately so missing model doesn't block dashboard
        try:
            CleaningOperation = apps.get_model('cleaning', 'CleaningOperation')
            if CleaningOperation is not None:
                cleaning_operations = CleaningOperation.objects.all()
        except LookupError:
            logger.debug('cleaning.CleaningOperation model not found; skipping operations panel')
            cleaning_operations = []
        # get faculties for filter (scoped by user role)
        if Faculty is not None:
            # Only resolve via helper if we haven't already pre-scoped for dean
            if not faculties:
                faculties, selected_faculty = _faculties_for_user(Faculty, request.user, request)
                show_faculty_filter = not (
                    len(faculties) == 1
                    and getattr(request.user, 'role', None) == 'DEAN_OFFICE'
                    and not getattr(request.user, 'is_staff', False)
                    and not getattr(request.user, 'is_superuser', False)
                )
            # Allow GET-based override only when filter is visible (i.e., privileged users)
            if show_faculty_filter and (request.GET.get('faculty') or request.GET.get('faculty_id')):
                selected_faculty_id = request.GET.get('faculty') or request.GET.get('faculty_id')
                try:
                    selected_faculty = Faculty.objects.get(pk=selected_faculty_id)
                    if faculties and selected_faculty not in faculties:
                        selected_faculty = None
                except Faculty.DoesNotExist:
                    selected_faculty = None
        # Filter operations by selected faculty only when applicable and the object supports filtering
        if selected_faculty and hasattr(cleaning_operations, 'filter'):
            cleaning_operations = cleaning_operations.filter(unit__faculty=selected_faculty)

        # Build KPIs dynamically from cleaning models when available
        kpis = {}
        try:
            CleaningActivity = apps.get_model('cleaning', 'CleaningActivity')
            # total activities (tasks) defined for units in the faculty (or overall)
            if CleaningActivity is not None:
                if selected_faculty:
                    total_activities = CleaningActivity.objects.filter(unit__faculty=selected_faculty).count()
                else:
                    total_activities = CleaningActivity.objects.all().count()
            else:
                total_activities = 0

            # records: scheduled/completed/pending counts
            if CleaningRecord is not None:
                qs = CleaningRecord.objects.select_related('unit')
                if selected_faculty:
                    qs = qs.filter(unit__faculty=selected_faculty)
                total_records = qs.count()
                completed = qs.filter(status__in=['COMPLETED', 'VERIFIED']).count()
                pending = qs.filter(status='PENDING').count()
            else:
                total_records = completed = pending = 0

            efficiency = round((completed / total_records) * 100, 2) if total_records else 0

            kpis = {
                'Total Activities': total_activities,
                'Total Records': total_records,
                'Completed Tasks': completed,
                'Pending Tasks': pending,
                'Efficiency': f"{efficiency}%",
            }
        except LookupError:
            logger.debug('cleaning models not available to compute KPIs')
        except Exception:
            logger.exception('Error computing KPIs')

        # Monthly cleaning details for selected faculty
        selected_month_param = request.GET.get('month')  # expected format YYYY-MM
        # Override defaults if a valid month param is present
        try:
            if selected_month_param:
                y_str, m_str = selected_month_param.split('-')
                year = int(y_str)
                month = int(m_str)
                start_of_month = date(year, month, 1)
                if month == 12:
                    end_of_month = date(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_of_month = date(year, month + 1, 1) - timedelta(days=1)
        except Exception:
            # keep defaults
            pass
        if CleaningRecord is not None and selected_faculty is not None:
            # Pull monthly records for the selected faculty within the month range.
            # Use scheduled_date for date filtering and include related FKs for efficiency.
            mqs = CleaningRecord.objects.select_related('unit', 'activity', 'assigned_to')
            mqs = mqs.filter(
                unit__faculty=selected_faculty,
                scheduled_date__gte=start_of_month,
                scheduled_date__lte=end_of_month,
            )
            try:
                logger.debug(
                    "Dean dashboard monthly: faculty_id=%s range=%s..%s count=%s",
                    getattr(selected_faculty, 'id', None), start_of_month, end_of_month, mqs.count()
                )
            except Exception:
                pass
            # Order by date then time
            monthly_records = mqs.order_by('scheduled_date', 'scheduled_time')[:1000]
            month_stats['total'] = mqs.count()
            month_stats['pending'] = mqs.filter(status='PENDING').count()
            month_stats['in_progress'] = mqs.filter(status='IN_PROGRESS').count()
            month_stats['completed'] = mqs.filter(status='COMPLETED').count()
            month_stats['verified'] = mqs.filter(status='VERIFIED').count()
        # Note: We intentionally avoid overriding monthly_records here. It is already
        # built from mqs above using scheduled_date and the selected_faculty scope.
    except LookupError:
        # Some cleaning models not available; continue with whatever sections we built
        logger.debug('One or more cleaning models not found; continuing with partial dashboard')
        show_faculty_filter = True  # Ensure variable is always set
    except Exception as exc:
        # Catch unexpected errors to avoid crashing the site on import/checks
        logger.exception('Error fetching CleaningOperation objects: %s', exc)
        show_faculty_filter = True  # Ensure variable is always set

    context = {
        'user': request.user,
        'cleaning_operations': cleaning_operations,
        'kpis': kpis,
        'faculties': faculties,
        'selected_faculty': selected_faculty,
        'show_faculty_filter': show_faculty_filter,
        'faculty_options': _build_faculty_options(None, faculties),
        'selected_param': request.GET.get('faculty') or request.GET.get('faculty_id'),
        'selected_month': f"{year:04d}-{month:02d}",
        'selected_year': year,
        'selected_month_num': month,
        'monthly_records': monthly_records,
        'month_stats': month_stats,
        'month_range': {'start': start_of_month, 'end': end_of_month},
    }

    return render(request, 'dean_office/dashboard_new_fixed.html', context)


@login_required
def reports(request):
    """Simple reports page (placeholder).

    Implement real report generation/exporting later. For now return a
    minimal template so {% url 'dean_office:reports' %} resolves.
    """
    faculties = []
    selected_faculty = None
    data_rows = []
    try:
        Faculty = apps.get_model('cleaning', 'Faculty')
        CleaningRecord = apps.get_model('cleaning', 'CleaningRecord')
        if Faculty is not None:
            faculties, selected_faculty = _faculties_for_user(Faculty, request.user, request)
        if CleaningRecord is not None:
            qs = CleaningRecord.objects.select_related('unit', 'activity')
            if selected_faculty:
                qs = qs.filter(unit__faculty=selected_faculty)
            data_rows = qs.order_by('-scheduled_date')[:200]
    except LookupError:
        logger.debug('cleaning models not available for reports')
    except Exception:
        logger.exception('Error building reports data')

    context = {
        'user': request.user,
        'reports': data_rows,
        'faculties': faculties,
        'selected_faculty': selected_faculty,
        'faculty_options': _build_faculty_options(None, faculties),
        'selected_param': request.GET.get('faculty') or request.GET.get('faculty_id'),
    }
    return render(request, 'dean_office/reports.html', context)


@login_required
def kpis(request):
    """Show faculty-wise KPIs: counts of units and active/inactive breakdown."""
    faculty_data = []
    faculties = []
    selected_faculty = None
    try:
        Faculty = apps.get_model('cleaning', 'Faculty')
        Unit = apps.get_model('cleaning', 'Unit')
        if Faculty is not None:
            faculties, selected_faculty = _faculties_for_user(Faculty, request.user, request)

            targets = [selected_faculty] if selected_faculty else faculties
            for f in targets:
                units_qs = Unit.objects.filter(faculty=f)
                total = units_qs.count()
                active = units_qs.filter(is_active=True).count()
                inactive = total - active
                percent_active = int((active / total) * 100) if total else 0
                faculty_data.append({
                    'faculty': f,
                    'total_units': total,
                    'active_units': active,
                    'inactive_units': inactive,
                    'percent_active': percent_active,
                })
    except LookupError:
        logger.debug('cleaning.Faculty or Unit model not found; KPIs page will show empty data')
    except Exception:
        logger.exception('Error building faculty KPIs')

    return render(request, 'dean_office/kpis.html', {
        'faculty_data': faculty_data,
        'faculties': faculties,
        'selected_faculty': selected_faculty,
        'faculty_options': _build_faculty_options(None, faculties),
        'selected_param': request.GET.get('faculty') or request.GET.get('faculty_id'),
    })


@login_required
def monitoring(request):
    """Monitoring page: list recent units grouped by faculty."""
    faculty_units = []
    faculties = []
    selected_faculty = None
    try:
        Faculty = apps.get_model('cleaning', 'Faculty')
        Unit = apps.get_model('cleaning', 'Unit')
        if Faculty is not None:
            faculties, selected_faculty = _faculties_for_user(Faculty, request.user, request)

            if selected_faculty:
                units = Unit.objects.filter(faculty=selected_faculty).order_by('-created_at')[:200]
                faculty_units.append({'faculty': selected_faculty, 'units': units})
            else:
                for f in faculties:
                    units = Unit.objects.filter(faculty=f).order_by('-created_at')[:20]
                    faculty_units.append({'faculty': f, 'units': units})
    except LookupError:
        logger.debug('cleaning.Faculty or Unit model not found; monitoring page will show empty data')
    except Exception:
        logger.exception('Error building monitoring data')

    return render(request, 'dean_office/monitoring.html', {
        'faculty_units': faculty_units,
        'faculties': faculties,
        'selected_faculty': selected_faculty,
        'faculty_options': _build_faculty_options(None, faculties),
        'selected_param': request.GET.get('faculty') or request.GET.get('faculty_id'),
    })


@login_required
def templates_view(request):
    """Templates page placeholder: show unit templates / placeholders grouped by faculty."""
    faculty_templates = []
    faculties = []
    selected_faculty = None
    try:
        Faculty = apps.get_model('cleaning', 'Faculty')
        Unit = apps.get_model('cleaning', 'Unit')
        if Faculty is not None:
            faculties, selected_faculty = _faculties_for_user(Faculty, request.user, request)

            targets = [selected_faculty] if selected_faculty else faculties
            for f in targets:
                units = Unit.objects.filter(faculty=f).order_by('unit_name')
                # For now, treat each unit as having a 'cleaning template' placeholder
                templates = [{'unit': u, 'template_name': f"Default - {u.unit_name}"} for u in units]
                faculty_templates.append({'faculty': f, 'templates': templates})
    except LookupError:
        logger.debug('cleaning.Faculty or Unit model not found; templates page will show empty data')
    except Exception:
        logger.exception('Error building templates data')

    return render(request, 'dean_office/templates_list.html', {
        'faculty_templates': faculty_templates,
        'faculties': faculties,
        'selected_faculty': selected_faculty,
        'faculty_options': _build_faculty_options(None, faculties),
        'selected_param': request.GET.get('faculty') or request.GET.get('faculty_id'),
    })