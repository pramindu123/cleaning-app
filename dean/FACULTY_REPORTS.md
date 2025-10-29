# Faculty Reports Feature - Dean Dashboard

## Overview
Added comprehensive faculty reports functionality to the dean dashboard, providing detailed analytics and insights into cleaning operations.

## New Features

### 1. Faculty Reports Page
**URL:** `/dean/reports/`

**Access:** Top-right button on dashboard + Navigation bar link

### Report Sections:

#### Summary Statistics (4 Cards)
- **Total Units** with active count
- **Total Activities** with active count
- **Total Records** with completed count
- **Completion Rate** with visual progress bar

#### Records by Status (4 Cards)
- Pending records count
- In Progress records count
- Completed records count
- Verified records count

#### Activities by Frequency (4 Cards)
- Daily activities count
- Weekly activities count
- Monthly activities count
- Quarterly activities count

#### Unit Performance Details Table
Comprehensive table showing:
- Unit name
- Section and Zone
- Number of activities
- Total records
- Completed count
- Pending count
- Completion rate (with color-coded progress bar)
- Active/Inactive status

### Progress Bar Color Coding
- **Green (≥75%)** - Excellent performance
- **Blue (≥50%)** - Good performance
- **Yellow (≥25%)** - Needs attention
- **Red (<25%)** - Critical attention required

## Navigation

### Dashboard Header
- New button: "View Detailed Reports" (top-right)
- Links to: `/dean/reports/`

### Navigation Bar
- Dashboard link
- **Reports link** (new)
- User profile dropdown

### Reports Page
- "Back to Dashboard" button (top-right)

## Data Filtering

- If dean is assigned to a faculty: Shows only that faculty's data
- If dean has no faculty: Shows all faculties (admin view)

## Usage

1. Login as dean office user
2. From dashboard, click "View Detailed Reports" or "Reports" in nav
3. View comprehensive faculty statistics
4. Analyze unit-level performance
5. Monitor completion rates and activity distribution

## Technical Details

**New View:** `dean.views.faculty_reports`
- Calculates detailed statistics per faculty
- Breaks down records by status
- Categorizes activities by frequency
- Provides unit-level performance metrics

**New Template:** `dean/templates/dean/faculty_reports.html`
- Responsive Bootstrap layout
- Color-coded visual indicators
- Detailed data tables
- Summary cards for quick insights

**Updated Files:**
- `dean/views.py` - Added `faculty_reports` view
- `dean/urls.py` - Added `/reports/` route
- `dean/templates/dean/base.html` - Added Reports nav link
- `dean/templates/dean/dashboard.html` - Added Reports button

## Benefits

1. **Comprehensive Overview** - All statistics in one place
2. **Performance Monitoring** - Track completion rates per unit
3. **Activity Planning** - See frequency distribution
4. **Status Tracking** - Monitor record status breakdown
5. **Data-Driven Decisions** - Visual indicators for priority areas
