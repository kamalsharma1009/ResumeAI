"""System verification script for Resume AI"""
import urllib.request
import json

BASE = 'http://127.0.0.1:8000'
user_token = None
hr_token = None

print("=== RESUME AI - SYSTEM VERIFICATION ===\n")

# 1. Landing page
try:
    resp = urllib.request.urlopen(f'{BASE}/')
    print(f"[PASS] Landing page (/) -> HTTP {resp.status}")
except Exception as e:
    print(f"[FAIL] Landing page -> {e}")

# 2. Swagger docs
try:
    resp = urllib.request.urlopen(f'{BASE}/docs')
    print(f"[PASS] Swagger API docs (/docs) -> HTTP {resp.status}")
except Exception as e:
    print(f"[FAIL] Swagger docs -> {e}")

# 3. Admin login
try:
    data = json.dumps({"email": "admin@resumeai.com", "password": "admin123"}).encode()
    req = urllib.request.Request(f'{BASE}/api/auth/login', data=data,
                                  headers={"Content-Type": "application/json"}, method="POST")
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    admin_token = result["access_token"]
    print(f"[PASS] Admin login -> Role: {result['user']['role']}")
except Exception as e:
    print(f"[FAIL] Admin login -> {e}")

# 4. HR login
try:
    data = json.dumps({"email": "hr@techcorp.com", "password": "hr123456"}).encode()
    req = urllib.request.Request(f'{BASE}/api/auth/login', data=data,
                                  headers={"Content-Type": "application/json"}, method="POST")
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    hr_token = result["access_token"]
    print(f"[PASS] HR login -> Role: {result['user']['role']}")
except Exception as e:
    print(f"[FAIL] HR login -> {e}")

# 5. User login
try:
    data = json.dumps({"email": "john.doe@gmail.com", "password": "user123"}).encode()
    req = urllib.request.Request(f'{BASE}/api/auth/login', data=data,
                                  headers={"Content-Type": "application/json"}, method="POST")
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    user_token = result["access_token"]
    print(f"[PASS] User login -> Role: {result['user']['role']}")
except Exception as e:
    print(f"[FAIL] User login -> {e}")

# 6. Jobs API
if user_token:
    try:
        req = urllib.request.Request(f'{BASE}/api/jobs',
                                      headers={"Authorization": f"Bearer {user_token}"})
        resp = urllib.request.urlopen(req)
        jobs = json.loads(resp.read())
        print(f"[PASS] Jobs API (/api/jobs) -> {len(jobs)} jobs found")
        for j in jobs:
            print(f"       - {j['title']} @ {j['company']}")
    except Exception as e:
        print(f"[FAIL] Jobs API -> {e}")

# 7. Analytics dashboard
if hr_token:
    try:
        req = urllib.request.Request(f'{BASE}/api/analytics/dashboard',
                                      headers={"Authorization": f"Bearer {hr_token}"})
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        kpi = data.get("kpi", {})
        print(f"[PASS] Analytics dashboard -> Resumes: {kpi.get('total_resumes',0)}, Jobs: {kpi.get('total_jobs',0)}")
    except Exception as e:
        print(f"[FAIL] Analytics dashboard -> {e}")

# 8. Auth /me
if user_token:
    try:
        req = urllib.request.Request(f'{BASE}/api/auth/me',
                                      headers={"Authorization": f"Bearer {user_token}"})
        resp = urllib.request.urlopen(req)
        profile = json.loads(resp.read())
        print(f"[PASS] Auth profile (/api/auth/me) -> {profile['full_name']}")
    except Exception as e:
        print(f"[FAIL] Auth profile -> {e}")

# 9. Resumes listing
if user_token:
    try:
        req = urllib.request.Request(f'{BASE}/api/resumes',
                                      headers={"Authorization": f"Bearer {user_token}"})
        resp = urllib.request.urlopen(req)
        resumes = json.loads(resp.read())
        print(f"[PASS] Resumes API (/api/resumes) -> {len(resumes)} resumes")
    except Exception as e:
        print(f"[FAIL] Resumes API -> {e}")

print("\n=== SERVER RUNNING AT: http://127.0.0.1:8000 ===")
print("    API DOCS AT:        http://127.0.0.1:8000/docs")
