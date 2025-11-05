"""
Quick test to verify Todo metrics are working
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:7001/api/v1"

# Try to login with various credentials
credentials = [
    ("admin@ama-impact.com", "adminpass123"),
    ("admin@ama-impact.com", "securepass123"),
    ("hr@ama-impact.com", "securepass123"),
    ("priya.sharma@ama-impact.com", "securepass123"),
]

token = None
for email, password in credentials:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"✅ Logged in as: {email}")
        break
    else:
        print(f"❌ Failed to login as {email}: {response.json().get('detail')}")

if not token:
    print("\n❌ Could not authenticate with any credentials")
    print("Please check the database and ensure users are seeded correctly")
    exit(1)

# Get my todos with metrics
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/todos/my-todos", headers=headers)

if response.status_code == 200:
    todos = response.json()
    print(f"\n✅ Retrieved {len(todos)} todos")
    
    if todos:
        print("\n" + "="*80)
        print("TODO METRICS VERIFICATION")
        print("="*80)
        
        for i, todo in enumerate(todos, 1):
            print(f"\n[{i}] {todo.get('title')}")
            print(f"    Status: {todo.get('status')} | Priority: {todo.get('priority')}")
            print(f"    Due Date: {todo.get('due_date')}")
            print(f"    Completed At: {todo.get('completed_at')}")
            print(f"    📊 METRICS:")
            print(f"       • is_overdue: {todo.get('is_overdue')}")
            print(f"       • days_overdue: {todo.get('days_overdue')}")
            print(f"       • days_to_complete: {todo.get('days_to_complete')}")
            print(f"       • completed_on_time: {todo.get('completed_on_time')}")
        
        print("\n" + "="*80)
        
        # Check if metrics are present
        metrics_found = all(
            key in todos[0] 
            for key in ['is_overdue', 'days_overdue', 'days_to_complete', 'completed_on_time']
        )
        
        if metrics_found:
            print("✅ All metric fields are present in the response!")
        else:
            print("❌ Some metric fields are missing")
            print(f"Available keys: {list(todos[0].keys())}")
    else:
        print("No todos found. This is normal if the database is empty.")
else:
    print(f"❌ Failed to get todos: {response.status_code}")
    print(response.text)
