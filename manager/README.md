# Manager App

This app provides a comprehensive dashboard and management interface for users with the **Manager** role.

## Features

### 🎯 Manager Dashboard
- **Overview Statistics**
  - Total zones, sections, faculties, and units
  - Active vs inactive units count
  - Total assistants count
  - Recent units created
  - Quick access to zones

### 📍 Zone Management
- **Zones List**: View all zones with section and unit counts
- **Zone Details**: 
  - View all sections within a zone
  - Total sections and units statistics
  - Active units tracking

### 🏢 Section Management
- **Sections List**: View all sections grouped by zone
- **Section Details**:
  - View all units within a section
  - Units grouped by floor number
  - Active/inactive unit statistics

### 🎓 Faculty Management
- **Faculties List**: View all faculties with unit counts
- **Faculty Details**:
  - View all units under faculty responsibility
  - Units grouped by type
  - Active/inactive unit statistics

### 📦 Unit Management
- **Units List** with advanced filtering:
  - Filter by zone
  - Filter by section
  - Filter by faculty
  - Filter by unit type
  - Filter by status (active/inactive)
  - Search by name, code, or description
- **Unit Details**:
  - Complete unit information
  - Physical location hierarchy (Zone → Section → Unit)
  - Administrative responsibility (Faculty)
  - Floor, area, capacity details
  - Special cleaning notes

### 👥 Assistant Management
- **Assistants List**: View all users with Assistant role
- User information and contact details

### 📊 Reports & Analytics
- **Unit Statistics by Type**: Total, active, and inactive counts
- **Faculty Statistics**: Units per faculty with active counts
- **Zone Statistics**: Sections and units per zone
- **Total Area**: Sum of all unit areas (square meters)
- **Total Capacity**: Sum of all unit capacities

## Access Control

All views are protected with:
- `@login_required`: User must be authenticated
- `@user_passes_test(is_manager)`: User must have MANAGER role

Non-manager users attempting to access these views will be redirected to the login page.

## URL Structure

```
/manager/
├── dashboard/                    # Main manager dashboard
├── zones/                        # List all zones
│   └── <zone_id>/               # Zone detail
├── sections/                     # List all sections
│   └── <section_id>/            # Section detail
├── faculties/                    # List all faculties
│   └── <faculty_id>/            # Faculty detail
├── units/                        # List all units (with filters)
│   └── <unit_id>/               # Unit detail
├── assistants/                   # List all assistants
└── reports/                      # Reports and analytics
```

## Views

### Dashboard Views
- `manager_dashboard`: Main overview with statistics

### Entity List Views
- `zones_list`: All zones
- `sections_list`: All sections
- `faculties_list`: All faculties
- `units_list`: All units with filtering
- `assistants_list`: All assistant users

### Detail Views
- `zone_detail`: Specific zone with sections
- `section_detail`: Specific section with units
- `faculty_detail`: Specific faculty with units
- `unit_detail`: Specific unit information

### Analytics Views
- `reports`: Comprehensive reports and statistics

## Integration

### With Accounts App
- Uses `User` model with role checking
- Redirects from general dashboard to manager dashboard for managers
- User authentication and authorization

### With Cleaning App
- Displays and manages all Zone, Section, Faculty, and Unit entities
- Shows relationships between entities
- Provides comprehensive filtering and search

## Templates Structure

```
manager/
└── templates/
    └── manager/
        ├── dashboard.html           # Main dashboard
        ├── zones_list.html          # Zones listing
        ├── zone_detail.html         # Zone details
        ├── sections_list.html       # Sections listing
        ├── section_detail.html      # Section details
        ├── faculties_list.html      # Faculties listing
        ├── faculty_detail.html      # Faculty details
        ├── units_list.html          # Units listing with filters
        ├── unit_detail.html         # Unit details
        ├── assistants_list.html     # Assistants listing
        └── reports.html             # Reports and analytics
```

## Future Enhancements

Potential features to add:
- Task assignment to assistants
- Cleaning schedule management
- Task completion tracking
- Performance analytics per assistant
- Unit inspection history
- Maintenance request management
- Real-time notifications
- Export reports to PDF/Excel
- Calendar view for schedules
- Mobile-responsive design optimization

## Usage Example

1. **Login as Manager**
   ```
   Username: manager1
   Password: [your_password]
   ```

2. **Access Manager Dashboard**
   - After login, you'll be automatically redirected to `/manager/dashboard/`
   - View overview statistics and quick links

3. **Browse Entities**
   - Click on "Zones", "Sections", "Faculties", or "Units" in navigation
   - Use filters and search to find specific items

4. **View Details**
   - Click on any entity to see detailed information
   - Navigate through relationships (Zone → Section → Unit)

5. **Generate Reports**
   - Visit `/manager/reports/` for analytics
   - View statistics by type, faculty, zone
