from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.conf import settings
from .models import User, Student, Teacher, Batch, Subject, AttendanceSession, AttendanceRecord, AuditLog
import qrcode
import json
import csv
import uuid
import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.core import signing
import time

# --- Helper Functions ---

def is_admin(user):
    return user.is_superuser

def is_teacher(user):
    return user.is_teacher

def is_student(user):
    return user.is_student

# --- Authentication Views ---

def index_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.is_teacher:
            return redirect('teacher_dashboard')
        elif request.user.is_student:
            return redirect('student_dashboard')
    return render(request, 'index.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index') # Let index handle the redirect based on role

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

def register_view(request):
    batches = Batch.objects.all()
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        roll_number = request.POST.get('roll_number')
        batch_id = request.POST.get('batch')
        
        # Basic Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'register.html', {'batches': batches})
            
        if Student.objects.filter(roll_number=roll_number).exists():
            messages.error(request, 'Roll number already registered')
            return render(request, 'register.html', {'batches': batches})
            
        if not batch_id:
            messages.error(request, 'Please select a batch')
            return render(request, 'register.html', {'batches': batches})
            
        try:
            # Create User
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_student=True
            )
            
            # Create Student Profile
            batch = get_object_or_404(Batch, id=batch_id)
            Student.objects.create(
                user=user,
                roll_number=roll_number,
                batch=batch
            )
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            
    return render(request, 'register.html', {'batches': batches})

# --- Admin Views ---

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_sessions = AttendanceSession.objects.count()
    recent_activity = AuditLog.objects.order_by('-timestamp')[:10]
    
    # Calculate daily attendance for the last 7 days for chart
    from datetime import timedelta
    today = timezone.now().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    
    chart_labels = [day.strftime('%a') for day in last_7_days]
    chart_data = [] # Total attendance records per day
    
    for day in last_7_days:
        count = AttendanceRecord.objects.filter(timestamp__date=day).count()
        chart_data.append(count)

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_sessions': total_sessions,
        'recent_activity': recent_activity,
        'chart_labels': chart_labels,
        'chart_data': chart_data
    }
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def manage_users(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_teacher':
            username = request.POST.get('username')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            else:
                user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email, is_teacher=True)
                Teacher.objects.create(user=user)
                messages.success(request, 'Teacher added successfully')
                
        elif action == 'add_student':
            username = request.POST.get('username')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            roll_number = request.POST.get('roll_number')
            batch_id = request.POST.get('batch')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif Student.objects.filter(roll_number=roll_number).exists():
                messages.error(request, 'Roll number already exists')
            else:
                user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email, is_student=True)
                batch = Batch.objects.get(id=batch_id) if batch_id else None
                Student.objects.create(user=user, roll_number=roll_number, batch=batch)
                messages.success(request, 'Student added successfully')

        elif action == 'delete_user':
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                user.delete()
                messages.success(request, 'User deleted successfully')
            except User.DoesNotExist:
                messages.error(request, 'User not found')
                
        return redirect('manage_users')

    students = Student.objects.select_related('user', 'batch').all()
    teachers = Teacher.objects.select_related('user').prefetch_related('subjects').all()
    batches = Batch.objects.all()
    
    return render(request, 'admin/manage_users.html', {
        'students': students, 
        'teachers': teachers,
        'batches': batches
    })

@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user_to_edit = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user_to_edit.first_name = request.POST.get('first_name')
        user_to_edit.last_name = request.POST.get('last_name')
        user_to_edit.email = request.POST.get('email')
        user_to_edit.save()
        
        if user_to_edit.is_student:
            student_profile = user_to_edit.student_profile
            student_profile.roll_number = request.POST.get('roll_number')
            batch_id = request.POST.get('batch')
            if batch_id:
                student_profile.batch = get_object_or_404(Batch, id=batch_id)
            student_profile.save()
            
        messages.success(request, 'User updated successfully')
        return redirect('manage_users')
        
    batches = Batch.objects.all()
    return render(request, 'admin/edit_user.html', {'target_user': user_to_edit, 'batches': batches})

@login_required
@user_passes_test(is_admin)
def manage_attendance(request):
    sessions = AttendanceSession.objects.select_related('teacher', 'subject', 'batch').order_by('-start_time')
    return render(request, 'admin/manage_attendance.html', {'sessions': sessions})

@login_required
@user_passes_test(is_admin)
def delete_attendance_record(request, record_id):
    if request.method == 'POST':
        record = get_object_or_404(AttendanceRecord, id=record_id)
        record.delete()
        messages.success(request, 'Attendance record deleted')
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

