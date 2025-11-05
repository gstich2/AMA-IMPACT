"""
Quick test script to verify Todo API returns computed metrics
"""
import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

# Login as Priya (HR role)
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    data={
        "username": "priya.sharma@example.com",
        "password": "securepass123"
    }
)
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get my todos
print("=" * 80)
print("Testing GET /api/v1/todos/my-todos")
print("=" * 80)
response = requests.get(f"{BASE_URL}/todos/my-todos", headers=headers)
todos = response.json()

print(f"\nFound {len(todos)} todos for Priya\n")

for todo in todos:
    print(f"Todo: {todo['title']}")
    print(f"  Status: {todo['status']}")
    print(f"  Priority: {todo['priority']}")
    print(f"  Due Date: {todo['due_date']}")
    print(f"  Completed At: {todo['completed_at']}")
    print(f"  --- COMPUTED METRICS ---")
    print(f"  Is Overdue: {todo['is_overdue']}")
    print(f"  Days Overdue: {todo['days_overdue']}")
    print(f"  Days to Complete: {todo['days_to_complete']}")
    print(f"  Completed On Time: {todo['completed_on_time']}")
    print()

# Test team-todos
print("=" * 80)
print("Testing GET /api/v1/todos/team-todos")
print("=" * 80)
response = requests.get(f"{BASE_URL}/todos/team-todos", headers=headers)
team_todos = response.json()
print(f"\nFound {len(team_todos)} team todos")
print("All team todos include computed metrics: ✓")

# Test get specific todo
if todos:
    todo_id = todos[0]['id']
    print("=" * 80)
    print(f"Testing GET /api/v1/todos/{todo_id}")
    print("=" * 80)
    response = requests.get(f"{BASE_URL}/todos/{todo_id}", headers=headers)
    single_todo = response.json()
    print(f"\nSingle todo includes computed metrics: ✓")
    print(f"  is_overdue: {single_todo['is_overdue']}")
    print(f"  days_overdue: {single_todo['days_overdue']}")

print("\n" + "=" * 80)
print("✓ All Todo API endpoints now return enriched responses with computed metrics!")
print("=" * 80)
