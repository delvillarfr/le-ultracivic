"""Background task manager for orchestrating all background services."""

import asyncio
import logging
from typing import Dict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.services.cleanup_service import cleanup_service
from app.services.transaction_monitor import transaction_monitor

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """Manager for all background tasks and scheduled jobs."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    async def start(self) -> None:
        """Start all background tasks and scheduled jobs."""
        if self.is_running:
            logger.warning("Background task manager is already running")
            return

        try:
            logger.info("Starting background task manager")

            # Add cleanup job every 20 minutes
            self.scheduler.add_job(
                func=self._run_cleanup_job,
                trigger=IntervalTrigger(minutes=20),
                id="cleanup_expired_reservations",
                name="Cleanup expired reservations",
                replace_existing=True
            )

            # Add transaction monitoring job every 30 seconds
            self.scheduler.add_job(
                func=self._run_transaction_monitoring,
                trigger=IntervalTrigger(seconds=30),
                id="monitor_transactions",
                name="Monitor pending transactions",
                replace_existing=True
            )

            # Start the scheduler
            self.scheduler.start()
            self.is_running = True

            logger.info("Background task manager started successfully")

        except Exception as e:
            logger.error(f"Error starting background task manager: {str(e)}")
            raise

    async def stop(self) -> None:
        """Stop all background tasks and scheduled jobs."""
        if not self.is_running:
            logger.warning("Background task manager is not running")
            return

        try:
            logger.info("Stopping background task manager")

            self.scheduler.shutdown(wait=True)
            self.is_running = False

            logger.info("Background task manager stopped successfully")

        except Exception as e:
            logger.error(f"Error stopping background task manager: {str(e)}")
            raise

    async def _run_cleanup_job(self) -> None:
        """Run the cleanup job (called by scheduler)."""
        try:
            logger.info("Running scheduled cleanup job")
            result = await cleanup_service.full_cleanup()
            
            if result["success"]:
                logger.info(f"Cleanup job completed: {result['message']}")
            else:
                logger.error(f"Cleanup job failed: {result.get('error')}")
                
                # Send email alert for cleanup failures
                try:
                    from app.services.email import email_service
                    await email_service.send_system_error_alert(
                        error_type="cleanup_job_failed",
                        error_message=result.get('error', 'Unknown cleanup error'),
                        context={"cleanup_result": result}
                    )
                except Exception as email_error:
                    logger.error(f"Failed to send cleanup failure alert: {email_error}")
                
        except Exception as e:
            logger.error(f"Error in cleanup job: {str(e)}")
            
            # Send email alert for cleanup exceptions
            try:
                from app.services.email import email_service
                await email_service.send_system_error_alert(
                    error_type="cleanup_job_exception",
                    error_message=str(e),
                    context={"exception_type": type(e).__name__}
                )
            except Exception as email_error:
                logger.error(f"Failed to send cleanup exception alert: {email_error}")

    async def _run_transaction_monitoring(self) -> None:
        """Run transaction monitoring (called by scheduler)."""
        try:
            logger.debug("Running transaction monitoring")
            await transaction_monitor.monitor_pending_transactions()
            
        except Exception as e:
            logger.error(f"Error in transaction monitoring: {str(e)}")

    async def run_cleanup_now(self) -> Dict[str, any]:
        """Manually trigger cleanup job."""
        try:
            logger.info("Manually triggering cleanup job")
            result = await cleanup_service.full_cleanup()
            return result
            
        except Exception as e:
            logger.error(f"Error in manual cleanup: {str(e)}")
            return {
                "success": False,
                "error": f"Manual cleanup error: {str(e)}"
            }

    async def run_transaction_check_now(self) -> Dict[str, any]:
        """Manually trigger transaction monitoring."""
        try:
            logger.info("Manually triggering transaction monitoring")
            await transaction_monitor.monitor_pending_transactions()
            return {
                "success": True,
                "message": "Transaction monitoring completed"
            }
            
        except Exception as e:
            logger.error(f"Error in manual transaction check: {str(e)}")
            return {
                "success": False,
                "error": f"Manual transaction check error: {str(e)}"
            }

    async def get_status(self) -> Dict[str, any]:
        """Get status of background task manager and scheduled jobs."""
        try:
            jobs = []
            if self.is_running and self.scheduler:
                for job in self.scheduler.get_jobs():
                    jobs.append({
                        "id": job.id,
                        "name": job.name,
                        "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                        "trigger": str(job.trigger)
                    })

            # Get cleanup stats
            cleanup_stats = await cleanup_service.get_cleanup_stats()

            return {
                "success": True,
                "is_running": self.is_running,
                "scheduled_jobs": jobs,
                "cleanup_stats": cleanup_stats.get("stats", {}),
                "cleanup_thresholds": cleanup_stats.get("cleanup_thresholds", {})
            }

        except Exception as e:
            logger.error(f"Error getting background task status: {str(e)}")
            return {
                "success": False,
                "error": f"Status error: {str(e)}",
                "is_running": self.is_running
            }

    async def process_payment_background(self, order_id: str) -> None:
        """
        Process payment in background (triggered by API endpoint).
        This is called by FastAPI BackgroundTasks.
        """
        try:
            logger.info(f"Processing payment in background for order {order_id}")
            
            # Give the transaction a moment to propagate
            await asyncio.sleep(5)
            
            # Process the order
            result = await transaction_monitor.process_single_order(order_id)
            
            if result["success"]:
                logger.info(f"Background payment processing completed for order {order_id}")
            else:
                logger.warning(f"Background payment processing incomplete for order {order_id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error in background payment processing for order {order_id}: {str(e)}")


# Global instance
background_manager = BackgroundTaskManager()