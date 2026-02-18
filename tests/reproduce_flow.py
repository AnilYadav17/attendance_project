import os
import django
import requests
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')
django.setup()

from attendance_project.models import Batch, Subject

BASE = 'http://127.0.0.1:8001'

# Ensure batch exists
batch, _ = Batch.objects.get_or_create(name='B.Tech CSE', year=2024, defaults={'section': 'A'})
print('Using batch id:', batch.id)

# Create users if not present by calling create_users script
print('Running create_users.py to ensure test users...')
import runpy
runpy.run_path('../create_users.py', run_name='__main__')

# 1. Login as faculty and create a subject
s = requests.Session()
login = s.post(f'{BASE}/login/', data={'username': 'faculty', 'password': '123'})
print('Faculty login status code:', login.status_code)

# Create subject
resp = s.post(f'{BASE}/teacher/subjects/', data={'name': 'Test Subject', 'code': 'TS101', 'batch': batch.id, 'semester': 1}, allow_redirects=True)
print('Create subject response code:', resp.status_code)

# Find subject id by fetching subjects page (simple parsing)
r = s.get(f'{BASE}/teacher/subjects/')
if r.status_code != 200:
    print('Failed to list subjects; status:', r.status_code)
    print(r.text[:1000])
    raise SystemExit(1)

# We'll fetch Subject via Django ORM to get id
subject = Subject.objects.filter(code='TS101', batch=batch).first()
if not subject:
    print('Subject was not created; aborting')
    raise SystemExit(1)
print('Subject id:', subject.id)

# Create session
resp = s.post(f'{BASE}/session/create/', data={'subject': subject.id, 'batch': batch.id}, allow_redirects=False)
print('Create session response code:', resp.status_code)
if resp.status_code in (301, 302):
    loc = resp.headers.get('Location')
    print('Redirect to:', loc)
    # If redirected to session QR page, extract session_id from URL
    import re
    m = re.search(r'/session/([0-9a-fA-F\-]+)/qr/', loc)
    if m:
        session_uuid = m.group(1)
        print('Session UUID from redirect:', session_uuid)
    else:
        # Try follow
        r2 = s.get(loc)
        print('Followed redirect, status:', r2.status_code)
else:
    # maybe response contains redirect HTML
    print('Create session response body preview:', resp.text[:500])

# If we have session_uuid, call QR data API
if 'session_uuid' in locals():
    q = s.get(f'{BASE}/api/session/{session_uuid}/qr-data/')
    print('QR data status:', q.status_code, q.text)
    token = q.json().get('qr_data')
    print('Token:', token)

    # Now login as student and mark attendance
    s2 = requests.Session()
    l2 = s2.post(f'{BASE}/login/', data={'username': 'Anil', 'password': '123'})
    print('Student login status:', l2.status_code)
    mark = s2.post(f'{BASE}/api/mark-attendance/', json={'token': token})
    print('Mark attendance response:', mark.status_code, mark.text)
else:
    print('No session UUID; cannot continue')

print('Done')
