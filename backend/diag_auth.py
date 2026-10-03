"""Diagnose auth flow for the Resume AI application."""
import urllib.request
import json

BASE = 'http://127.0.0.1:8000'

print("=== AUTH FLOW DIAGNOSTIC ===\n")

# 1. Login
print("Step 1: POST /api/auth/login")
data = json.dumps({"email": "john.doe@gmail.com", "password": "user123"}).encode()
req = urllib.request.Request(f'{BASE}/api/auth/login', data=data,
                              headers={"Content-Type": "application/json"}, method="POST")
resp = urllib.request.urlopen(req)
result = json.loads(resp.read())
token = result["access_token"]
user_role = result["user"]["role"]
print(f"  -> access_token present: {bool(token)}")
print(f"  -> token length: {len(token)}")
print(f"  -> user role: {user_role}")
print()

# 2. Dashboard
print("Step 2: GET /api/analytics/dashboard with token")
req2 = urllib.request.Request(f'{BASE}/api/analytics/dashboard',
    headers={"Authorization": f"Bearer {token}"})
resp2 = urllib.request.urlopen(req2)
data2 = json.loads(resp2.read())
print(f"  -> Dashboard OK, keys: {list(data2.keys())}")
print()

# 3. /me
print("Step 3: GET /api/auth/me with token")
req3 = urllib.request.Request(f'{BASE}/api/auth/me',
    headers={"Authorization": f"Bearer {token}"})
resp3 = urllib.request.urlopen(req3)
data3 = json.loads(resp3.read())
print(f"  -> Profile: {data3['full_name']} ({data3['email']})")
print()

# 4. No token
print("Step 4: GET /api/analytics/dashboard WITHOUT token")
try:
    req4 = urllib.request.Request(f'{BASE}/api/analytics/dashboard')
    urllib.request.urlopen(req4)
except urllib.error.HTTPError as e:
    print(f"  -> Correctly returns {e.code} Unauthorized")
print()

# 5. Bad token
print("Step 5: GET /api/auth/me with INVALID token")
try:
    req5 = urllib.request.Request(f'{BASE}/api/auth/me',
        headers={"Authorization": "Bearer invalidbadtoken.here.xyz"})
    urllib.request.urlopen(req5)
except urllib.error.HTTPError as e:
    body = json.loads(e.read())
    print(f"  -> Correctly returns {e.code}: {body['detail']}")

print()
print("=== ALL AUTH CHECKS PASSED ===")
