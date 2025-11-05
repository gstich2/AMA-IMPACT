from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "AMA IMPACT"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DB_NAME: str = "ama-impact.db"  # Can be overridden with env var: ama-impact.db or devel.db
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from DB_NAME."""
        return f"sqlite:///./{ self.DB_NAME}"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        """Return list of allowed CORS origins."""
        return [self.FRONTEND_URL, "http://localhost:3000"]
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@ama-impact.com"
    
    # Scheduler
    NOTIFICATION_CHECK_HOUR: int = 8
    NOTIFICATION_CHECK_MINUTE: int = 0
    
    # Initial Admin User (for database initialization)
    INITIAL_ADMIN_EMAIL: str = "admin@example.com"
    INITIAL_ADMIN_PASSWORD: str = "ChangeMe123!"
    INITIAL_ADMIN_NAME: str = "System Administrator"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env for backward compatibility


settings = Settings()
