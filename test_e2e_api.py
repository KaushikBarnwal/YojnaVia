import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent / 'backend'
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.test import Client
import json

c = Client()

print("--- 1. Testing GET /api/v1/profiles/personas/ ---")
res = c.get('/api/v1/profiles/personas/')
assert res.status_code == 200
print(f"Loaded {len(res.json()['personas'])} demo personas.")

print("\n--- 2. Testing POST /api/v1/profiles/load_persona/ (Rohan Gaikwad) ---")
res = c.post('/api/v1/profiles/load_persona/', 
             json.dumps({"persona_key": "rohan_obc", "session_token": "test-session-123"}),
             content_type="application/json")
assert res.status_code == 200
profile = res.json()["profile"]
print(f"Loaded profile: {profile['name']}, income: ₹{profile['annual_family_income']}")

print("\n--- 3. Testing POST /api/v1/eligibility/evaluate/ ---")
res = c.post('/api/v1/eligibility/evaluate/',
             json.dumps({"session_token": "test-session-123"}),
             content_type="application/json")
assert res.status_code == 200
data = res.json()
print(f"Evaluation Summary: {data['summary']}")
print(f"Stacking Bundle: {data['stacking_bundle']['guidance']}")
print(f"Total Package Rupee Value: ₹{data['stacking_bundle']['total_package_value']:,}")

print("\n--- 4. Testing GET /api/v1/documents/dependency_graph/ ---")
res = c.get('/api/v1/documents/dependency_graph/')
assert res.status_code == 200
graph = res.json()
top_doc = graph["top_multiplier_document"]
print(f"Top Multiplier Document: {top_doc['name']} unlocks {top_doc['schemes_count']} schemes (₹{top_doc['total_financial_value_unlocked']:,})")

print("\n--- 5. Testing POST /api/v1/tracker/update/ ---")
res = c.post('/api/v1/tracker/update/',
             json.dumps({
                 "session_token": "test-session-123",
                 "scheme_code": "MH_OBC_POSTMATRIC_2024",
                 "stage": "DOCUMENTS_PREPARATION",
                 "completed_documents": ["DOC_TAHSILDAR_INCOME", "DOC_DOMICILE"],
                 "application_reference_number": "MHDBT-2024-TEST-99"
             }),
             content_type="application/json")
assert res.status_code == 200
rec = res.json()["record"]
print(f"Tracked application: {rec['scheme_code']} at stage {rec['stage']}")
print(f"Next Immediate Action: {rec['next_immediate_action']}")

print("\n--- 6. Testing Conversational Intake POST /api/v1/intake/chat/ ---")
res = c.post('/api/v1/intake/chat/',
             json.dumps({
                 "session_token": "test-session-123",
                 "message": "I am an SC student from Solapur studying civil diploma. Family income 65000."
             }),
             content_type="application/json")
assert res.status_code == 200
intake_data = res.json()
print(f"AI Assistant Reply: {intake_data['reply']}")
print(f"Extracted Profile: {list(intake_data['extracted_profile'].keys())}")

print("\n✅ ALL 6 END-TO-END SYSTEM INTEGRATION TESTS PASSED PERFECTLY!")
