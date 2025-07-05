"""Retry utilities for external API calls."""

import asyncio
import logging
from typing import Any, Callable, Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)


async def retry_async(
    func: Callable,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    context: Optional[str] = None
) -> Any:
    """
    Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retries
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exceptions to catch and retry
        context: Context string for logging
        
    Returns:
        Result of the function call
        
    Raises:
        Last exception if all retries failed
    """
    last_exception = None
    current_delay = delay
    
    for attempt in range(max_retries + 1):
        try:
            result = await func()
            if attempt > 0:
                logger.info(f"Retry succeeded on attempt {attempt + 1}/{max_retries + 1} for {context}")
            return result
            
        except exceptions as e:
            last_exception = e
            
            if attempt < max_retries:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed for {context}: {str(e)}. "
                    f"Retrying in {current_delay:.1f}s..."
                )
                await asyncio.sleep(current_delay)
                current_delay *= backoff
            else:
                logger.error(
                    f"All {max_retries + 1} attempts failed for {context}. "
                    f"Final error: {str(e)}"
                )
    
    raise last_exception


def retry_external_api(max_retries: int = 3, delay: float = 1.0, context: str = None):
    """
    Decorator for retrying external API calls.
    
    Args:
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        context: Context string for logging
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async def call_func():
                return await func(*args, **kwargs)
            
            func_context = context or f"{func.__module__}.{func.__name__}"
            
            return await retry_async(
                func=call_func,
                max_retries=max_retries,
                delay=delay,
                context=func_context,
                exceptions=(Exception,)  # Catch all exceptions for external APIs
            )
        return wrapper
    return decorator


class CircuitBreaker:
    """
    Simple circuit breaker for external services.
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def can_execute(self) -> bool:
        """Check if the circuit breaker allows execution."""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if self.last_failure_time and \
               (asyncio.get_event_loop().time() - self.last_failure_time) > self.recovery_timeout:
                self.state = "half-open"
                return True
            return False
        elif self.state == "half-open":
            return True
        return False
    
    def record_success(self):
        """Record a successful execution."""
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        """Record a failed execution."""
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")


# Global circuit breakers for external services
alchemy_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
thirdweb_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=120)
price_api_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)