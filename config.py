"""
AEGIS FIT Backend Configuration
Handles all application settings and environment variables
"""

import os
from typing import List, Optional, Any
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Basic Configuration
    secret_key: str = Field(default="aegis-fit-2024-super-secret-jwt-key")
    cors_origins: str = Field(default="http://localhost:3000,https://aegis-fit.vercel.app")
    database_url: str = Field(default="sqlite:///./aegis_fit.db")
    environment: str = Field(default="development")
    
    # Stripe Configuration
    stripe_secret_key: Optional[str] = Field(default=None)
    stripe_publishable_key: Optional[str] = Field(default=None)
    stripe_webhook_secret: Optional[str] = Field(default=None)
    
    # Email Configuration
    smtp_host: Optional[str] = Field(default=None)
    smtp_port: int = Field(default=587)
    smtp_username: Optional[str] = Field(default=None)
    smtp_password: Optional[str] = Field(default=None)
    
    # Monitoring and Logging
    log_level: str = Field(default="INFO")
    structured_logging: bool = Field(default=True)
    
    # Rate Limiting
    rate_limiting_enabled: bool = Field(default=False)
    rate_limit_per_minute: int = Field(default=100)
    
    # Security
    security_headers_enabled: bool = Field(default=True)
    csp_enabled: bool = Field(default=True)
    
    # Development Settings
    debug: bool = Field(default=False)
    auto_reload: bool = Field(default=False)
    enable_docs_in_production: bool = Field(default=False)
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        """Validate secret key length"""
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v
    
    @validator('cors_origins')
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins into list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment value"""
        valid_environments = ['development', 'staging', 'production']
        if v.lower() not in valid_environments:
            raise ValueError(f'ENVIRONMENT must be one of: {valid_environments}')
        return v.lower()
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of: {valid_levels}')
        return v.upper()
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == 'development'
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == 'production'
    
    def is_staging(self) -> bool:
        """Check if running in staging mode"""
        return self.environment == 'staging'
    
    def is_stripe_configured(self) -> bool:
        """Check if Stripe is properly configured"""
        return all([
            self.stripe_secret_key,
            self.stripe_publishable_key,
            self.stripe_webhook_secret
        ])
    
    def is_email_configured(self) -> bool:
        """Check if email is properly configured"""
        return all([
            self.smtp_host,
            self.smtp_username,
            self.smtp_password
        ])
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as list"""
        return self.cors_origins
    
    def should_show_docs(self) -> bool:
        """Check if API docs should be enabled"""
        if self.is_development():
            return True
        return self.enable_docs_in_production
    
    def get_database_url(self) -> str:
        """Get database URL"""
        return self.database_url
    
    def get_log_level(self) -> str:
        """Get log level"""
        return self.log_level
    
    def __str__(self) -> str:
        """String representation of settings (hides sensitive data)"""
        return f"""
Settings(
    environment={self.environment},
    debug={self.debug},
    cors_origins={len(self.cors_origins)} origins,
    stripe_configured={self.is_stripe_configured()},
    email_configured={self.is_email_configured()},
    docs_enabled={self.should_show_docs()}
)"""
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return self.__str__()


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment (useful for testing)"""
    global settings
    settings = Settings()
    return settings


# Validation function
def validate_settings() -> bool:
    """Validate all settings"""
    try:
        # Test basic settings
        assert len(settings.secret_key) >= 32
        assert len(settings.cors_origins) > 0
        assert settings.environment in ['development', 'staging', 'production']
        
        # Test Stripe settings if configured
        if settings.stripe_secret_key:
            assert settings.stripe_secret_key.startswith('sk_')
        
        if settings.stripe_publishable_key:
            assert settings.stripe_publishable_key.startswith('pk_')
        
        if settings.stripe_webhook_secret:
            assert settings.stripe_webhook_secret.startswith('whsec_')
        
        logger.info("Settings validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Settings validation failed: {e}")
        return False


# Initialize logging based on settings
def setup_logging():
    """Setup logging configuration based on settings"""
    log_level = settings.get_log_level()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    if settings.structured_logging:
        import structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )


if __name__ == "__main__":
    # Test settings when run directly
    print("Testing AEGIS FIT Backend Settings")
    print("=" * 50)
    
    # Load and display settings
    current_settings = get_settings()
    print(current_settings)
    
    # Validate settings
    if validate_settings():
        print("\n✅ Settings validation passed")
    else:
        print("\n❌ Settings validation failed")
    
    # Display configuration status
    print(f"\nConfiguration Status:")
    print(f"  Environment: {current_settings.environment}")
    print(f"  Debug Mode: {current_settings.debug}")
    print(f"  Stripe Configured: {current_settings.is_stripe_configured()}")
    print(f"  Email Configured: {current_settings.is_email_configured()}")
    print(f"  API Docs Enabled: {current_settings.should_show_docs()}")
    print(f"  CORS Origins: {len(current_settings.get_cors_origins())}")