import requests
import re

BASE = 'http://127.0.0.1:8001'

# Session for faculty
s = requests.Session()
print('Logging in as faculty...')
resp = s.post(f'{BASE}/login/', data={'username':'faculty','password':'123'})
print('Login status:', resp.status_code)

# Get subjects page to find a batch id
r = s.get(f'{BASE}/teacher/subjects/')
if r.status_code != 200:
    print('Failed to load subjects page', r.status_code)
    print(r.text[:1000])
    raise SystemExit(1)

m = re.search(r'<option value="(\d+)">', r.text)
if not m:
    print('Could not find batch option in subjects page')
    # print a snippet to debug
    print(r.text[:2000])
    raise SystemExit(1)

batch_id = m.group(1)
print('Found batch id:', batch_id)

# Create subject
print('Creating subject...')
resp = s.post(f'{BASE}/teacher/subjects/', data={'name':'AutoTest','code':'AT101','batch':batch_id,'semester':1}, allow_redirects=True)
print('Create subject status:', resp.status_code)

# Create session
print('Creating session...')
# Need subject id. List subjects page again and parse for code
r2 = s.get(f'{BASE}/teacher/subjects/')
sm = re.search(r'<tr>.*?AT101.*?<td.*?>(\d+)</td>', r2.text, re.S)
if sm:
    subject_id = sm.group(1)
    print('Found subject id in table:', subject_id)
else:
    # Fallback: try to extract via inputs or links
    m2 = re.search(r'/teacher/subjects/edit/(\d+)/', r2.text)
    if m2:
        subject_id = m2.group(1)
        print('Found subject id via edit link:', subject_id)
    else:
        # We will try to post with a known code and batch anyway
        print('Could not determine subject id automatically; posting create_session using code and batch')
        subject_id = ''

data = {'subject': subject_id, 'batch': batch_id}
resp = s.post(f'{BASE}/session/create/', data=data, allow_redirects=False)
print('Create session response code:', resp.status_code)
if resp.status_code in (301,302):
    loc = resp.headers.get('Location')
    print('Redirect location:', loc)
    m = re.search(r'/session/([0-9a-fA-F\-]+)/qr/', loc)
    if m:
        session_uuid = m.group(1)
        print('Session UUID:', session_uuid)
    else:
        print('Could not extract session UUID from redirect')
else:
    print('Create session response body preview:', resp.text[:500])

if 'session_uuid' in locals():
    q = s.get(f'{BASE}/api/session/{session_uuid}/qr-data/')
    print('QR data status:', q.status_code, q.text)
    token = q.json().get('qr_data')
    print('Token acquired')

    # Student marks attendance
    s2 = requests.Session()
    l2 = s2.post(f'{BASE}/login/', data={'username':'Anil','password':'123'})
    print('Student login:', l2.status_code)
    mark = s2.post(f'{BASE}/api/mark-attendance/', json={'token': token})
    print('Mark attendance response:', mark.status_code, mark.text)
else:
    print('No session UUID; stopping')

print('Script finished')
