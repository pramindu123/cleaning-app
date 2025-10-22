# USJ Cleaning App

A Django web application for managing cleaning tasks with two user roles (Manager and Assistant) and a comprehensive physical units management system for university facilities.

## Features

### 🔐 User Authentication System
- **Custom User Authentication**
  - User registration with role selection (Manager/Assistant)
  - Secure login/logout functionality
  - Role-based dashboard access

- **User Roles**
  - **Manager**: Full access to manage tasks, view reports, and manage team
  - **Assistant**: View assigned tasks and update status

### 🏢 Physical Units Management (Cleaning App)
- **Hierarchical Structure**
  - **Zones**: Broad campus areas (Main Campus, Medical Campus, Engineering Campus)
  - **Sections**: Buildings within zones (Science Building, Library Block, etc.)
  - **Faculties**: Administrative divisions (Faculty of Science, Arts, Engineering, etc.)
  - **Units**: Specific cleanable areas (Lecture Halls, Labs, Offices, Restrooms, etc.)

- **Entity Relationships**
  - Physical hierarchy: Zone → Section → Unit
  - Administrative hierarchy: Faculty → Unit
  - Units connect both hierarchies as the central entity

- **Features**
  - Active/Inactive status tracking for units under maintenance
  - Floor-based organization
  - Area and capacity tracking
  - Special cleaning notes and requirements
  - 13 different unit types (Lecture Hall, Laboratory, Office, etc.)

## Installation

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Load sample data (optional but recommended):**
   ```bash
   python manage.py load_sample_data
   ```
   
   This will create:
   - 3 Zones (Main, Medical, Engineering Campus)
   - 5 Sections (Buildings)
   - 4 Faculties
   - 13 Units (Lecture halls, labs, offices, etc.)

6. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   - Frontend: `http://127.0.0.1:8000/`
   - Admin Panel: `http://127.0.0.1:8000/admin/`

## Usage

### Sign Up
1. Navigate to the signup page
2. Fill in your details (username, email, first name, last name)
3. Select your role (Manager or Assistant)
4. Create a password
5. Click "Create Account"

### Login
1. Navigate to the login page
2. Enter your username and password
3. Click "Sign In"
4. You'll be redirected to your dashboard

### Dashboard
- View your account information
- See role-specific features and permissions
- Access role-based functionality

### Managing Physical Units (Admin Panel)
1. Log in to admin panel at `http://127.0.0.1:8000/admin/`
2. Navigate to Cleaning section
3. Manage Zones, Sections, Faculties, and Units
4. View hierarchical relationships
5. Activate/deactivate units for maintenance tracking

## Project Structure

```
USJ Cleaning App/
├── cleaning_project/          # Project configuration
│   ├── __init__.py
│   ├── settings.py           # Project settings
│   ├── urls.py               # Main URL configuration
│   ├── asgi.py
│   └── wsgi.py
├── accounts/                  # Authentication app
│   ├── __init__.py
│   ├── admin.py              # Admin configuration
│   ├── apps.py
│   ├── forms.py              # Authentication forms
│   ├── models.py             # Custom User model
│   ├── urls.py               # App URL patterns
│   ├── views.py              # Authentication views
│   └── templates/            # App-level templates
│       ├── base.html
│       └── accounts/
│           ├── login.html
│           ├── signup.html
│           └── dashboard.html
├── cleaning/                  # Physical units management app
│   ├── __init__.py
│   ├── admin.py              # Admin interface for units
│   ├── apps.py
│   ├── models.py             # Zone, Section, Faculty, Unit models
│   ├── urls.py
│   ├── views.py
│   ├── README.md             # Detailed entity documentation
│   ├── sample_data.py        # Sample data script
│   └── management/
│       └── commands/
│           └── load_sample_data.py  # Management command
├── static/                    # Static files (CSS, JS, images)
│   ├── style.css
│   └── favicon.svg
├── manage.py
└── requirements.txt
```

## Data Models

### User Model (accounts app)
The custom User model extends Django's AbstractUser and includes:
- `role`: CharField with choices (MANAGER, ASSISTANT)
- Helper methods: `is_manager()`, `is_assistant()`

### Cleaning Models (cleaning app)

#### 1. Zone
- Broad campus areas
- Fields: name, code, description
- Relationship: One Zone → Many Sections

#### 2. Section  
- Buildings or areas within zones
- Fields: name, code, zone (FK), floor_count, description
- Relationship: One Section → Many Units

#### 3. Faculty
- Administrative divisions
- Fields: name, short_name, code, description
- Relationship: One Faculty → Many Units

#### 4. Unit (Central Entity)
- Specific cleanable areas
- Fields: name, code, section (FK), faculty (FK), unit_type, floor_number, area_sqm, capacity, is_active, notes
- 13 unit types: Lecture Hall, Laboratory, Office, Classroom, Restroom, Corridor, Staircase, Common Area, Cafeteria, Library, Auditorium, Storage, Other
- Connects physical (Zone→Section) and administrative (Faculty) hierarchies

For detailed entity flow documentation, see `cleaning/README.md`

## Admin Panel

Access the admin panel at `http://127.0.0.1:8000/admin/` to:
- Manage users
- View user roles
- Perform administrative tasks

## Security Notes

- Change the SECRET_KEY in settings.py before deployment
- Set DEBUG=False in production
- Configure ALLOWED_HOSTS for production
- Use environment variables for sensitive data

## Next Steps

This project provides the foundation for user authentication. You can extend it by:
- Adding cleaning task models
- Implementing task assignment functionality
- Creating reports and analytics
- Adding API endpoints
- Implementing real-time notifications
