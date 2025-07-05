import re
import logging
from typing import Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database Configuration
    database_url: str = Field(..., description="PostgreSQL database URL")
    
    # Application Configuration
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Blockchain & Web3
    alchemy_api_key: str = Field(..., description="Alchemy API key for Sepolia")
    alchemy_sepolia_url: str = Field(..., description="Alchemy Sepolia RPC URL")
    thirdweb_secret_key: str = Field(..., description="Thirdweb secret key for treasury operations")
    treasury_wallet_address: str = Field(..., description="Ultra Civic treasury wallet address")
    pr_token_contract_address: str = Field(..., description="$PR token contract address on Sepolia")
    
    # Email
    resend_api_key: str = Field(..., description="Resend API key for email notifications")
    alert_email: str = Field(default="paco@ultracivic.com", description="Email for alerts")
    
    # API Configuration
    frontend_url: str = Field(default="http://localhost:3000", description="Frontend URL for CORS")
    rate_limit_requests: int = Field(default=10, description="Rate limit requests per minute per IP")
    
    # Transaction Monitoring
    tx_timeout_minutes: int = Field(default=5, description="Transaction timeout in minutes")
    reservation_timeout_minutes: int = Field(default=15, description="Reservation timeout in minutes")
    
    # Pricing
    allowance_price_usd: float = Field(default=24.0, description="Price per allowance in USD")
    
    # 1inch API
    oneinch_api_url: str = Field(default="https://api.1inch.io/v5.0/11155111", description="1inch API URL for Sepolia")
    
    # Production-specific Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    db_pool_size: int = Field(default=10, description="Database connection pool size")
    audit_logging_enabled: bool = Field(default=True, description="Enable audit logging")
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    
    # Development-specific Configuration
    db_echo_queries: bool = Field(default=False, description="Enable SQL query logging")
    cors_allow_all_origins: bool = Field(default=False, description="Allow CORS from any origin")
    
    @validator('treasury_wallet_address', 'pr_token_contract_address')
    def validate_ethereum_address(cls, v):
        """Validate Ethereum address format"""
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError(f'Invalid Ethereum address format: {v}')
        return v.lower()
    
    @validator('database_url')
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v.startswith('postgresql+asyncpg://'):
            raise ValueError('Database URL must use asyncpg driver (postgresql+asyncpg://)')
        return v
    
    @validator('alchemy_sepolia_url')
    def validate_alchemy_url(cls, v):
        """Validate Alchemy URL format"""
        if not v.startswith('https://eth-sepolia.g.alchemy.com/v2/'):
            raise ValueError('Invalid Alchemy Sepolia URL format')
        return v
    
    @validator('frontend_url')
    def validate_frontend_url(cls, v):
        """Validate frontend URL format"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Frontend URL must start with http:// or https://')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Invalid log level: {v}. Must be one of {valid_levels}')
        return v.upper()
    
    @validator('rate_limit_requests')
    def validate_rate_limit(cls, v):
        """Validate rate limit value"""
        if v < 1 or v > 1000:
            raise ValueError('Rate limit must be between 1 and 1000 requests per minute')
        return v
    
    @validator('allowance_price_usd')
    def validate_price(cls, v):
        """Validate allowance price"""
        if v <= 0:
            raise ValueError('Allowance price must be greater than 0')
        return v


def validate_environment():
    """Validate environment configuration on startup"""
    try:
        settings = Settings()
        
        # Additional validation logic
        if settings.debug and not settings.database_url.startswith('postgresql+asyncpg://localhost'):
            logging.warning("Debug mode enabled with non-local database. This may expose sensitive data.")
        
        if not settings.debug and settings.cors_allow_all_origins:
            raise ValueError("CORS_ALLOW_ALL_ORIGINS cannot be true in production mode")
        
        # Validate required API keys are not placeholder values
        placeholder_keys = [
            'your_alchemy_api_key_here',
            'your_thirdweb_secret_key_here',
            'your_resend_api_key_here'
        ]
        
        if settings.alchemy_api_key in placeholder_keys:
            raise ValueError("ALCHEMY_API_KEY is still set to placeholder value")
        
        if settings.thirdweb_secret_key in placeholder_keys:
            raise ValueError("THIRDWEB_SECRET_KEY is still set to placeholder value")
        
        if settings.resend_api_key in placeholder_keys:
            raise ValueError("RESEND_API_KEY is still set to placeholder value")
        
        # Configure logging based on settings
        logging.basicConfig(
            level=getattr(logging, settings.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logging.info("Environment validation completed successfully")
        return settings
        
    except Exception as e:
        logging.error(f"Environment validation failed: {str(e)}")
        raise


settings = validate_environment()