import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.test import Client

c = Client()

# 1. Scheme list
r = c.get('/api/v1/ps5/schemes/')
assert r.status_code == 200
schemes = r.json()['schemes']
print(f"1. Schemes list OK: {len(schemes)} active schemes returned.")

# 2. Scheme detail
code = schemes[0]['code']
r = c.get(f'/api/v1/ps5/schemes/{code}/')
assert r.status_code == 200
rules_cnt = len(r.json().get('eligibility_rules', []))
docs_cnt = len(r.json().get('required_documents', []))
print(f"2. Scheme detail OK for {code}: rules={rules_cnt}, docs={docs_cnt}")

# 3. Scheme documents
r = c.get(f'/api/v1/ps5/schemes/{code}/documents/')
assert r.status_code == 200
docs_list = r.json().get('required_documents', [])
print(f"3. Scheme documents OK: {len(docs_list)} docs returned.")

# 4. Profile create
r = c.post('/api/v1/ps5/profiles/', json.dumps({
    'display_label': 'Sneha Deshmukh (Sample)',
    'state': 'Maharashtra',
    'district': 'Nashik',
    'caste_category': 'OPEN',
    'annual_household_income_inr': 180000.00,
    'is_maharashtra_domicile': True,
    'is_sample': True,
    'members': [
        {'relation': 'SELF', 'label': 'Sneha', 'age': 20, 'is_student': True, 'annual_income_inr': 0}
    ]
}), content_type='application/json')
assert r.status_code == 201
data = r.json()
profile_ref = data['profile_ref']
token = data['owner_token']
print(f"4. Profile create OK: profile_ref={profile_ref}, token={token[:10]}...")

# 5. Profile detail
r = c.get(f'/api/v1/ps5/profiles/{profile_ref}/', HTTP_X_PROFILE_TOKEN=token)
assert r.status_code == 200
print(f"5. Profile detail OK: label={r.json()['display_label']}, members={len(r.json()['members'])}")

# 6. Application create
r = c.post('/api/v1/ps5/applications/', json.dumps({
    'profile_ref': profile_ref,
    'scheme_code': code,
    'status': 'IN_PROGRESS',
    'reference_note': 'Initial application draft'
}), content_type='application/json', HTTP_X_PROFILE_TOKEN=token)
assert r.status_code == 201
app_ref = r.json()['application_ref']
print(f"6. Application create OK: application_ref={app_ref}")

# 7. Application list
r = c.get(f'/api/v1/ps5/applications/?profile_ref={profile_ref}', HTTP_X_PROFILE_TOKEN=token)
assert r.status_code == 200
print(f"7. Application list OK: {len(r.json()['applications'])} application(s)")

# 8. Application patch
r = c.patch(f'/api/v1/ps5/applications/{app_ref}/', json.dumps({
    'status': 'SUBMITTED',
    'submitted_on': '2026-11-21',
    'notes': 'Submitted via portal'
}), content_type='application/json', HTTP_X_PROFILE_TOKEN=token)
assert r.status_code == 200
print(f"8. Application patch OK: new status={r.json()['status']}, submitted_on={r.json()['submitted_on']}")

# 9. Phase 2 Evaluation: Full scheme evaluation
r = c.post('/api/v1/ps5/evaluations/', json.dumps({
    'profile_ref': profile_ref
}), content_type='application/json', HTTP_X_PROFILE_TOKEN=token)
assert r.status_code == 200
eval_data = r.json()
assert eval_data['profile_ref'] == profile_ref
results = {res['scheme_code']: res for res in eval_data['results']}
print(f"9. Phase 2 Evaluation OK: evaluated {len(results)} schemes.")

# Check likely_eligible for MahaDBT EBC Scholarship
ebc_res = results.get('SAMPLE-MH-EBC-SCHOLARSHIP')
assert ebc_res is not None
assert ebc_res['outcome'] == 'likely_eligible', f"Expected likely_eligible for EBC, got {ebc_res['outcome']}"
print(f"   - SAMPLE-MH-EBC-SCHOLARSHIP: {ebc_res['outcome']} (disclaimer: {ebc_res['disclaimer']})")

# Check not_eligible for Dr. Ambedkar Swadhar (SC only, profile is OPEN)
swadhar_res = results.get('SAMPLE-MH-SWADHAR')
assert swadhar_res is not None
assert swadhar_res['outcome'] == 'not_eligible', f"Expected not_eligible for Swadhar, got {swadhar_res['outcome']}"
assert len(swadhar_res['recommendations']) > 0
print(f"   - SAMPLE-MH-SWADHAR: {swadhar_res['outcome']} (remedy recommendation: '{swadhar_res['recommendations'][0]['text']}')")

# 10. Targeted evaluation by scheme_codes filter
r = c.post('/api/v1/ps5/evaluations/', json.dumps({
    'profile_ref': profile_ref,
    'scheme_codes': ['SAMPLE-MH-EBC-SCHOLARSHIP', 'SAMPLE-MH-SWADHAR']
}), content_type='application/json', HTTP_X_PROFILE_TOKEN=token)
assert r.status_code == 200
filtered_res = r.json()['results']
assert len(filtered_res) == 2
print(f"10. Targeted Scheme Evaluation filter OK: returned {len(filtered_res)} results.")

# 11. Security checks: missing or wrong token returns 404
r_no_tok = c.post('/api/v1/ps5/evaluations/', json.dumps({'profile_ref': profile_ref}), content_type='application/json')
assert r_no_tok.status_code == 404
r_bad_tok = c.post('/api/v1/ps5/evaluations/', json.dumps({'profile_ref': profile_ref}), content_type='application/json', HTTP_X_PROFILE_TOKEN='fake_token')
assert r_bad_tok.status_code == 404
print("11. Evaluation Auth Security OK: missing and wrong tokens rejected with 404.")

print("\nALL PS5 PHASE 1 & 2 ENDPOINTS VERIFIED AND PASSING!")
