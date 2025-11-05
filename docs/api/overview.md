# API Overview

The AMA-IMPACT API is built with **FastAPI** and follows **REST** principles with **JWT authentication**.

## Base URL

```
Development: http://localhost:8000/api/v1
Production:  https://api.ama-impact.com/api/v1
```

## Authentication

All endpoints except `/auth/login` and `/auth/forgot-password` require authentication.

### Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepass123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using Tokens

Include the access token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Response Format

### Success Response (2xx)

```json
{
  "id": "uuid",
  "field1": "value1",
  "field2": "value2",
  ...
}
```

Or for lists:

```json
[
  { "id": "uuid-1", ... },
  { "id": "uuid-2", ... }
]
```

### Error Response (4xx, 5xx)

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Role-Based Access Control

Different endpoints have different permission requirements:

| Role | Access Level |
|------|-------------|
| **ADMIN** | Full system access |
| **HR** | Manage visa applications, view all beneficiaries, create BENEFICIARY users |
| **PM** | View all data, advanced metrics, create BENEFICIARY users |
| **MANAGER** | View direct/indirect reports, create BENEFICIARY users |
| **BENEFICIARY** | View own cases only |

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Rate Limiting

- **Login attempts**: 5 per 15 minutes per IP
- **Password changes**: 2 per 24 hours per user
- **General API**: 100 requests per minute per user

## API Endpoints by Category

### Authentication
- `POST /auth/login` - Login with email/password
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout (invalidate refresh token)
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token
- `POST /auth/change-password` - Change own password

### Users
- `GET /users` - List users (role-filtered)
- `GET /users/{id}` - Get user details
- `POST /users` - Create user (role-based permissions)
- `PATCH /users/{id}` - Update user
- `DELETE /users/{id}` - Deactivate user
- `GET /users/me` - Get current user profile

### Beneficiaries
- `GET /beneficiaries` - List beneficiaries
- `GET /beneficiaries/{id}` - Get beneficiary details
- `POST /beneficiaries` - Create beneficiary
- `PATCH /beneficiaries/{id}` - Update beneficiary
- `DELETE /beneficiaries/{id}` - Deactivate beneficiary

### Visa Applications
- `GET /visa-applications` - List visa applications
- `GET /visa-applications/{id}` - Get application details
- `POST /visa-applications` - Create application
- `PATCH /visa-applications/{id}` - Update application
- `DELETE /visa-applications/{id}` - Delete application

### Case Groups
- `GET /case-groups` - List case groups
- `GET /case-groups/{id}` - Get case group details
- `POST /case-groups` - Create case group
- `PATCH /case-groups/{id}` - Update case group
- `DELETE /case-groups/{id}` - Delete case group
- `GET /case-groups/{id}/visa-applications` - Get applications in group

### Todos
- `GET /todos/my-todos` - Get my assigned todos
- `GET /todos/team-todos` - Get team todos (hierarchy-based)
- `GET /todos/stats` - Get todo statistics
- `GET /todos/beneficiary/{id}` - Get todos for beneficiary
- `GET /todos/visa-application/{id}` - Get todos for visa application
- `GET /todos/case-group/{id}` - Get todos for case group
- `POST /todos` - Create todo
- `GET /todos/{id}` - Get todo details
- `PATCH /todos/{id}` - Update todo
- `DELETE /todos/{id}` - Delete todo

### Contracts
- `GET /contracts` - List contracts
- `GET /contracts/{id}` - Get contract details
- `POST /contracts` - Create contract (admin only)
- `PATCH /contracts/{id}` - Update contract
- `DELETE /contracts/{id}` - Archive contract

### Departments
- `GET /departments` - List departments
- `GET /departments/{id}` - Get department details
- `POST /departments` - Create department
- `PATCH /departments/{id}` - Update department
- `DELETE /departments/{id}` - Deactivate department

## Common Query Parameters

### Filtering
```
?status=ACTIVE
?priority=HIGH
?visa_type=H1B
```

### Pagination (where supported)
```
?skip=0&limit=20
```

### Sorting (where supported)
```
?sort=created_at&order=desc
```

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success - Request completed |
| 201 | Created - Resource created successfully |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - Authenticated but insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Something went wrong |

## Error Handling

Validation errors return detailed information:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## Versioning

API version is included in the URL: `/api/v1/...`

Future versions will use `/api/v2/...` and maintain backward compatibility for v1.

## Next Steps

Explore specific endpoint documentation:

- [Authentication Endpoints](authentication.md)
- [User Management](users.md)
- [Beneficiaries](beneficiaries.md)
- [Visa Applications](visa-applications.md)
- [Case Groups](case-groups.md)
- [Todos](todos.md)
