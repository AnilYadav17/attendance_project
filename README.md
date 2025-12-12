# Attendance Management System

A complete Attendance Management System built with Django, MySQL, and QR-code tracking.

## Features

- **Admin**: Manage users, subjects, batches, and view reports.
- **Teacher**: Create attendance sessions, generate QR codes, and monitor live attendance.
- **Student**: Scan QR codes to mark attendance and view history.

## Setup Instructions

1. **Clone the repository** (if applicable) or navigate to the project directory.

2. **Create a Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database**:

   - Create a MySQL database named `attendance_db`.
   - Copy `.env.example` to `.env` and update the credentials:
     ```bash
     cp .env.example .env
     ```

5. **Run Migrations**:

   ```bash
   python manage.py migrate
   ```

6. **Create Superuser**:

   ```bash
   python manage.py createsuperuser
   ```

7. **Run Server**:
   ```bash
   python manage.py runserver
   ```

## Project Structure

- `attendance_project/`: Main project and app directory.
- `templates/`: HTML templates organized by role.
- `static/`: CSS and JS files.
- `media/`: Generated QR codes and uploads.
- `sql/`: Database schema file.

## Usage

1. **Admin**: Log in with superuser credentials to manage the system.
2. **Teacher**: Admin creates teacher accounts. Teachers can then log in to create sessions.
3. **Student**: Admin creates student accounts. Students can log in to scan QR codes.

## Technologies

- Backend: Django
- Database: MySQL
- Frontend: HTML, CSS, JavaScript
- QR Code: `qrcode` (Python), `html5-qrcode` (JS)
- Charts: Chart.js
