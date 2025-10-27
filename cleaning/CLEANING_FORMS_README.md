# Cleaning Forms Feature

## Overview
This module provides comprehensive cleaning record management functionality for both Managers and Assistants in the USJ Cleaning App.

## Features

### For Managers
1. **Create Cleaning Records**
   - Assign cleaning tasks to assistants
   - Schedule cleaning date and time
   - Select specific units to be cleaned
   - Add notes and special instructions

2. **Manage Cleaning Records**
   - View all cleaning records
   - Edit pending/in-progress records
   - Delete records if needed
   - Filter records by status, unit, assistant, and date range

3. **Verify Completed Tasks**
   - Review completed cleaning tasks
   - Add verification notes
   - Mark tasks as verified
   - Track quality and completion

### For Assistants
1. **View Assigned Tasks**
   - See all cleaning tasks assigned to them
   - View task details and requirements
   - Check scheduled dates and times

2. **Complete Tasks**
   - Mark tasks as completed
   - Add completion notes and observations
   - Track work progress

3. **Filter Tasks**
   - Filter by status (Pending, In Progress, Completed, Verified)
   - Filter by date range
   - View task history

## Models

### CleaningRecord
- **unit**: The unit to be cleaned (ForeignKey to Unit)
- **assigned_to**: The assistant assigned to the task (ForeignKey to User)
- **verified_by**: The manager who verified the task (ForeignKey to User)
- **status**: Current status (PENDING, IN_PROGRESS, COMPLETED, VERIFIED)
- **scheduled_date**: Date when cleaning is scheduled
 
- **completed_date**: Date and time when cleaning was completed
- **verified_date**: Date and time when cleaning was verified
- **notes**: General notes about the cleaning task
- **verification_notes**: Notes added by manager during verification

## Forms

### CleaningRecordForm
Used by managers to create and update cleaning records.
- Fields: unit, assigned_to, scheduled_date, status, notes
- Filters units to show only active units
- Filters users to show only assistants

### CleaningVerificationForm
Used by managers to verify completed cleaning records.
- Fields: verification_notes
- Required field for quality tracking

### CleaningCompletionForm
Used by assistants to mark tasks as completed.
- Fields: notes
- Optional completion observations

### CleaningRecordFilterForm
Used to filter cleaning records in the list view.
- Fields: status, unit, assigned_to, date_from, date_to
- All fields are optional

## Views

### cleaning_record_list
- Lists all cleaning records with filtering options
- Assistants see only their assigned tasks
- Managers see all tasks

### cleaning_record_create
- Manager-only view to create new cleaning records
- Requires login and manager role

### cleaning_record_update
- Manager-only view to edit existing records
- Only editable if status is PENDING or IN_PROGRESS

### cleaning_record_detail
- View detailed information about a cleaning record
- Assistants can only view their assigned tasks

### cleaning_record_complete
- Assistant-only view to mark tasks as completed
- Only for assigned tasks in PENDING or IN_PROGRESS status

### cleaning_record_verify
- Manager-only view to verify completed tasks
- Only for tasks with COMPLETED status

### cleaning_record_delete
- Manager-only view to delete records
- Requires confirmation

## URL Patterns

```
/cleaning/records/                      - List all cleaning records
/cleaning/records/create/               - Create new record (Manager)
/cleaning/records/<id>/                 - View record details
/cleaning/records/<id>/update/          - Update record (Manager)
/cleaning/records/<id>/delete/          - Delete record (Manager)
/cleaning/records/<id>/complete/        - Complete task (Assistant)
/cleaning/records/<id>/verify/          - Verify task (Manager)
```

## Permissions

### Managers can:
- Create cleaning records
- Edit pending/in-progress records
- Delete records
- Verify completed records
- View all records

### Assistants can:
- View their assigned records
- Mark their tasks as completed
- Add completion notes
- Filter their tasks

## Status Workflow

1. **PENDING** - Initial status when record is created
2. **IN_PROGRESS** - Task is being worked on
3. **COMPLETED** - Assistant has finished cleaning
4. **VERIFIED** - Manager has verified the cleaning quality

## Templates

- `cleaning_record_list.html` - List view with filters
- `cleaning_record_form.html` - Create/Edit form
- `cleaning_record_detail.html` - Detail view
- `cleaning_record_complete.html` - Completion form for assistants
- `cleaning_record_verify.html` - Verification form for managers
- `cleaning_record_confirm_delete.html` - Delete confirmation

## Usage Examples

### Creating a Cleaning Record (Manager)
1. Navigate to `/cleaning/records/`
2. Click "Create New Record"
3. Select unit, assistant, date, and time
4. Add any special instructions in notes
5. Submit the form

### Completing a Task (Assistant)
1. Navigate to `/cleaning/records/`
2. Click on an assigned task
3. Click "Mark as Completed"
4. Add completion notes
5. Submit the form

### Verifying a Task (Manager)
1. Navigate to `/cleaning/records/`
2. Filter by status "Completed"
3. Click on a record
4. Click "Verify Cleaning"
5. Add verification notes
6. Submit the form

## Admin Interface

The CleaningRecord model is registered in the admin interface with:
- List display of key fields
- Search functionality
- Filtering by status, date, and zone
- Bulk actions to mark as completed or verified
- Date hierarchy for easy navigation
