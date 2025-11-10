# API Documentation

**AMA-IMPACT Backend API v3.0**

Complete API reference for the Immigration Visa Management System backend. All endpoints support role-based access control and return consistent JSON responses.

## Base URL
- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://your-domain.com/api/v1`

## Authentication
All endpoints (except `/auth/login` and `/health`) require JWT authentication via the `Authorization` header:

```
Authorization: Bearer <jwt_access_token>
```

## API Endpoints Overview

### 🔐 Authentication & Security
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/auth/login` | POST | User login with email/password |
| `/auth/refresh` | POST | Refresh JWT access token |
| `/auth/logout` | POST | Invalidate refresh token |
| `/password/change` | PUT | Change user password |
| `/password/reset-request` | POST | Request password reset |
| `/password/reset` | POST | Complete password reset |

### 📊 Dashboard & Analytics  
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/dashboard/summary` | GET | Role-based dashboard metrics |
| `/dashboard/expiring-visas` | GET | Visas expiring within timeframe |

### 👥 User Management
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/users/` | GET | List users with role-based filtering |
| `/users/` | POST | Create new user (role-restricted) |
| `/users/{id}` | GET | Get user details |
| `/users/{id}` | PUT | Update user information |
| `/users/{id}` | DELETE | Deactivate user |
| `/users/me` | GET | Get current user profile |
| `/users/me` | PUT | Update own profile |

### 🏢 Organizational Structure
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/contracts/` | GET, POST | Contract management |
| `/contracts/{id}` | GET, PUT, DELETE | Individual contract operations |
| `/departments/` | GET, POST | Department hierarchy management |
| `/departments/{id}` | GET, PUT, DELETE | Department operations |

### 👤 Beneficiary Management
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/beneficiaries/` | GET, POST | Foreign national tracking |
| `/beneficiaries/{id}` | GET, PUT, DELETE | Individual beneficiary operations |
| `/beneficiaries/{id}/visa-applications` | GET | All visa cases for beneficiary |
| `/dependents/` | GET, POST | Dependent family members |
| `/dependents/{id}` | GET, PUT, DELETE | Dependent operations |

### 📋 Visa Case Management
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/visa-applications/` | GET | List visa applications with advanced filtering |
| `/visa-applications/` | POST | Create new visa application |
| `/visa-applications/{id}` | GET, PUT, DELETE | Individual case operations |
| `/visa-applications/bulk-update` | PUT | Update multiple applications |
| `/visa-applications/export` | GET | Export applications as CSV/Excel |

### ✅ Task Management  
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/todos/` | GET, POST | Task management with computed metrics |
| `/todos/{id}` | GET, PUT, DELETE | Individual task operations |
| `/todos/bulk-complete` | POST | Mark multiple tasks complete |
| `/todos/metrics` | GET | Task performance analytics |

### 🔗 Supporting Data
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/case-groups/` | GET, POST | Immigration pathway grouping |
| `/case-groups/{id}` | GET, PUT, DELETE | Case group operations |
| `/law-firms/` | GET, POST | Legal service provider management |
| `/law-firms/{id}` | GET, PUT, DELETE | Law firm operations |

### 🔔 Notifications
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/notifications/` | GET | User notifications with filtering |
| `/notifications/` | POST | Create individual notification |
| `/notifications/bulk` | POST | Create bulk notifications |
| `/notifications/system-announcement` | POST | System-wide announcements |
| `/notifications/{id}/read` | PATCH | Mark notification as read |
| `/notifications/mark-all-read` | PATCH | Mark all notifications as read |
| `/notifications/stats` | GET | Notification statistics |
| `/notifications/check-expiring-visas` | POST | Manual expiration check |
| `/notifications/check-overdue-todos` | POST | Manual overdue task check |
| `/notifications/cleanup` | DELETE | Clean up old notifications |

### 📋 Audit & Compliance
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/audit-logs/` | GET | Comprehensive audit trail with filtering |
| `/audit-logs/stats` | GET | Audit statistics and summaries |
| `/audit-logs/resource/{type}/{id}` | GET | Activity history for specific resource |
| `/audit-logs/user/{id}` | GET | User activity summary |
| `/audit-logs/compliance-report` | GET | Generate compliance report |
| `/audit-logs/security-events` | GET | Security-related audit events |
| `/audit-logs/changes-summary` | GET | Recent system changes overview |
| `/audit-logs/cleanup` | DELETE | Clean up old audit records |

