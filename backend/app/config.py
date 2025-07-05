from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = Field(..., description="PostgreSQL database URL")
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


settings = Settings()