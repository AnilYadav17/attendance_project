from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls), # Django Admin
    
    # Auth
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Custom Admin
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/users/', views.manage_users, name='manage_users'),
    path('dashboard/admin/users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('dashboard/admin/attendance/', views.manage_attendance, name='manage_attendance'),
    path('dashboard/admin/attendance/delete/<int:record_id>/', views.delete_attendance_record, name='delete_attendance_record'),
    path('dashboard/admin/batches/', views.manage_batches, name='manage_batches'),
    path('dashboard/admin/batches/edit/<int:batch_id>/', views.edit_batch, name='edit_batch'),
    path('dashboard/admin/report/', views.admin_attendance_report, name='admin_attendance_report'),
    path('dashboard/admin/export/', views.export_reports, name='export_reports'),
    
    # Teacher
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/subjects/', views.manage_subjects, name='manage_subjects'),
    path('teacher/subjects/edit/<int:subject_id>/', views.edit_subject, name='edit_subject'),
    path('session/create/', views.create_session, name='create_session'),
    path('session/<uuid:session_id>/qr/', views.session_qr, name='session_qr'),
    path('session/<uuid:session_id>/manual/', views.manual_attendance, name='manual_attendance'),
    path('api/session/<uuid:session_id>/attendance/', views.get_session_attendance, name='get_session_attendance'),
    path('api/session/<uuid:session_id>/qr-data/', views.get_qr_data, name='get_qr_data'),
    
    # Student
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('scan/', views.scan_qr, name='scan_qr'),
    path('api/mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('history/', views.attendance_history, name='attendance_history'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
