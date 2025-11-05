# AMA-IMPACT Immigration Management System

**Internal visa and immigration case tracking system for AMA Inc.**

!!! info "Version"
    Current Version: **2.0**  
    Last Updated: November 4, 2025

## Overview

AMA-IMPACT is a comprehensive web application designed to track and manage foreign national employee visa and green card applications across multiple company contracts. The system provides role-based access control, automated notifications, hierarchical case management, and task tracking capabilities.

## Key Features

### 🔐 **Role-Based Access Control**
- Five user roles: Admin, HR, Program Manager (PM), Manager, Beneficiary
- Hierarchical visibility based on organizational structure
- Contract-based data isolation

### 📋 **Comprehensive Case Management**
- Track visa applications from filing to approval
- **Case Groups** for organizing related visa cases (e.g., H1B → Green Card pathway)
- **Dependent tracking** for family members
- RFE (Request for Evidence) management
- Timeline tracking with milestones

### ✅ **Task Management**
- **Todo system** with role-based access
- **Computed metrics**: overdue status, completion time, on-time tracking
- Priority levels and status tracking
- Dashboard for team and personal todos

### 📊 **Analytics & Reporting**
- Dashboard with key metrics
- Expiration tracking and alerts
- Performance analytics
- Export capabilities

### 🔔 **Automated Notifications**
- Email alerts for expiring visas
- In-app notifications
- Configurable thresholds
- Escalation rules

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT with OAuth2
- **Email**: SMTP with templates

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: React Query + Zustand

## Quick Links

- [Getting Started](getting-started/quickstart.md) - Set up your development environment
- [API Reference](api/overview.md) - Complete API documentation
- [Data Models](architecture/data-models.md) - Database schema and relationships
- [Product Requirements](product/prd.md) - Full PRD with use cases

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (Next.js)                     │
│  ┌──────────┬──────────┬──────────┬──────────┬───────────┐ │
│  │Dashboard │  Users   │  Visas   │  Cases   │   Todos   │ │
│  └──────────┴──────────┴──────────┴──────────┴───────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │ REST API
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────┬──────────┬──────────┬──────────┬───────────┐ │
│  │   Auth   │  RBAC    │  Visa    │  Case    │   Todo    │ │
│  │          │Middleware│  API     │  Groups  │   API     │ │
│  └──────────┴──────────┴──────────┴──────────┴───────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │ SQLAlchemy
┌─────────────────────────────────────────────────────────────┐
│                     Database (SQLite)                        │
│  ┌──────────┬──────────┬──────────┬──────────┬───────────┐ │
│  │  Users   │Benefic-  │  Visa    │  Case    │   Todos   │ │
│  │          │ iaries   │  Apps    │  Groups  │           │ │
│  └──────────┴──────────┴──────────┴──────────┴───────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Core Concepts

### Users vs Beneficiaries

**User** = System access account (authentication + authorization)
- US citizens (managers, HR, PMs) have User accounts only
- Has email, password, role, organizational hierarchy

**Beneficiary** = Foreign national with visa cases
- May or may not have a User account
- Future hires are Beneficiaries without User accounts
- Links to User via one-to-one relationship when employed

### Case Groups

**CaseGroup** = Collection of related visa applications
- Example: H1B → EB2-NIW I-140 → I-485 AOS → Green Card
- Tracks the entire immigration journey
- Organized under a Beneficiary

### Task Tracking

**Todo** = Action items for visa case management
- Assigned to users with role-based visibility
- **Computed metrics** for performance tracking:
    - `is_overdue`: Dynamic calculation based on due date
    - `days_overdue`: Time past due date
    - `days_to_complete`: Duration from creation to completion
    - `completed_on_time`: Whether completed before deadline
- Dashboard views for individuals and teams

## Getting Started

1. **[Install Prerequisites](getting-started/installation.md)** - Python 3.12+, Node.js 18+
2. **[Setup Development Environment](getting-started/quickstart.md)** - Clone, install, configure
3. **[Run the Application](getting-started/first-steps.md)** - Start backend and frontend
4. **[Explore the API](api/overview.md)** - Test endpoints with Swagger UI

## Support

For questions, issues, or contributions:

- **Internal Wiki**: [Confluence Page](https://ama-inc.atlassian.net)
- **Issues**: GitHub Issues
- **Contact**: dev-team@ama-inc.com

---

**Made with ❤️ by the AMA Engineering Team**
