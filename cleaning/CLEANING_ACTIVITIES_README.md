# Cleaning Activities Feature

## Overview
The Cleaning Activities feature allows managers to define specific cleaning tasks for each unit with different frequencies. This provides more granular control over cleaning operations and helps track specific activities rather than just general cleaning records.

## New Models

### CleaningActivity
Represents specific cleaning tasks that need to be performed for a unit.

**Fields:**
- `unit` - ForeignKey to Unit (required)
- `activity_name` - Name of the activity (e.g., "Sweep floor", "Mop floor", "Clean windows")
- `description` - Detailed description of the activity (optional)
- `frequency` - How often the activity should be performed:
  - **Twice Per Day** - Performed 2 times daily
  - **Daily** - Once per day
  - **Every 2 Days** - Every other day
  - **Weekly** - Once per week
  - **Every 2 Weeks** (Biweekly) - Every two weeks
  - **Monthly** - Once per month
- `is_active` - Whether this activity is currently required
- `special_instructions` - Additional notes or requirements (optional)
- `created_at` - Timestamp when activity was created
- `updated_at` - Timestamp when activity was last updated

**Methods:**
- `get_frequency_per_week()` - Returns how many times per week this activity occurs

**Constraints:**
- `unique_together`: (`unit`, `activity_name`) - Each activity name must be unique within a unit

## Updated Models

### CleaningRecord
Added new optional field:
- `activity` - ForeignKey to CleaningActivity (optional)
  - Links a cleaning record to a specific activity
  - If null, represents general cleaning
  - Uses SET_NULL on delete to preserve historical records

## Forms

### CleaningActivityForm
Form for creating and updating cleaning activities.

**Fields:**
- unit (Select)
- activity_name (Text input)
- description (Textarea)
- frequency (Select)
- is_active (Checkbox)
- special_instructions (Textarea)

**Features:**
- Can pre-populate unit field when creating from unit detail page
- Filters to show only active units
- Displays full location path for units

### Updated CleaningRecordForm
Now includes:
- `activity` field (optional Select)
- Dynamic loading of activities based on selected unit
- JavaScript to fetch and populate activities when unit changes

## Views

### Cleaning Activity Views

1. **cleaning_activity_list**
   - Lists all cleaning activities
   - Filter by unit and active status
   - Accessible to all logged-in users
   - URL: `/cleaning/activities/`

2. **cleaning_activity_create**
   - Create new cleaning activity (Manager only)
   - Can pre-select unit from URL parameter
   - URL: `/cleaning/activities/create/`
   - Optional: `?unit=<unit_id>`

3. **cleaning_activity_update**
   - Edit existing activity (Manager only)
   - URL: `/cleaning/activities/<id>/update/`

4. **cleaning_activity_detail**
   - View activity details
   - Shows recent cleaning records for this activity
   - URL: `/cleaning/activities/<id>/`

5. **cleaning_activity_delete**
   - Delete activity (Manager only)
   - Requires confirmation
   - URL: `/cleaning/activities/<id>/delete/`

### AJAX Endpoint

**get_activities_by_unit**
- Returns JSON list of activities for a specific unit
- Used by cleaning record form to dynamically load activities
- URL: `/cleaning/api/activities/unit/<unit_id>/`
- Returns: `{'activities': [{'id', 'activity_name', 'frequency'}]}`

## Templates

### New Templates
1. **cleaning_activity_list.html**
   - Lists all activities with filtering
   - Shows unit, location, frequency, and status
   - Manager can create new activities

2. **cleaning_activity_form.html**
   - Create/edit form for activities
   - Includes all fields with validation

3. **cleaning_activity_detail.html**
   - Shows full activity details
   - Lists recent cleaning records for the activity
   - Manager can edit, delete, or create cleaning records

4. **cleaning_activity_confirm_delete.html**
   - Confirmation page for deleting activities
   - Shows activity details and warning

### Updated Templates
1. **cleaning_record_form.html**
   - Added activity field
   - Includes JavaScript for dynamic activity loading
   - Activities auto-populate when unit is selected

2. **cleaning_record_detail.html**
   - Shows activity information if present
   - Displays frequency and special instructions

## URL Patterns

```
# Cleaning Activities
/cleaning/activities/                       - List all activities
/cleaning/activities/create/                - Create new activity (Manager)
/cleaning/activities/<id>/                  - View activity details
/cleaning/activities/<id>/update/           - Update activity (Manager)
/cleaning/activities/<id>/delete/           - Delete activity (Manager)

# AJAX
/cleaning/api/activities/unit/<unit_id>/   - Get activities for unit (JSON)
```

## Admin Interface

### CleaningActivity Admin
- List display: activity_name, unit, frequency, is_active, created_at
- Search: activity_name, description, unit name, special_instructions
- Filters: frequency, is_active, created_at, zone
- Bulk actions: Activate/Deactivate activities
- Fieldsets organized by: Basic Info, Schedule, Status & Instructions

### Updated CleaningRecord Admin
- Added activity field to list display and filters
- Activity is searchable

## Workflow Examples

### Creating a Cleaning Activity

1. Navigate to `/cleaning/activities/`
2. Click "Create New Activity"
3. Select the unit
4. Enter activity name (e.g., "Mop floor")
5. Add description (optional)
6. Select frequency (e.g., "Daily")
7. Add special instructions if needed
8. Ensure "Active" is checked
9. Submit

### Creating a Cleaning Record with Activity

1. Navigate to `/cleaning/records/create/`
2. Select a unit
3. Activity dropdown automatically populates with unit's activities
4. Select specific activity or leave as "General cleaning"
5. Select assistant, date, time
6. Add notes if needed
7. Submit

### Viewing Activity Details

1. Navigate to `/cleaning/activities/`
2. Click "View" on any activity
3. See full details including:
   - Activity information
   - Unit location
   - Frequency
   - Special instructions
   - Recent cleaning records for this activity

## Frequency Options Explained

| Frequency | Times per Week | Use Case Example |
|-----------|---------------|------------------|
| Twice Per Day | 14 | High-traffic areas, restrooms |
| Daily | 7 | Regular classrooms, offices |
| Every 2 Days | 3.5 | Low-traffic areas |
| Weekly | 1 | Deep cleaning, windows |
| Every 2 Weeks | 0.5 | Specialized maintenance |
| Monthly | 0.25 | Quarterly-like tasks |

## JavaScript Functionality

The cleaning record form includes JavaScript that:
1. Listens for changes to the unit dropdown
2. Fetches activities for the selected unit via AJAX
3. Populates the activity dropdown with matching activities
4. Shows frequency in activity option text
5. Clears activities when no unit is selected

## Permissions

### Managers Can:
- Create, view, edit, and delete cleaning activities
- View all activities across all units
- Filter and search activities
- Create cleaning records with specific activities

### Assistants Can:
- View cleaning activities
- See activity details in their assigned records
- Filter activities by unit

## Benefits

1. **Granular Tracking** - Track specific tasks, not just "cleaning"
2. **Frequency Management** - Ensure tasks are done at the right frequency
3. **Special Instructions** - Provide task-specific guidance
4. **Reporting** - Generate reports on specific activities
5. **Accountability** - Clear expectations for each task
6. **Scheduling** - Better planning based on frequency requirements

## Integration with Existing System

- Activities are optional - records can still be created without specific activities
- Existing cleaning records remain valid (activity field is nullable)
- Activities enhance but don't replace the general cleaning workflow
- Reports can group by activity or show all cleaning together