### 📊 Reports & Analytics
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/reports/types` | GET | Available report types by role |
| `/reports/generate` | POST | Generate comprehensive reports |
| `/reports/visa-status` | GET | Detailed visa status analytics |
| `/reports/user-activity` | GET | User engagement and activity patterns |
| `/reports/executive-summary` | GET | Executive dashboard with KPIs |
| `/reports/department-stats` | GET | **NEW** Department visa tracking statistics |
| `/reports/dashboard/widgets` | GET | Real-time dashboard widgets |
| `/reports/{id}/status` | GET | Check report generation status |
| `/reports/{id}/download` | GET | Download generated report files |
| `/reports/analytics/trends` | GET | Time-series trend analysis |
| `/reports/cleanup` | DELETE | Clean up old report files |

## Role-Based Access Control

### User Roles
- **ADMIN**: Full system access, user management, system configuration
- **HR**: Multi-contract access, can create beneficiary users, compliance reports
- **PM**: Contract-wide access, advanced analytics, can create beneficiary users
- **MANAGER**: Team-level access based on reporting hierarchy, can create beneficiary users
- **BENEFICIARY**: Self-only access to own visa cases and tasks

### Data Scoping
All endpoints automatically filter data based on user role:
- **Beneficiaries** see only their own data
- **Managers** see data for users in their reporting hierarchy
- **PMs** see all data within their assigned contracts
- **HR/Admin** see all system data

## Advanced Filtering

Most list endpoints support comprehensive filtering:

**Common Parameters:**
- `limit`: Results per page (default: 50, max: 500)
- `offset`: Pagination offset (default: 0)
- `sort_by`: Field to sort by
- `sort_order`: "asc" or "desc"
- `search`: Text search across relevant fields

**Visa Applications Filtering:**
- `status`: Filter by visa status
- `visa_type`: Filter by visa type (H1B, L1, etc.)
- `priority`: Filter by priority level
- `expiring_within_days`: Find visas expiring soon
- `beneficiary_id`: Filter by beneficiary
- `department_id`: Filter by department
- `law_firm_id`: Filter by law firm

**Audit Logs Filtering:**
- `user_id`: Filter by user who performed action
- `action`: Filter by audit action type
- `resource_type`: Filter by resource (visa_application, user, etc.)
- `date_from` / `date_to`: Date range filtering
- `ip_address`: Filter by IP address

## Response Format

All endpoints return consistent JSON responses:

**Success Response:**
```json
{
  "data": { ... },          // Response data
  "message": "Success",     // Optional success message
  "timestamp": "2025-11-05T12:00:00Z"
}
```

**List Response:**
```json
{
  "data": [...],           // Array of items
  "total": 150,            // Total count
  "limit": 50,             // Items per page
  "offset": 0,             // Current offset
  "has_next": true         // More pages available
}
```

**Error Response:**
```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-11-05T12:00:00Z"
}
```

## Notification Types

The notification system supports various alert types:

- `VISA_EXPIRING`: Visa expiration warnings
- `OVERDUE`: Overdue tasks and expired visas  
- `STATUS_CHANGED`: Status updates for applications
- `SYSTEM`: System announcements
- `REMINDER`: General reminders and alerts

## Audit Actions

All system changes are logged with these action types:

- `CREATE`: Resource creation
- `UPDATE`: Resource modifications
- `DELETE`: Resource deletion
- `LOGIN` / `LOGIN_FAILED`: Authentication events
- `EXPORT`: Data export operations
- `VIEW`: Resource access (for sensitive data)

## Export Formats

Reports and data exports support multiple formats:

- `JSON`: Structured data format
- `CSV`: Comma-separated values for Excel
- `XLSX`: Native Excel format
- `PDF`: Formatted documents (reports only)


## Rate Limiting

Authentication endpoints are rate-limited:
- Login attempts: 5 per minute per IP
- Password reset: 3 per hour per IP
- Other endpoints: 100 per minute per user

---

## Department Statistics Endpoint

### GET `/api/v1/reports/department-stats`

Get visa tracking statistics for a department or contract. Focuses on beneficiary counts and visa application metrics.

**Query Parameters:**
- `department_id` (optional): Specific department UUID
- `contract_id` (optional): Contract UUID for contract-wide stats
- `include_subdepartments` (default: `true`): Include recursive sub-department statistics

**Requirements:**
- At least one of `department_id` or `contract_id` must be provided
- Beneficiary role users cannot access this endpoint

**Access Control:**
- **ADMIN**: Can view any department/contract
- **PM/HR**: Can view their contract's departments
- **MANAGER**: Can view their department and sub-departments only
- **BENEFICIARY**: Access denied

**Response Schema:**
```json
{
  "department_id": "uuid",
  "department_name": "Entry Systems and Technology Division",
  "department_code": "TS",
  "contract_id": "uuid",
  "contract_code": "ASSESS",
  "beneficiaries_direct": 8,
  "beneficiaries_total": 12,
  "beneficiaries_active": 11,
  "beneficiaries_inactive": 1,
  "visa_applications_total": 25,
  "visa_applications_active": 18,
  "visa_applications_by_status": {
    "DRAFT": 2,
    "IN_PROGRESS": 3,
    "APPROVED": 15,
    "DENIED": 5
  },
  "visa_applications_by_type": {
    "H1B": 10,
    "L1": 5,
    "EB2": 8,
    "TN": 2
  },
  "expiring_next_30_days": 2,
  "expiring_next_90_days": 5,
  "expired": 1,
  "generated_at": "2025-11-07T12:00:00Z",
  "include_subdepartments": true
}
```

**Example Requests:**

1. **Specific Department with Sub-departments:**
```bash
GET /api/v1/reports/department-stats?department_id=abc123&include_subdepartments=true
```

2. **Contract-Wide Statistics:**
```bash
GET /api/v1/reports/department-stats?contract_id=xyz789
```

3. **Department Only (No Sub-departments):**
```bash
GET /api/v1/reports/department-stats?department_id=abc123&include_subdepartments=false
```

**Use Cases:**
- **Tree View Badges**: Display inline statistics for each department
- **Department Dashboard**: Show detailed metrics for selected department
- **Contract Overview**: Aggregate all departments within a contract
- **Manager Dashboard**: Show manager's department team statistics

---

## Interactive Documentation

Complete interactive API documentation with request/response examples available at:
- **Development**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Support

For API questions or issues:
- Check interactive docs at `/docs`
- Review audit logs for debugging
- Contact system administrators for access issues
```