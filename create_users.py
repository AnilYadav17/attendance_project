import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from attendance_project.models import Teacher, Student, Batch

User = get_user_model()

print("Creating users...")

# 1. Admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print("✅ Superuser 'admin' created (password: admin)")
else:
    print("ℹ️ Superuser 'admin' already exists.")

# 2. Faculty
if not User.objects.filter(username='faculty').exists():
    faculty_user = User.objects.create_user('faculty', 'faculty@example.com', '123')
    faculty_user.is_teacher = True
    faculty_user.save()
    Teacher.objects.create(user=faculty_user)
    print("✅ Teacher 'faculty' created (password: 123)")
else:
    print("ℹ️ User 'faculty' already exists.")

# 3. Student – ensure a default batch exists (Batch has only name + year, no section)
batch, created = Batch.objects.get_or_create(
    name='B.Tech CSE',
    defaults={'year': 2024}
)

if not User.objects.filter(username='Anil').exists():
    student_user = User.objects.create_user('Anil', 'anil@example.com', '123')
    student_user.is_student = True
    student_user.save()
    Student.objects.create(user=student_user, batch=batch, roll_number='CS101')
    print("✅ Student 'Anil' created (password: 123)")
else:
    print("ℹ️ User 'Anil' already exists.")

print("\n✨ User setup complete!")
