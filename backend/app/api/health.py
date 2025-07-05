"""Health check endpoints for monitoring system status."""

import asyncio
import logging
from datetime import datetime
from typing import Dict

import httpx
from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, text

from app.config import settings
from app.database import get_session
from app.models.allowances import Allowance
from app.utils.retry import (
    alchemy_circuit_breaker,
    thirdweb_circuit_breaker,
    price_api_circuit_breaker
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ultra-civic-backend"
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check including external services."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ultra-civic-backend",
        "version": "1.0.0",
        "checks": {}
    }
    
    overall_healthy = True
    
    # Database health check
    try:
        async for session in get_session():
            # Test basic database connectivity
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            
            # Test allowances table access
            stmt = select(Allowance).limit(1)
            await session.execute(stmt)
            
            health_status["checks"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful"
            }
            break
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database error: {str(e)}"
        }
        overall_healthy = False
    
    # Circuit breaker status
    health_status["checks"]["circuit_breakers"] = {
        "alchemy": {
            "state": alchemy_circuit_breaker.state,
            "failure_count": alchemy_circuit_breaker.failure_count
        },
        "thirdweb": {
            "state": thirdweb_circuit_breaker.state,
            "failure_count": thirdweb_circuit_breaker.failure_count
        },
        "price_api": {
            "state": price_api_circuit_breaker.state,
            "failure_count": price_api_circuit_breaker.failure_count
        }
    }
    
    # External service checks (quick pings)
    external_checks = await asyncio.gather(
        _check_alchemy_health(),
        _check_thirdweb_health(),
        _check_price_api_health(),
        return_exceptions=True
    )
    
    # Process external check results
    service_names = ["alchemy", "thirdweb", "price_api"]
    for i, result in enumerate(external_checks):
        service_name = service_names[i]
        if isinstance(result, Exception):
            health_status["checks"][service_name] = {
                "status": "unhealthy",
                "message": f"Health check failed: {str(result)}"
            }
            overall_healthy = False
        else:
            health_status["checks"][service_name] = result
            if result["status"] != "healthy":
                overall_healthy = False
    
    # Set overall status
    health_status["status"] = "healthy" if overall_healthy else "unhealthy"
    
    return health_status


async def _check_alchemy_health() -> Dict:
    """Check Alchemy service health."""
    try:
        # Quick health check - get latest block number
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_blockNumber",
            "params": []
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                settings.alchemy_sepolia_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    return {
                        "status": "healthy",
                        "message": "Alchemy API responsive",
                        "block_number": data["result"]
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": f"Alchemy RPC error: {data.get('error', 'Unknown error')}"
                    }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"Alchemy HTTP error: {response.status_code}"
                }
                
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Alchemy connection failed: {str(e)}"
        }


async def _check_thirdweb_health() -> Dict:
    """Check Thirdweb service health."""
    try:
        # Simple health check - try to get account info
        headers = {
            "Authorization": f"Bearer {settings.thirdweb_secret_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                "https://engine.thirdweb.com/backend-wallets",
                headers=headers
            )
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "message": "Thirdweb Engine API responsive"
                }
            elif response.status_code == 401:
                return {
                    "status": "unhealthy",
                    "message": "Thirdweb authentication failed"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"Thirdweb HTTP error: {response.status_code}"
                }
                
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Thirdweb connection failed: {str(e)}"
        }


async def _check_price_api_health() -> Dict:
    """Check price API health (1inch)."""
    try:
        # Quick health check - get supported protocols
        headers = {
            "Authorization": f"Bearer {settings.oneinch_api_key}"
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                "https://api.1inch.dev/swap/v6.0/11155111/liquidity-sources",
                headers=headers
            )
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "message": "1inch API responsive"
                }
            elif response.status_code == 401:
                return {
                    "status": "unhealthy", 
                    "message": "1inch authentication failed"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"1inch HTTP error: {response.status_code}"
                }
                
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"1inch connection failed: {str(e)}"
        }


@router.get("/readiness")
async def readiness_check():
    """Kubernetes-style readiness probe."""
    try:
        # Check if database is ready
        async for session in get_session():
            await session.execute(text("SELECT 1"))
            break
            
        # Check critical circuit breakers
        if (alchemy_circuit_breaker.state == "open" or 
            thirdweb_circuit_breaker.state == "open"):
            raise HTTPException(
                status_code=503,
                detail="Critical services unavailable (circuit breaker open)"
            )
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Service not ready"
        )


@router.get("/liveness")
async def liveness_check():
    """Kubernetes-style liveness probe."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "N/A"  # Could track actual uptime if needed
    }