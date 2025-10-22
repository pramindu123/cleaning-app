# USJ Cleaning App

A Django web application for managing cleaning tasks with two user roles: Manager and Assistant.

## Features

- **Custom User Authentication**
  - User registration with role selection (Manager/Assistant)
  - Secure login/logout functionality
  - Role-based dashboard access

- **User Roles**
  - **Manager**: Full access to manage tasks, view reports, and manage team
  - **Assistant**: View assigned tasks and update status

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

5. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   - Open your browser and go to `http://127.0.0.1:8000/`

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
│   └── views.py              # Authentication views
├── templates/                 # HTML templates
│   ├── base.html
│   └── accounts/
│       ├── login.html
│       ├── signup.html
│       └── dashboard.html
├── manage.py
└── requirements.txt
```

## User Model

The custom User model extends Django's AbstractUser and includes:
- `role`: CharField with choices (MANAGER, ASSISTANT)
- Helper methods: `is_manager()`, `is_assistant()`

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
