# Dean Dashboard - Faculty Reports Integration

## Overview
Updated dean dashboard to link to the existing faculty reports in the cleaning app, with faculty-specific filtering for dean office users.

## Changes Made

### 1. Updated Cleaning App Views

#### `cleaning.views.faculty_list_report`
**Before:** Only managers could access
**After:** Both managers and dean office users can access

**Filtering Logic:**
- **Dean Users:** See only their assigned faculty
- **Managers:** See all faculties
- **Unassigned Deans:** See all faculties (admin view)

#### `cleaning.views.faculty_cleaning_report`
**Before:** Only managers could access individual faculty reports
**After:** Both managers and dean office users can access

**Security:**
- Dean users can only view reports for their assigned faculty
- Attempting to access another faculty's report redirects to faculty list
- Managers have unrestricted access to all faculty reports

### 2. Updated Dean Dashboard Templates

#### Dashboard Header Button
- **Before:** Linked to `dean:faculty_reports` (dean app)
- **After:** Links to `cleaning:faculty_list_report` (cleaning app)
- **Label:** "View Faculty Reports"

#### Navigation Bar
- **Before:** "Reports" link to dean app reports
- **After:** "Faculty Reports" link to cleaning app reports
- **URL:** `/cleaning/reports/faculties/`

### 3. Context Variables Added
Both views now include:
- `is_dean` - Boolean flag indicating if user is dean office

## URL Structure

### Faculty List Report
- **URL:** `/cleaning/reports/faculties/`
- **Access:** Managers and Dean Office users
- **Shows:** List of faculties with unit and activity counts
- **Dean View:** Only shows assigned faculty

### Individual Faculty Report
- **URL:** `/cleaning/reports/faculty/<faculty_id>/`
- **Access:** Managers and Dean Office users
- **Shows:** Detailed cleaning report for specific faculty
- **Features:**
  - Month/year selection
  - Unit-by-unit breakdown
  - Activity statistics (expected vs actual)
  - Budget percentage and variance
  - Completion percentages
- **Dean Security:** Can only access their assigned faculty

## User Experience Flow

### For Dean Office Users:
1. Login → Auto-redirect to dean dashboard
2. Click "View Faculty Reports" button or nav link
3. See only their assigned faculty in the list
4. Click on faculty to view detailed report
5. View monthly cleaning statistics and performance

### For Managers:
1. Login → Auto-redirect to manager dashboard
2. Access reports through cleaning menu or manager reports
3. See all faculties in the list
4. Access any faculty report
5. View all data without restrictions

## Security Features

✅ **Role-Based Access Control**
- Managers: Full access to all faculties
- Dean Office: Access only to assigned faculty
- Assistants: No access to faculty reports

✅ **Faculty Assignment Validation**
- Dean users attempting to access other faculties are redirected
- Error messages inform users of permission issues

✅ **Authentication Required**
- All views require login
- Unauthorized users redirected to login page

## Benefits

1. **Reuses Existing Reports** - No duplication of report logic
2. **Consistent UI** - Dean users see same report format as managers
3. **Faculty-Specific Data** - Automatic filtering for security
4. **Month Selection** - Can view historical data
5. **Detailed Analytics** - Expected vs actual completions, variance analysis

## Files Modified

- `cleaning/views.py`:
  - `faculty_list_report()` - Added dean access and filtering
  - `faculty_cleaning_report()` - Added dean access with security check

- `dean/templates/dean/dashboard.html`:
  - Changed button link from dean app to cleaning app

- `dean/templates/dean/base.html`:
  - Updated nav link from dean reports to cleaning reports

## Testing Checklist

- [ ] Dean user can access faculty list report
- [ ] Dean user sees only assigned faculty
- [ ] Dean user can view detailed faculty report
- [ ] Dean user cannot access other faculties' reports
- [ ] Manager can access all faculties
- [ ] Unassigned dean sees all faculties
- [ ] Proper error messages for unauthorized access
