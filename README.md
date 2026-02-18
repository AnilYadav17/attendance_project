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

   - Create a MySQL/MariaDB database (e.g. `attendance_db1`).
   - Copy `.env.example` to `.env` and set DB credentials (so they are not hardcoded):
     ```bash
     cp .env.example .env
     ```
     In `.env` set: `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (optional). The database name is fixed to `attendance_db1`.

5. **Run Migrations** (use the safe script to avoid conflicts – see **Migrations** below):

   ```bash
   python manage.py migrate
   ```
   Or run the one-command safe migrator: `./scripts/migrate_safe.sh`

6. **Create Superuser**:

   ```bash
   python manage.py createsuperuser
   ```

7. **Run Server**:
   ```bash
   python manage.py runserver
   ```

## Migrations – avoiding and fixing errors

To avoid **“Conflicting migrations / multiple leaf nodes”** and **“Table already exists”**:

- **Always create new migrations from the latest state**: run `python manage.py migrate` before `makemigrations` so there is only one leaf.
- **Use the safe migrator** (recommended): `./scripts/migrate_safe.sh` – it merges conflicts if needed, then runs migrate.

**If you already see an error:**

1. **“Conflicting migrations detected; multiple leaf nodes”**  
   - Run: `python manage.py makemigrations --merge --noinput`  
   - Then: `python manage.py migrate`

2. **“Table '…' already exists”** (migration was half-applied or DB was created elsewhere)  
   - Mark that migration as applied without running SQL:  
     `python manage.py migrate <app_name> <migration_name> --fake`  
   - Example: `python manage.py migrate attendance_project 0003_notification --fake`  
   - Then run: `python manage.py migrate`

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
