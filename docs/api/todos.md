# Todos API

Task tracking with hierarchical case relationships and computed performance metrics.

## Overview

Todos provide task management capabilities with:
- **Hierarchical organization**: Link to visa applications, case groups, or beneficiaries
- **Role-based visibility**: See tasks based on assignment and organizational hierarchy
- **Computed metrics**: Automatic calculation of overdue status, completion time, on-time performance
- **Auto-population**: Hierarchy automatically filled from visa application → case group → beneficiary

---

## Endpoints

### Create Todo

Create a new todo task.

```http
POST /api/v1/todos
```

**Authentication:** Required

**Permissions:** All roles can create todos

**Request Body:**
```json
{
  "title": "Submit I-485 Application",
  "description": "Prepare and submit adjustment of status application",
  "assigned_to_user_id": "user-uuid",
  "visa_application_id": "visa-uuid",  // Optional - auto-fills case_group_id, beneficiary_id
  "case_group_id": "case-uuid",        // Optional - auto-fills beneficiary_id
  "beneficiary_id": "ben-uuid",        // Optional - for beneficiary-level todos
  "status": "TODO",                     // Optional, default: TODO
  "priority": "HIGH",                   // Optional, default: MEDIUM
  "due_date": "2025-12-15"             // Optional
}
```

**Response:** `201 Created`
```json
{
  "id": "todo-uuid",
  "title": "Submit I-485 Application",
  "description": "Prepare and submit adjustment of status application",
  "assigned_to_user_id": "user-uuid",
  "created_by_user_id": "creator-uuid",
  "visa_application_id": "visa-uuid",
  "case_group_id": "case-uuid",        // Auto-populated
  "beneficiary_id": "ben-uuid",        // Auto-populated
  "status": "TODO",
  "priority": "HIGH",
  "due_date": "2025-12-15",
  "completed_at": null,
  "created_at": "2025-11-05T10:00:00Z",
  "updated_at": "2025-11-05T10:00:00Z",
  "is_overdue": false,
  "days_overdue": null,
  "days_to_complete": null,
  "completed_on_time": null
}
```

**Notes:**
- If `visa_application_id` provided, system auto-fills `case_group_id` and `beneficiary_id`
- If only `case_group_id` provided, system auto-fills `beneficiary_id`
- If none provided, creates a general todo not tied to any case

---

### Get My Todos

Get todos assigned to the current user.

```http
GET /api/v1/todos/my-todos
```

**Authentication:** Required

**Query Parameters:**
- `status` (optional): Filter by status (TODO, IN_PROGRESS, BLOCKED, COMPLETED, CANCELLED)
- `priority` (optional): Filter by priority (LOW, MEDIUM, HIGH, URGENT)
- `include_completed` (optional): Include completed todos (default: false)

**Examples:**
```http
GET /api/v1/todos/my-todos
GET /api/v1/todos/my-todos?status=TODO&priority=URGENT
GET /api/v1/todos/my-todos?include_completed=true
```

**Response:** `200 OK`
```json
[
  {
    "id": "todo-1",
    "title": "Submit I-485 Application",
    "description": "Prepare and submit adjustment of status application",
    "assigned_to_user_id": "user-uuid",
    "created_by_user_id": "hr-uuid",
    "visa_application_id": "visa-uuid",
    "case_group_id": "case-uuid",
    "beneficiary_id": "ben-uuid",
    "status": "IN_PROGRESS",
    "priority": "URGENT",
    "due_date": "2025-11-10",
    "completed_at": null,
    "created_at": "2025-11-01T10:00:00Z",
    "updated_at": "2025-11-02T14:30:00Z",
    "is_overdue": false,
    "days_overdue": null,
    "days_to_complete": null,
    "completed_on_time": null
  },
  {
    "id": "todo-2",
    "title": "Review LCA documents",
    "status": "TODO",
    "priority": "HIGH",
    "due_date": "2025-11-08",
    "is_overdue": true,        // Due date passed, not completed
    "days_overdue": 2,          // 2 days past due
    "completed_at": null
  }
]
```

