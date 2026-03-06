"""
Run this script ONCE to create the Supabase tables.
Uses the Supabase REST API via the anon key + direct HTTP.
"""

import requests
import json

SUPABASE_URL = "https://kdtskvugdhtwjegdegno.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtkdHNrdnVnZGh0d2plZ2RlZ25vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NzIxNTcsImV4cCI6MjA4ODM0ODE1N30.jBUXZ9iH35uw3XGMAE4Gi90BOFkXsO9YEsDSt4iRq48"

# Try to insert a test row into each table to verify they exist.
# If the tables don't exist, we'll get an error and guide the user.

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def check_table(table_name):
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?limit=1"
    r = requests.get(url, headers=headers)
    return r.status_code, r.text

def insert_test_row(table_name, row):
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    r = requests.post(url, headers=headers, json=row)
    return r.status_code, r.text

print("=" * 55)
print("  Haptic-Q: Supabase Table Verification")
print("=" * 55)

# Check each table
tables = {
    "telemetry_logs": {
        "force_applied": 0, "quantum_integrity": 100, "latency_ms": 0,
        "joystick_x": 128, "joystick_y": 128, "socket_active": False,
        "hw_active": False, "breach_detected": False
    },
    "robot_sync_logs": {
        "fsr_value": 0, "joystick_cmd": 128, "hw_active": False
    },
    "breach_events": {
        "reason": "SYSTEM INIT TEST", "severity": "INFO"
    }
}

all_ok = True
for table, row in tables.items():
    code, text = check_table(table)
    if code == 200:
        print(f"  [OK] {table}: EXISTS")
    elif "does not exist" in text or code == 404:
        print(f"  [MISSING] {table}: NOT FOUND -- tables not created yet!")
        all_ok = False
    else:
        print(f"  [WARN] {table}: HTTP {code} -- {text[:80]}")
        all_ok = False

print()
if all_ok:
    # Try inserting a test row into telemetry_logs
    code, text = insert_test_row("telemetry_logs", tables["telemetry_logs"])
    if code in (200, 201):
        print("  [OK] Test row inserted into telemetry_logs -- Supabase fully operational!")
    else:
        print(f"  [WARN] Insert failed (RLS may need setup): HTTP {code} -- {text[:200]}")
    
    code, text = insert_test_row("robot_sync_logs", tables["robot_sync_logs"])
    if code in (200, 201):
        print("  [OK] Test row inserted into robot_sync_logs")
    else:
        print(f"  [WARN] robot_sync_logs insert: HTTP {code} -- {text[:200]}")
    
    code, text = insert_test_row("breach_events", tables["breach_events"])
    if code in (200, 201):
        print("  [OK] Test row inserted into breach_events")
    else:
        print(f"  [WARN] breach_events insert: HTTP {code} -- {text[:200]}")
else:
    print("  [ERROR] Tables are missing. Please run supabase_setup.sql in the Supabase SQL Editor:")
    print()
    print("     1. Go to: https://supabase.com/dashboard/project/kdtskvugdhtwjegdegno/sql/new")
    print("     2. Paste the contents of  c:\\Remote Robotic Surgery\\supabase_setup.sql")
    print("     3. Click Run (Ctrl+Enter)")
    print()
print("=" * 55)
