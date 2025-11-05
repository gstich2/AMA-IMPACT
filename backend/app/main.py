from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import auth, users, beneficiaries, contracts, visa_applications, password, law_firms, dependents, case_groups, todos, departments, dashboard, notifications, audit_logs, reports

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Immigration Visa Management System API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers (ordered for Swagger UI display)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(password.router, prefix="/api/v1/password", tags=["Password Management"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(contracts.router, prefix="/api/v1/contracts", tags=["Contracts"])
app.include_router(departments.router, prefix="/api/v1/departments", tags=["Departments"])
app.include_router(beneficiaries.router, prefix="/api/v1/beneficiaries", tags=["Beneficiaries"])
app.include_router(dependents.router, prefix="/api/v1/dependents", tags=["Dependents"])
app.include_router(case_groups.router, prefix="/api/v1/case-groups", tags=["Case Groups"])
app.include_router(visa_applications.router, prefix="/api/v1/visa-applications", tags=["Visa Applications"])
app.include_router(todos.router, prefix="/api/v1/todos", tags=["Todos"])
app.include_router(law_firms.router, prefix="/api/v1/law-firms", tags=["Law Firms"])

# Advanced APIs - moved to end for better organization
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(audit_logs.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