**Notes:**
- Returns todos ordered by: priority (URGENT first) → due date (soonest first) → created date
- Computed metrics included automatically:
  - `is_overdue`: true if due_date < now AND status NOT IN (COMPLETED, CANCELLED)
  - `days_overdue`: number of days past due (only if overdue)
  - `days_to_complete`: days from created to completed (only if completed)
  - `completed_on_time`: true if completed before due date (only if completed)

---

### Get Team Todos

Get todos for current user's reporting hierarchy.

```http
GET /api/v1/todos/team-todos
```

**Authentication:** Required

**Permissions:**
- **BENEFICIARY**: Only their own todos (same as my-todos)
- **MANAGER**: Their todos + all subordinates' todos (recursive hierarchy)
- **PM/HR/ADMIN**: All todos in the system

**Query Parameters:**
- `status` (optional): Filter by status
- `priority` (optional): Filter by priority
- `include_completed` (optional): Include completed todos (default: false)

**Response:** `200 OK`
```json
[
  {
    "id": "todo-1",
    "title": "Submit I-485 Application",
    "assigned_to_user_id": "subordinate-uuid",
    "status": "TODO",
    "priority": "URGENT",
    "is_overdue": false
  },
  {
    "id": "todo-2",
    "title": "Review petition draft",
    "assigned_to_user_id": "another-subordinate-uuid",
    "status": "IN_PROGRESS",
    "priority": "HIGH",
    "is_overdue": false
  }
]
```

**Use Case:**
- Managers viewing team workload
- HR viewing all pending tasks
- Dashboard for "Team Todos" widget

---

### Get Todo Statistics

Get todo statistics for dashboard display.

```http
GET /api/v1/todos/stats
```

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "total": 25,
  "todo": 10,
  "in_progress": 5,
  "blocked": 2,
  "completed": 7,
  "cancelled": 1,
  "overdue": 3,
  "urgent": 4,
  "high_priority": 6
}
```

**Fields:**
- `total`: Total todos assigned to user
- `todo`: Count with status = TODO
- `in_progress`: Count with status = IN_PROGRESS
- `blocked`: Count with status = BLOCKED
- `completed`: Count with status = COMPLETED
- `cancelled`: Count with status = CANCELLED
- `overdue`: Count with due_date < now AND status NOT IN (COMPLETED, CANCELLED)
- `urgent`: Count with priority = URGENT AND status != COMPLETED
- `high_priority`: Count with priority = HIGH AND status != COMPLETED

---

### Get Todos for Beneficiary

Get all todos related to a specific beneficiary.

```http
GET /api/v1/todos/beneficiary/{beneficiary_id}
```

**Authentication:** Required

**Permissions:**
- **BENEFICIARY**: Only if it's their own beneficiary record
- **MANAGER/PM/HR/ADMIN**: Any beneficiary

**Query Parameters:**
- `status` (optional): Filter by status

**Response:** `200 OK`
```json
[
  {
    "id": "todo-1",
    "title": "Submit I-485 Application",
    "beneficiary_id": "ben-uuid",
    "case_group_id": "case-uuid",
    "visa_application_id": "visa-uuid",
    "status": "TODO",
    "priority": "URGENT"
  }
]
```

**Use Case:**
- View all tasks for a specific employee
- Case management dashboard

---

### Get Todos for Visa Application

Get all todos for a specific visa application.

```http
GET /api/v1/todos/visa-application/{visa_application_id}
```

**Authentication:** Required

**Permissions:**
- **BENEFICIARY**: Only if it's their own visa application
- **MANAGER/PM/HR/ADMIN**: Any visa application

**Response:** `200 OK`
```json
[
  {
    "id": "todo-1",
    "title": "Submit I-485 Application",
    "visa_application_id": "visa-uuid",
    "status": "TODO",
    "due_date": "2025-11-15",
    "is_overdue": false
  },
  {
    "id": "todo-2",
    "title": "Prepare medical exam",
    "visa_application_id": "visa-uuid",
    "status": "IN_PROGRESS",
    "due_date": "2025-11-10",
    "is_overdue": false
  }
]
```

**Use Case:**
- View all tasks for a specific visa petition
- Visa application detail page

---

### Get Todos for Case Group

Get all todos for a specific case group.

```http
GET /api/v1/todos/case-group/{case_group_id}
```

**Authentication:** Required

**Permissions:**
- **BENEFICIARY**: Only if it's their own case group
- **MANAGER/PM/HR/ADMIN**: Any case group

**Response:** `200 OK`
```json
[
  {
    "id": "todo-1",
    "title": "File I-140 petition",
    "case_group_id": "case-uuid",
    "visa_application_id": "visa-1-uuid",
    "status": "COMPLETED",
    "completed_at": "2025-10-15T10:00:00Z",
    "days_to_complete": 5,
    "completed_on_time": true
  },
  {
    "id": "todo-2",
    "title": "Submit I-485 application",
    "case_group_id": "case-uuid",
    "visa_application_id": "visa-2-uuid",
    "status": "TODO",
    "due_date": "2025-12-01",
    "is_overdue": false
  }
]
```

**Use Case:**
- View all tasks across multiple visa applications in a case group
- Track progress of entire immigration pathway

---

### Get Todo by ID

Get details of a specific todo.

```http
GET /api/v1/todos/{id}
```

**Authentication:** Required

**Permissions:**
- **BENEFICIARY**: Only their own todos
- **Others**: Based on hierarchy

**Response:** `200 OK`
```json
{
  "id": "todo-uuid",
  "title": "Submit I-485 Application",
  "description": "Prepare and submit adjustment of status application with all supporting documents",
  "assigned_to_user_id": "user-uuid",
  "created_by_user_id": "hr-uuid",
  "visa_application_id": "visa-uuid",
  "case_group_id": "case-uuid",
  "beneficiary_id": "ben-uuid",
  "status": "IN_PROGRESS",
  "priority": "URGENT",
  "due_date": "2025-11-15",
  "completed_at": null,
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-02T14:30:00Z",
  "is_overdue": false,
  "days_overdue": null,
  "days_to_complete": null,
  "completed_on_time": null
}
```

---

### Update Todo

Update an existing todo.

```http
PATCH /api/v1/todos/{id}
```

**Authentication:** Required

**Permissions:**
- **Assigned user**: Can update status
- **PM/HR/ADMIN**: Can update everything

**Request Body:**
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "status": "COMPLETED",
  "priority": "HIGH",
  "due_date": "2025-12-01"
}
```

