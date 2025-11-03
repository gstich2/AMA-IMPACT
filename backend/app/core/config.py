from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "AMA IMPACT"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./ama_impact.db"
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
