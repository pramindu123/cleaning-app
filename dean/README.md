# Dean Office App

This Django app provides a dashboard for Dean Office users to view and monitor cleaning activities and records for their assigned faculty.

## Features

### Dashboard View
- **Faculty-Specific Data**: Dean office users see data filtered by their assigned faculty
- **Statistics Cards**: 
  - Total Units (with active count)
  - Completed Cleaning Records
  - Verified Cleaning Records
  - Pending Cleaning Records

### Faculty Statistics
- Detailed table showing:
  - Total and active units per faculty
  - Number of cleaning activities
  - Total, completed, and verified records

### Completion Rate
- Visual representation of overall cleaning completion percentage
- Progress bar showing completion status

### Unit Performance
- Table displaying individual unit performance:
  - Unit name and section
  - Total and completed records
  - Completion rate with color-coded progress bars
  - Active/Inactive status

### Recent Cleaning Records
- List of the 10 most recent cleaning records
- Shows unit, activity, assigned assistant, date, and status

### Active Cleaning Activities
- List of active cleaning activities
- Displays activity name, frequency, and associated unit

## User Permissions

Only users with `DEAN_OFFICE` role can access the dean dashboard.

## URL Structure

- `/dean/dashboard/` - Main dean office dashboard

## Templates

- `dean/base.html` - Base template with navigation
- `dean/dashboard.html` - Main dashboard view

## Usage

1. Create a user with `DEAN_OFFICE` role
2. Assign the user to a faculty
3. Login and access `/dean/dashboard/`
4. View faculty-specific cleaning statistics and performance

## Notes

- If a dean office user has no faculty assigned, they will see data for all faculties
- The dashboard automatically filters all data based on the assigned faculty
- Statistics are updated in real-time based on the database state