**Response:** `200 OK`
```json
{
  "id": "todo-uuid",
  "title": "Updated title",
  "status": "COMPLETED",
  "completed_at": "2025-11-05T15:30:00Z",  // Auto-set when status = COMPLETED
  "days_to_complete": 4,                    // Computed: completed_at - created_at
  "completed_on_time": true,                // Computed: completed_at <= due_date
  "updated_at": "2025-11-05T15:30:00Z"
}
```

**Notes:**
- When `status` changes to `COMPLETED`, `completed_at` is automatically set to current time
- When `status` changes from `COMPLETED` to another status, `completed_at` is cleared
- Computed metrics recalculated on every response

---

### Delete Todo

Delete a todo task.

```http
DELETE /api/v1/todos/{id}
```

**Authentication:** Required

**Permissions:**
- **Creator**: Can delete their own todos
- **PM/HR/ADMIN**: Can delete any todo

**Response:** `204 No Content`

---

## Data Models

### TodoCreate Schema
```python
{
  "title": str,                      # Required
  "description": str | None,         # Optional
  "assigned_to_user_id": UUID,       # Required
  "visa_application_id": UUID | None,  # Optional
  "case_group_id": UUID | None,      # Optional
  "beneficiary_id": UUID | None,     # Optional
  "status": TodoStatus,              # Optional, default: TODO
  "priority": TodoPriority,          # Optional, default: MEDIUM
  "due_date": date | None            # Optional
}
```

### TodoUpdate Schema
```python
{
  "title": str | None,
  "description": str | None,
  "assigned_to_user_id": UUID | None,
  "visa_application_id": UUID | None,
  "case_group_id": UUID | None,
  "beneficiary_id": UUID | None,
  "status": TodoStatus | None,
  "priority": TodoPriority | None,
  "due_date": date | None
}
```