@login_required
@user_passes_test(is_admin)
def manage_batches(request):
    if request.method == 'POST':
        if 'delete' in request.POST:
            batch_id = request.POST.get('batch_id')
            Batch.objects.get(id=batch_id).delete()
            messages.success(request, 'Batch deleted')
        else:
            name = request.POST.get('name')
            year = request.POST.get('year')
            if Batch.objects.filter(name=name).exists():
                messages.error(request, 'Batch name already exists')
            else:
                Batch.objects.create(name=name, year=year)
                messages.success(request, 'Batch created successfully')
        return redirect('manage_batches')
        
    batches = Batch.objects.all().order_by('-year', 'name')
    batches = Batch.objects.all().order_by('-year', 'name')
    return render(request, 'admin/manage_batches.html', {'batches': batches})

@login_required
@user_passes_test(is_admin)
def edit_batch(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        year = request.POST.get('year')
        
        # Check for duplicates excluding current batch
        if Batch.objects.filter(name=name).exclude(id=batch_id).exists():
            messages.error(request, 'Batch name already exists')
        else:
            batch.name = name
            batch.year = year
            batch.save()
            messages.success(request, 'Batch updated successfully')
            return redirect('manage_batches')
            
    return render(request, 'admin/edit_batch.html', {'batch': batch})

def is_teacher_or_admin(user):
    return user.is_superuser or user.is_teacher

@login_required
@user_passes_test(is_teacher_or_admin)
def manage_subjects(request):
    if request.method == 'POST':
        if 'delete' in request.POST:
            subject_id = request.POST.get('subject_id')
            subject = get_object_or_404(Subject, id=subject_id)
            
            # Admin can delete any, Teacher only their own
            if request.user.is_superuser:
                subject.delete()
                messages.success(request, 'Subject deleted')
            elif request.user.teacher_profile in subject.teachers.all():
                subject.delete()
                messages.success(request, 'Subject deleted')
            else:
                messages.error(request, 'You can only delete your own subjects')
        else:
            name = request.POST.get('name')
            code = request.POST.get('code')
            batch_id = request.POST.get('batch')
            
            if Subject.objects.filter(code=code).exists():
                messages.error(request, 'Subject code already exists')
            else:
                batch = get_object_or_404(Batch, id=batch_id)
                subject = Subject.objects.create(name=name, code=code, batch=batch)
                
                # If teacher created, assign to them
                if not request.user.is_superuser:
                    subject.teachers.add(request.user.teacher_profile)
                    
                messages.success(request, 'Subject created successfully')
        return redirect('manage_subjects')
        
    if request.user.is_superuser:
        subjects = Subject.objects.select_related('batch').all()
    else:
        subjects = Subject.objects.filter(teachers=request.user.teacher_profile).select_related('batch')
        
    batches = Batch.objects.all()
    return render(request, 'teacher/manage_subjects.html', {'subjects': subjects, 'batches': batches})

@login_required
@user_passes_test(is_teacher_or_admin)
def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Permission check
    if not request.user.is_superuser and request.user.teacher_profile not in subject.teachers.all():
        messages.error(request, 'You can only edit your own subjects')
        return redirect('manage_subjects')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        batch_id = request.POST.get('batch')
        
        # Check for duplicates excluding current subject
        if Subject.objects.filter(code=code).exclude(id=subject_id).exists():
            messages.error(request, 'Subject code already exists')
        else:
            subject.name = name
            subject.code = code
            subject.batch = get_object_or_404(Batch, id=batch_id)
            subject.save()
            messages.success(request, 'Subject updated successfully')
            return redirect('manage_subjects')
            
    batches = Batch.objects.all()
    return render(request, 'teacher/edit_subject.html', {'subject': subject, 'batches': batches})

@login_required
@user_passes_test(is_admin)
def export_reports(request):
    if request.method == 'POST':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Session ID', 'Teacher', 'Subject', 'Batch', 'Student', 'Status'])
        
        records = AttendanceRecord.objects.select_related('session', 'student', 'session__teacher', 'session__subject', 'session__batch').all()
        
        for record in records:
            writer.writerow([
                record.timestamp,
                record.session.session_id,
                record.session.teacher.user.get_full_name(),
                record.session.subject.name,
                record.session.batch.name,
                record.student.user.get_full_name(),
                record.status
            ])
        
        return response
        return response
    return render(request, 'admin/export_reports.html')

@login_required
@user_passes_test(is_admin)
def admin_attendance_report(request):
    sessions = AttendanceSession.objects.select_related('teacher', 'subject', 'batch').order_by('-start_time')
    batches = Batch.objects.all()
    subjects = Subject.objects.all()
    
    # Filters
    batch_id = request.GET.get('batch')
    subject_id = request.GET.get('subject')
    date_str = request.GET.get('date')
    
    records = AttendanceRecord.objects.select_related('session', 'student__user', 'session__teacher__user', 'session__subject', 'session__batch').all().order_by('-timestamp')
    
    if batch_id:
        records = records.filter(session__batch_id=batch_id)
    if subject_id:
        records = records.filter(session__subject_id=subject_id)
    if date_str:
        records = records.filter(timestamp__date=date_str)
        
    context = {
        'records': records,
        'batches': batches,
        'subjects': subjects,
    }
    return render(request, 'admin/admin_attendance_report.html', context)

# --- Teacher Views ---

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    teacher = request.user.teacher_profile
    active_sessions = AttendanceSession.objects.filter(teacher=teacher, is_active=True)
    past_sessions = AttendanceSession.objects.filter(teacher=teacher, is_active=False).order_by('-start_time')[:5]
    
    # Calculate recent attendance trend for chart
    from datetime import timedelta
    today = timezone.now().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    
    chart_labels = [day.strftime('%a') for day in last_7_days]
    chart_data = []
    
    # Calculate attendance for teacher's sessions only
    for day in last_7_days:
        count = AttendanceRecord.objects.filter(
            session__teacher=teacher,
            timestamp__date=day
        ).count()
        chart_data.append(count)

    # Calculate average attendance rate for this teacher
    total_teacher_sessions = AttendanceSession.objects.filter(teacher=teacher, is_active=False).count()
    overall_attendance_rate = 0
    if total_teacher_sessions > 0:
        total_possible_attendance = 0
        actual_attendance = 0
        sessions = AttendanceSession.objects.filter(teacher=teacher, is_active=False)
        for s in sessions:
            total_possible_attendance += s.batch.students.count()
            actual_attendance += s.records.count()
        
        if total_possible_attendance > 0:
            overall_attendance_rate = round((actual_attendance / total_possible_attendance) * 100, 1)

    return render(request, 'teacher/teacher_dashboard.html', {
        'active_sessions': active_sessions,
        'past_sessions': past_sessions,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'overall_attendance_rate': overall_attendance_rate,
        'total_teacher_sessions': total_teacher_sessions
    })

@login_required
@user_passes_test(is_teacher)
def create_session(request):
    teacher = request.user.teacher_profile
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        batch_id = request.POST.get('batch')
        
        subject = get_object_or_404(Subject, id=subject_id)
        batch = get_object_or_404(Batch, id=batch_id)
        
        session = AttendanceSession.objects.create(
            teacher=teacher,
            subject=subject,
            batch=batch
        )
        
        # Generate QR Code
        qr_data = f"{session.session_id}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to media
        blob = BytesIO()
        img.save(blob, 'PNG')
        file_name = f'qr_{session.session_id}.png'
        
        # Ensure directory exists
        qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        os.makedirs(qr_dir, exist_ok=True)
        
        with open(os.path.join(qr_dir, file_name), 'wb') as f:
            f.write(blob.getvalue())
            
        return redirect('session_qr', session_id=session.session_id)
        
    subjects = teacher.subjects.all()
    batches = Batch.objects.all() # Or filter by what the teacher teaches if that relationship existed
    return render(request, 'teacher/create_session.html', {'subjects': subjects, 'batches': batches})

@login_required
@user_passes_test(is_teacher)
def session_qr(request, session_id):
    session = get_object_or_404(AttendanceSession, session_id=session_id, teacher=request.user.teacher_profile)
    qr_url = f"{settings.MEDIA_URL}qr_codes/qr_{session.session_id}.png"
    
    if request.method == 'POST' and 'end_session' in request.POST:
        session.is_active = False
        session.end_time = timezone.now()
        session.save()
        return redirect('teacher_dashboard')
        
    return render(request, 'teacher/session_qr.html', {'session': session, 'qr_url': qr_url})

@login_required
@user_passes_test(is_teacher)
def get_session_attendance(request, session_id):
    # AJAX endpoint for live updates
    session = get_object_or_404(AttendanceSession, session_id=session_id)
    records = session.records.select_related('student__user').all()
    data = [{'student': r.student.user.get_full_name(), 'timestamp': r.timestamp.strftime('%H:%M:%S')} for r in records]
    return JsonResponse({'attendance': data, 'count': len(data)})

@login_required
@user_passes_test(is_teacher)
def manual_attendance(request, session_id):
    session = get_object_or_404(AttendanceSession, session_id=session_id, teacher=request.user.teacher_profile)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'mark':
            student_id = request.POST.get('student_id')
            student = get_object_or_404(Student, id=student_id)
            
            if student.batch != session.batch:
                messages.error(request, 'Student not in this batch')
            elif AttendanceRecord.objects.filter(session=session, student=student).exists():
                messages.info(request, 'Already marked present')
            else:
                AttendanceRecord.objects.create(session=session, student=student)
                messages.success(request, f'{student.user.get_full_name()} marked present')
                
        elif action == 'unmark':
            record_id = request.POST.get('record_id')
            record = get_object_or_404(AttendanceRecord, id=record_id, session=session)
            record.delete()
            messages.success(request, 'Attendance unmarked')
            
        return redirect('manual_attendance', session_id=session_id)
    
    # Get all students in the batch
    batch_students = Student.objects.filter(batch=session.batch).select_related('user')
    present_students = session.records.select_related('student__user').all()
    present_ids = set(present_students.values_list('student_id', flat=True))
    
    absent_students = [s for s in batch_students if s.id not in present_ids]
    
    return render(request, 'teacher/manual_attendance.html', {
        'session': session,
        'present_students': present_students,
        'absent_students': absent_students
    })

# --- Student Views ---

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    student = request.user.student_profile
    
    # Get total attendance records
    total_attendance = AttendanceRecord.objects.filter(student=student).count()
    
    # Calculate attendance percentage
    # Get total sessions for student's batch
    if student.batch:
        total_sessions = AttendanceSession.objects.filter(
            batch=student.batch,
            is_active=False  # Only count completed sessions
        ).count()
        
        if total_sessions > 0:
            attendance_percentage = round((total_attendance / total_sessions) * 100, 1)
        else:
            attendance_percentage = 0
    else:
        attendance_percentage = 0
    
    # Calculate current streak (consecutive days with attendance)
    from datetime import timedelta
    current_streak = 0
    records = AttendanceRecord.objects.filter(student=student).order_by('-timestamp')
    
    if records.exists():
        current_date = records.first().timestamp.date()
        expected_date = timezone.now().date()
        
        for record in records:
            record_date = record.timestamp.date()
            if record_date == expected_date or record_date == expected_date - timedelta(days=1):
                if record_date < expected_date:
                    current_streak += 1
                    expected_date = record_date
                elif record_date == expected_date:
                    current_streak += 1
                    expected_date = record_date - timedelta(days=1)
            else:
                break
    
    # Calculate attendance for the last 7 days
    today = timezone.now().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    
    chart_labels = [day.strftime('%a') for day in last_7_days]
    chart_data = []
    
    for day in last_7_days:
        count = AttendanceRecord.objects.filter(
            student=student,
            timestamp__date=day
        ).count()
        chart_data.append(count)
    
    context = {
        'total_attendance': total_attendance,
        'attendance_percentage': attendance_percentage,
        'current_streak': current_streak,
        'chart_labels': chart_labels, # Passed as list, will be json_scripted in template
        'chart_data': chart_data,
    }
    
    return render(request, 'student/student_dashboard.html', context)

@login_required
@user_passes_test(is_student)
def scan_qr(request):
    return render(request, 'student/scan_qr.html')

@login_required
@user_passes_test(is_teacher)
def get_qr_data(request, session_id):
    session = get_object_or_404(AttendanceSession, session_id=session_id)
    if not session.is_active:
        return JsonResponse({'status': 'error', 'message': 'Session inactive'})
    
    data = {
        'session_id': str(session.session_id),
        'timestamp': time.time()
    }
    # Sign the data, valid for limited time (validated in mark_attendance)
    token = signing.dumps(data)
    return JsonResponse({'qr_data': token})

@login_required
@user_passes_test(is_student)
def mark_attendance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            
            try:
                # Decrypt and validate token
                # max_age=15 seconds: QR changes every 2s, but give some buffer for scanning/network
                payload = signing.loads(token, max_age=20)
                session_uuid_str = payload['session_id']
                session_uuid = uuid.UUID(session_uuid_str)
            except signing.SignatureExpired:
                 return JsonResponse({'status': 'error', 'message': 'QR Code expired. Scan faster!'})
            except signing.BadSignature:
                 return JsonResponse({'status': 'error', 'message': 'Invalid QR Code'})
            except (ValueError, KeyError):
                 return JsonResponse({'status': 'error', 'message': 'Invalid QR Data'})

            session = get_object_or_404(AttendanceSession, session_id=session_uuid)
            
            if not session.is_active:
                return JsonResponse({'status': 'error', 'message': 'Session has ended'})
            
            student = request.user.student_profile
            
            # Check if student belongs to the batch
            if student.batch != session.batch:
                return JsonResponse({'status': 'error', 'message': 'You are not in this batch'})
            
            # Check if already marked
            if AttendanceRecord.objects.filter(session=session, student=student).exists():
                return JsonResponse({'status': 'info', 'message': 'Attendance already marked'})
            
            AttendanceRecord.objects.create(session=session, student=student)
            
            return JsonResponse({'status': 'success', 'message': 'Attendance marked successfully'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
@user_passes_test(is_student)
def attendance_history(request):
    student = request.user.student_profile
    records = AttendanceRecord.objects.filter(student=student).order_by('-timestamp')
    return render(request, 'student/attendance_history.html', {'records': records})
