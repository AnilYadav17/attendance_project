from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Batch(models.Model):
    name = models.CharField(max_length=50, unique=True) # e.g., "Class 10 A"
    year = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.year})"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return f"{self.name} ({self.code})"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, related_name='students')
    roll_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.roll_number})"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    subjects = models.ManyToManyField(Subject, related_name='teachers')

    def __str__(self):
        return self.user.get_full_name()

class AttendanceSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.subject.name} - {self.batch.name} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"

class AttendanceRecord(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='Present') # Present, Absent (if needed later)

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.user.username} - {self.session}"

class AuditLog(models.Model):
    action = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"