### TodoResponse Schema
```python
{
  "id": UUID,
  "title": str,
  "description": str | None,
  "assigned_to_user_id": UUID,
  "created_by_user_id": UUID,
  "visa_application_id": UUID | None,
  "case_group_id": UUID | None,
  "beneficiary_id": UUID | None,
  "status": TodoStatus,
  "priority": TodoPriority,
  "due_date": date | None,
  "completed_at": datetime | None,
  "created_at": datetime,
  "updated_at": datetime,
  
  # Computed Metrics
  "is_overdue": bool | None,        # True if due_date < now AND not completed
  "days_overdue": int | None,       # Days past due date (if overdue)
  "days_to_complete": int | None,   # Days from creation to completion (if completed)
  "completed_on_time": bool | None  # True if completed <= due_date (if completed)
}
```

### TodoStats Schema
```python
{
  "total": int,
  "todo": int,
  "in_progress": int,
  "blocked": int,
  "completed": int,
  "cancelled": int,
  "overdue": int,
  "urgent": int,
  "high_priority": int
}
```

## Enums

### TodoStatus
```python
TODO         # Not started
IN_PROGRESS  # Currently working on it
BLOCKED      # Waiting on external dependency
COMPLETED    # Finished
CANCELLED    # No longer needed
```

### TodoPriority
```python
LOW      # Nice to have
MEDIUM   # Standard priority
HIGH     # Important, time-sensitive
URGENT   # Critical, immediate attention needed
```

## Examples

### Example 1: Create Todo for Visa Application

```bash
curl -X POST "http://localhost:8000/api/v1/todos" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Submit I-485 Application",
    "description": "Prepare and submit adjustment of status",
    "assigned_to_user_id": "hr-user-uuid",
    "visa_application_id": "visa-uuid",
    "priority": "URGENT",
    "due_date": "2025-12-01"
  }'
```

### Example 2: Get My Overdue Urgent Todos

```bash
curl -X GET "http://localhost:8000/api/v1/todos/my-todos?priority=URGENT" \
  -H "Authorization: Bearer $TOKEN"
  
# Filter in application for is_overdue == true
```

### Example 3: Complete a Todo

```bash
curl -X PATCH "http://localhost:8000/api/v1/todos/todo-uuid" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "COMPLETED"
  }'
  
# Response includes:
# - completed_at: "2025-11-05T15:30:00Z" (auto-set)
# - days_to_complete: 4 (computed)
# - completed_on_time: true (computed based on due_date)
```

### Example 4: Dashboard Todo Stats

```bash
curl -X GET "http://localhost:8000/api/v1/todos/stats" \
  -H "Authorization: Bearer $TOKEN"
  
# Use for dashboard widgets:
# - "3 Overdue Tasks" (overdue field)
# - "4 Urgent Tasks" (urgent field)
# - "5 In Progress" (in_progress field)
```

## Performance Considerations

### Computed Metrics
- Metrics calculated dynamically on retrieval
- No database writes needed for overdue status
- Timezone-aware datetime comparisons (UTC)

### Indexes
The following database indexes optimize todo queries:
- `(assigned_to_user_id, status)` - For my-todos filtering
- `(assigned_to_user_id, priority)` - For priority sorting
- `(beneficiary_id, status)` - For beneficiary todos
- `(due_date, status)` - For overdue queries

### Denormalization
- `beneficiary_id`, `case_group_id`, `visa_application_id` stored on Todo
- Avoids joins when filtering todos by case
- Trade-off: Slight redundancy for significant query performance gain

---

## Best Practices

1. **Always set due dates** for todos that have deadlines
2. **Use URGENT priority sparingly** - reserve for truly critical tasks
3. **Update status** as work progresses for accurate team visibility
4. **Add descriptions** to provide context for assignees
5. **Link to visa applications** when possible for hierarchical organization

---

## Related Endpoints

- [Beneficiaries API](beneficiaries.md) - Link todos to beneficiaries
- [Visa Applications API](visa-applications.md) - Link todos to visa applications
- [Case Groups API](case-groups.md) - Link todos to case groups
- [Users API](users.md) - Assign todos to users
