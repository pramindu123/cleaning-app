from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.apps import apps
import logging

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """Render the Dean Office dashboard.

    We avoid importing models from other apps at module import time to prevent
    circular imports or failures when the `cleaning` app is not available.
    """
    cleaning_operations = []
    try:
        CleaningOperation = apps.get_model('cleaning', 'CleaningOperation')
        # Defensive: only query if model is present
        if CleaningOperation is not None:
            cleaning_operations = CleaningOperation.objects.all()
    except LookupError:
        # Model not available; log and continue with empty data
        logger.debug('cleaning.CleaningOperation model not found; dashboard will show no operations')
    except Exception as exc:
        # Catch unexpected errors to avoid crashing the site on import/checks
        logger.exception('Error fetching CleaningOperation objects: %s', exc)

    context = {
        'user': request.user,
        'cleaning_operations': cleaning_operations,
        'kpis': {
            'completed_tasks': 42,
            'pending_tasks': 8,
            'efficiency': '95%',
        },
    }

    return render(request, 'dean_office/dashboard.html', context)


@login_required
def reports(request):
    """Simple reports page (placeholder).

    Implement real report generation/exporting later. For now return a
    minimal template so {% url 'dean_office:reports' %} resolves.
    """
    context = {
        'user': request.user,
        'reports': [],
    }
    return render(request, 'dean_office/reports.html', context)


@login_required
def kpis(request):
    """Show faculty-wise KPIs: counts of units and active/inactive breakdown."""
    faculty_data = []
    try:
        Faculty = apps.get_model('cleaning', 'Faculty')
        Unit = apps.get_model('cleaning', 'Unit')
        if Faculty is not None:
            for f in Faculty.objects.all().order_by('faculty_name'):
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

    return render(request, 'dean_office/kpis.html', {'faculty_data': faculty_data})


@login_required
def monitoring(request):
    """Monitoring page: list recent units grouped by faculty."""
    faculty_units = []
    try:
        Faculty = apps.get_model('cleaning', 'Faculty')
        Unit = apps.get_model('cleaning', 'Unit')
        if Faculty is not None:
            for f in Faculty.objects.all().order_by('faculty_name'):
                units = Unit.objects.filter(faculty=f).order_by('-created_at')[:20]
                faculty_units.append({'faculty': f, 'units': units})
    except LookupError:
        logger.debug('cleaning.Faculty or Unit model not found; monitoring page will show empty data')
    except Exception:
        logger.exception('Error building monitoring data')

    return render(request, 'dean_office/monitoring.html', {'faculty_units': faculty_units})


@login_required
def templates_view(request):
    """Templates page placeholder: show unit templates / placeholders grouped by faculty."""
    faculty_templates = []
    try:
        Faculty = apps.get_model('cleaning', 'Faculty')
        Unit = apps.get_model('cleaning', 'Unit')
        if Faculty is not None:
            for f in Faculty.objects.all().order_by('faculty_name'):
                units = Unit.objects.filter(faculty=f).order_by('unit_name')
                # For now, treat each unit as having a 'cleaning template' placeholder
                templates = [{'unit': u, 'template_name': f"Default - {u.unit_name}"} for u in units]
                faculty_templates.append({'faculty': f, 'templates': templates})
    except LookupError:
        logger.debug('cleaning.Faculty or Unit model not found; templates page will show empty data')
    except Exception:
        logger.exception('Error building templates data')

    return render(request, 'dean_office/templates_list.html', {'faculty_templates': faculty_templates})