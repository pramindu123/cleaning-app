"""
Dean Office helpers.

This module intentionally avoids declaring Django model classes (to prevent
accidental migrations). Instead it provides a small, defensive helper used by
the dean_office views to build a minimal template context. The helper uses the
app registry to look up models from the `cleaning` app if present, and falls
back to empty/default values when models are missing or queries fail.

Functions:
  - get_dashboard_context(): returns a dict with keys expected by the
	dean_office dashboard template: ``cleaning_operations`` and ``kpis``.

Note: keeping logic here reduces code in views and keeps this app safe to add
to INSTALLED_APPS without creating migrations.
"""

from django.apps import apps
from typing import Dict, List


def get_dashboard_context() -> Dict[str, object]:
	"""Return a minimal context for the dean_office dashboard.

	The function attempts to look up a likely cleaning operation model from
	the `cleaning` app and query a few rows to show on the dashboard. All
	failures are swallowed and replaced with sensible defaults so template
	rendering never raises due to missing models.

	Returns:
		dict: {
			'cleaning_operations': list (queryset list or empty list),
			'kpis': dict (simple KPI values)
		}
	"""

	cleaning_operations: List[object] = []
	kpis: Dict[str, object] = {}

	# Try a few common model names used by cleaning apps. If none exist,
	# leave the lists empty.
	candidate_names = [
		'CleaningOperation',
		'CleaningSchedule',
		'Operation',
		'Cleaning',
	]

	cleaning_model = None
	for name in candidate_names:
		try:
			cleaning_model = apps.get_model('cleaning', name)
			if cleaning_model:
				break
		except LookupError:
			cleaning_model = None

	if cleaning_model is not None:
		try:
			qs = cleaning_model.objects.all()[:10]
			cleaning_operations = list(qs)
			# Simple KPI: total count
			try:
				total = cleaning_model.objects.count()
			except Exception:
				total = len(cleaning_operations)
			kpis['total_operations'] = total
		except Exception:
			cleaning_operations = []
			kpis['total_operations'] = 0
	else:
		kpis['total_operations'] = 0

	return {
		'cleaning_operations': cleaning_operations,
		'kpis': kpis,
	}


