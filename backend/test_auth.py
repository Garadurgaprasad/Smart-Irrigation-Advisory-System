import requests
import json
import time

BASE_URL = 'http://localhost:5001/api/auth'

print('--- Testing Registration ---')
res = requests.post(f'{BASE_URL}/register', json={
    'name': 'Test User',
    'email': 'testuser@agrisense.test',
    'password': 'SuperSecretPassword123!',
    'role': 'farmer'
})
print(f'Status: {res.status_code}, Response: {res.text}')

print('\\n--- Attempting Login Before Verification ---')
res = requests.post(f'{BASE_URL}/login', json={
    'email': 'testuser@agrisense.test',
    'password': 'SuperSecretPassword123!'
})
print(f'Status: {res.status_code}, Response: {res.text}')

print('\\n--- Getting Token from Mock DB ---')
with open('mock_db.json', 'r') as f:
    mock_db = json.load(f)

# Find verification token for our user
token = None
for t, data in mock_db.get('verification_tokens', {}).items():
    user_id = data['user_id']
    if mock_db['users'][user_id]['email'] == 'testuser@agrisense.test':
        token = t
        break

if not token:
    print('COULD NOT FIND TOKEN!')
else:
    print(f'Found token: {token}')
    print('\\n--- Verifying Email ---')
    res = requests.post(f'{BASE_URL}/verify-email', json={'token': token})
    print(f'Status: {res.status_code}, Response: {res.text}')

    print('\\n--- Attempting Login After Verification ---')
    session = requests.Session()
    res = session.post(f'{BASE_URL}/login', json={
        'email': 'testuser@agrisense.test',
        'password': 'SuperSecretPassword123!'
    })
    print(f'Status: {res.status_code}, Response: {res.text}')
    print(f'Cookies Set: {session.cookies.get_dict()}')

    print('\\n--- Fetching /me endpoint with HttpOnly Cookie ---')
    res = session.get(f'{BASE_URL}/me')
    print(f'Status: {res.status_code}, Response: {res.text}')

    print('\\n--- Logging Out ---')
    res = session.post(f'{BASE_URL}/logout')
    print(f'Status: {res.status_code}, Response: {res.text}')
    print(f'Cookies Set: {session.cookies.get_dict()}')
