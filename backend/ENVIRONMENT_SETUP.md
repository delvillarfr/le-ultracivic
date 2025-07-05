# Environment Setup Guide

## Quick Start

1. **Copy the development template**:
   ```bash
   cp .env.local.example .env
   ```

2. **Update API keys** in `.env`:
   - Get Alchemy API key from [Alchemy Dashboard](https://dashboard.alchemy.com/)
   - Get Thirdweb secret key from [Thirdweb Dashboard](https://thirdweb.com/dashboard/settings/api-keys)
   - Get Resend API key from [Resend Dashboard](https://resend.com/api-keys)

3. **Set up local PostgreSQL**:
   ```bash
   # Create database and user
   createdb ultracivic_dev
   psql -c "CREATE USER ultracivic WITH PASSWORD 'ultracivic';"
   psql -c "GRANT ALL PRIVILEGES ON DATABASE ultracivic_dev TO ultracivic;"
   ```

4. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost:5432/db` |
| `ALCHEMY_API_KEY` | Alchemy API key for Sepolia | `your_alchemy_api_key_here` |
| `ALCHEMY_SEPOLIA_URL` | Alchemy Sepolia RPC URL | `https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY` |
| `THIRDWEB_SECRET_KEY` | Thirdweb secret key | `your_thirdweb_secret_key_here` |
| `TREASURY_WALLET_ADDRESS` | Treasury wallet address | `0x742d35Cc6634C0532925a3b8D11D2D7D2AE30B2B` |
| `PR_TOKEN_CONTRACT_ADDRESS` | $PR token contract address | `0x742d35Cc6634C0532925a3b8D11D2D7D2AE30B2B` |
| `RESEND_API_KEY` | Resend API key | `your_resend_api_key_here` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `FRONTEND_URL` | `http://localhost:3000` | Frontend URL for CORS |
| `RATE_LIMIT_REQUESTS` | `10` | Rate limit per minute per IP |
| `TX_TIMEOUT_MINUTES` | `5` | Transaction timeout |
| `RESERVATION_TIMEOUT_MINUTES` | `15` | Reservation timeout |
| `ALLOWANCE_PRICE_USD` | `24.0` | Price per allowance in USD |
| `LOG_LEVEL` | `INFO` | Logging level |
| `AUDIT_LOGGING_ENABLED` | `true` | Enable audit logging |

## Getting API Keys

### Alchemy API Key
1. Go to [Alchemy Dashboard](https://dashboard.alchemy.com/)
2. Create a new app for "Ethereum Sepolia"
3. Copy the API key from the app dashboard
4. Update `ALCHEMY_API_KEY` and `ALCHEMY_SEPOLIA_URL`

### Thirdweb Secret Key
1. Go to [Thirdweb Dashboard](https://thirdweb.com/dashboard/settings/api-keys)
2. Create a new secret key
3. Copy the secret key
4. Update `THIRDWEB_SECRET_KEY`

### Resend API Key
1. Go to [Resend Dashboard](https://resend.com/api-keys)
2. Create a new API key
3. Copy the API key
4. Update `RESEND_API_KEY`

## Security Considerations

### Development
- Use test/dummy values for development
- Never commit real API keys to version control
- Use debug mode only in development

### Production
- Use strong, unique values for all API keys
- Set `DEBUG=false` in production
- Use production database URLs
- Enable audit logging
- Set appropriate rate limits
- Monitor error logs

## Troubleshooting

### Common Issues

1. **Database connection fails**:
   - Check PostgreSQL is running
   - Verify database credentials
   - Ensure database exists

2. **API key validation fails**:
   - Check for placeholder values
   - Verify API keys are valid
   - Check API key permissions

3. **Environment validation fails**:
   - Check all required variables are set
   - Verify variable formats (URLs, addresses)
   - Check log output for specific errors

### Validation Errors

The application validates environment variables on startup. Common validation errors:

- **Invalid Ethereum address**: Must be 42 characters starting with `0x`
- **Invalid database URL**: Must use `postgresql+asyncpg://` driver
- **Invalid Alchemy URL**: Must use correct Sepolia format
- **Placeholder values**: API keys cannot be placeholder values
- **Invalid log level**: Must be DEBUG, INFO, WARNING, ERROR, or CRITICAL

## Environment Examples

### Development
```bash
DEBUG=true
DATABASE_URL=postgresql+asyncpg://ultracivic:ultracivic@localhost:5432/ultracivic_dev
RATE_LIMIT_REQUESTS=100
LOG_LEVEL=DEBUG
```

### Production
```bash
DEBUG=false
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db.example.com:5432/ultracivic
RATE_LIMIT_REQUESTS=10
LOG_LEVEL=INFO
AUDIT_LOGGING_ENABLED=true
```