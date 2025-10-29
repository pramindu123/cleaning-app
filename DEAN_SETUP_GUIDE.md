# Dean Office User Setup Guide

## Creating a Dean Office User

### Option 1: Using Django Admin

1. Access Django admin at `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Go to "Users" section
4. Click "Add User"
5. Fill in username and password
6. Click "Save and continue editing"
7. In the user details:
   - Set **Role** to "Dean Office"
   - Select a **Faculty** from the dropdown
   - Save the user

### Option 2: Using Django Shell

```python
python manage.py shell

from accounts.models import User
from cleaning.models import Faculty

# Get or create a faculty
faculty = Faculty.objects.first()  # Or create: Faculty.objects.create(faculty_name="Test Faculty")

# Create dean office user
dean_user = User.objects.create_user(
    username='dean_test',
    password='test123',
    email='dean@example.com',
    role='DEAN_OFFICE',
    faculty=faculty
)

print(f"Dean office user created: {dean_user.username}")
print(f"Assigned to faculty: {dean_user.faculty.faculty_name}")
```

### Option 3: Using Signup Form

1. Go to signup page: `http://localhost:8000/signup/`
2. Fill in the form
3. Select "Dean Office" as role
4. Select a faculty from the dropdown
5. Submit the form

## Testing the Dashboard

1. Login with the dean office user credentials
2. You will be automatically redirected to `/dean/dashboard/`
3. The dashboard will show:
   - Statistics for the assigned faculty
   - Unit performance metrics
   - Recent cleaning records
   - Active cleaning activities
   - Overall completion rate

## What You'll See

- **Faculty-Specific Data**: Only data related to the assigned faculty
- **Statistics Cards**: Real-time counts of units and cleaning records
- **Completion Rate**: Visual progress indicator
- **Unit Performance Table**: Individual unit cleaning status
- **Recent Records**: Last 10 cleaning activities
- **Active Activities**: Current cleaning schedule

## Troubleshooting

### "No data available" messages
- Ensure the faculty has units assigned
- Create cleaning activities for the units
- Create cleaning records for testing

### Cannot access dashboard
- Verify user role is set to "DEAN_OFFICE"
- Verify user is assigned to a faculty
- Check login credentials

### Permission denied
- Ensure user is logged in
- Verify role is correctly set in user profile
