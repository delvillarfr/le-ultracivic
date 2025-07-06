import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.middleware.rate_limit import limiter
from app.models.allowances import Allowance, AllowanceStatus
from app.schemas.retirements import (
    ConfirmPaymentRequest,
    ConfirmPaymentResponse,
    HistoryResponse,
    OrderStatus,
    OrderStatusResponse,
    RetirementRequest,
    RetirementResponse,
)
from app.services.background_manager import background_manager
from app.services.blockchain import blockchain_service
from app.services.payment_validator import payment_validator
from app.services.price_service import price_service
from app.services.reward_calculator import reward_calculator

router = APIRouter(prefix="/retirements", tags=["retirements"])
logger = logging.getLogger(__name__)


@router.get("/estimate/{num_allowances}")
async def get_payment_estimate(
    request: Request,
    num_allowances: int
):
    """Get payment estimate for given number of allowances."""
    try:
        if num_allowances < 1 or num_allowances > 99:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Number of allowances must be between 1 and 99"
            )
        
        # Get payment estimate
        payment_estimate = await price_service.get_payment_estimate(num_allowances)
        
        if not payment_estimate["success"]:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to get payment estimate: {payment_estimate.get('error')}"
            )
        
        # Get reward summary
        reward_summary = reward_calculator.get_reward_summary(num_allowances)
        
        if not reward_summary["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unable to calculate rewards: {reward_summary.get('error')}"
            )
        
        return {
            "success": True,
            "num_allowances": num_allowances,
            "payment_estimate": payment_estimate["estimate"],
            "reward_summary": reward_summary["reward_summary"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get estimate: {str(e)}",
        ) from e


@router.post("/", response_model=RetirementResponse)
@limiter.limit("5/minute")
async def create_retirement(
    request: Request,
    retirement_request: RetirementRequest,
    session: AsyncSession = Depends(get_session),
):
    """Reserve allowances for retirement"""
    try:
        # Find and lock available allowances
        stmt = (
            select(Allowance)
            .where(Allowance.status == AllowanceStatus.AVAILABLE)
            .limit(retirement_request.num_allowances)
            .with_for_update(skip_locked=True)
        )

        result = await session.execute(stmt)
        allowances = result.scalars().all()

        if len(allowances) < retirement_request.num_allowances:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {len(allowances)} allowances available, but {retirement_request.num_allowances} requested",
            )

        # Generate order ID and reserve allowances
        order_id = uuid4()

        for allowance in allowances:
            allowance.status = AllowanceStatus.RESERVED
            allowance.order_id = str(order_id)
            allowance.wallet = retirement_request.wallet
            allowance.message = retirement_request.message

        await session.commit()

        return RetirementResponse(order_id=order_id)

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reserve allowances: {str(e)}",
        ) from e


@router.post("/confirm", response_model=ConfirmPaymentResponse)
@limiter.limit("5/minute")
async def confirm_payment(
    request: Request,
    confirm_request: ConfirmPaymentRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Confirm payment was sent for an order with enhanced validation"""
    order_id = str(confirm_request.order_id)
    tx_hash = confirm_request.tx_hash
    
    logger.info(
        f"CRITICAL: Payment confirmation received | "
        f"order_id={order_id} | tx_hash={tx_hash} | "
        f"client_ip={request.client.host if request.client else 'unknown'}"
    )
    
    try:
        # Verify order exists and is in reserved status
        stmt = select(Allowance).where(Allowance.order_id == order_id)
        result = await session.execute(stmt)
        allowances = result.scalars().all()

        if not allowances:
            logger.error(f"CRITICAL: Order not found | order_id={order_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

        first_allowance = allowances[0]
        if first_allowance.status != AllowanceStatus.RESERVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order is not in reserved status: {first_allowance.status}"
            )

        # Check for duplicate transaction hash
        if first_allowance.tx_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already confirmed for this order"
            )

        num_allowances = len(allowances)
        tx_hash = confirm_request.tx_hash

        # Enhanced payment validation
        logger.info(
            f"CRITICAL: Starting payment validation | "
            f"order_id={order_id} | tx_hash={tx_hash} | "
            f"num_allowances={num_allowances} | wallet={first_allowance.wallet}"
        )
        
        validation_result = await payment_validator.validate_payment_transaction(
            tx_hash=tx_hash,
            num_allowances=num_allowances
        )

        if not validation_result["success"]:
            logger.error(
                f"CRITICAL: Payment validation failed | "
                f"order_id={order_id} | tx_hash={tx_hash} | "
                f"error={validation_result.get('error')}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment validation failed: {validation_result.get('error')}",
            )

        if not validation_result.get("valid", False):
            # Handle pending transactions
            if validation_result.get("status") == "pending":
                raise HTTPException(
                    status_code=status.HTTP_202_ACCEPTED,
                    detail="Transaction is pending confirmation. Please wait and try again.",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid payment: {validation_result.get('error')}",
                )

        # Store transaction hash and payment details in database
        for allowance in allowances:
            allowance.tx_hash = confirm_request.tx_hash

        await session.commit()
        
        logger.info(
            f"CRITICAL: Payment confirmed and stored | "
            f"order_id={order_id} | tx_hash={tx_hash} | "
            f"wallet={first_allowance.wallet} | num_allowances={num_allowances} | "
            f"triggering_background_processing=True"
        )

        # Trigger background payment processing
        background_tasks.add_task(
            background_manager.process_payment_background,
            order_id
        )

        # Get payment details for response
        payment_details = validation_result.get("payment_details", {})
        
        return {
            "message": "Payment confirmed and verified successfully",
            "status": "processing",
            "order_id": str(confirm_request.order_id),
            "payment_details": {
                "tx_hash": tx_hash,
                "amount_eth": payment_details.get("amount_eth"),
                "block_number": payment_details.get("block_number"),
                "num_allowances": num_allowances
            },
            "next_steps": "Your allowances are being retired and reward tokens are being distributed. Check order status for updates."
        }

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm payment: {str(e)}",
        ) from e


@router.get("/status/{order_id}", response_model=OrderStatusResponse)
@limiter.limit("10/minute")
async def get_order_status(
    request: Request, order_id: UUID, session: AsyncSession = Depends(get_session)
):
    """Get the status of an order"""
    try:
        stmt = select(Allowance).where(Allowance.order_id == str(order_id))
        result = await session.execute(stmt)
        allowances = result.scalars().all()

        if not allowances:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

        # Determine status based on allowance states
        first_allowance = allowances[0]

        # Determine status based on allowance state and transaction hashes
        if first_allowance.status == AllowanceStatus.RESERVED:
            if first_allowance.tx_hash and first_allowance.reward_tx_hash:
                status_value = OrderStatus.PAID_BUT_NOT_RETIRED
            elif first_allowance.tx_hash:
                status_value = OrderStatus.PAID_BUT_NOT_RETIRED
            else:
                status_value = OrderStatus.PENDING
        elif first_allowance.status == AllowanceStatus.RETIRED:
            status_value = OrderStatus.COMPLETED
        else:
            status_value = OrderStatus.ERROR

        serial_numbers = (
            [a.serial_number for a in allowances]
            if status_value == OrderStatus.COMPLETED
            else None
        )

        return OrderStatusResponse(
            order_id=order_id,
            status=status_value,
            serial_numbers=serial_numbers,
            message=first_allowance.message,
            tx_hash=first_allowance.tx_hash,
            reward_tx_hash=first_allowance.reward_tx_hash,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get order status: {str(e)}",
        ) from e


@router.get("/history", response_model=HistoryResponse)
@limiter.limit("30/minute")
async def get_retirement_history(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    """Get history of retired allowances grouped by retirement orders"""
    try:
        # Get all retired allowances grouped by order_id
        stmt = (
            select(Allowance)
            .where(Allowance.status == AllowanceStatus.RETIRED, Allowance.order_id.is_not(None))
            .order_by(Allowance.updated_at.desc())
        )
        
        result = await session.execute(stmt)
        all_retired_allowances = result.scalars().all()
        
        # Group allowances by order_id
        orders_dict = {}
        for allowance in all_retired_allowances:
            order_id = allowance.order_id
            if order_id not in orders_dict:
                orders_dict[order_id] = {
                    "allowances": [],
                    "timestamp": allowance.updated_at,
                    "message": allowance.message,
                    "wallet": allowance.wallet,
                    "reward_tx_hash": allowance.reward_tx_hash
                }
            orders_dict[order_id]["allowances"].append(allowance)
            
            # Use the most recent timestamp for the order
            if allowance.updated_at > orders_dict[order_id]["timestamp"]:
                orders_dict[order_id]["timestamp"] = allowance.updated_at

        # Sort orders by timestamp (most recent first) and apply pagination
        sorted_orders = sorted(
            orders_dict.items(), 
            key=lambda x: x[1]["timestamp"], 
            reverse=True
        )
        
        total_orders = len(sorted_orders)
        paginated_orders = sorted_orders[offset:offset + limit]

        # Build history items
        history_items = []
        for order_id, order_data in paginated_orders:
            # Generate Etherscan link for reward transaction
            etherscan_link = None
            if order_data["reward_tx_hash"]:
                etherscan_link = f"https://sepolia.etherscan.io/tx/{order_data['reward_tx_hash']}"
            
            # Collect all serial numbers for this order
            serial_numbers = [allowance.serial_number for allowance in order_data["allowances"]]
            
            history_items.append({
                "serial_numbers": serial_numbers,
                "message": order_data["message"],
                "wallet": order_data["wallet"],
                "timestamp": order_data["timestamp"].isoformat(),
                "etherscan_link": etherscan_link,
                "order_id": order_id
            })

        return HistoryResponse(
            retirements=history_items,
            total=total_orders
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get retirement history: {str(e)}",
        ) from e


# Admin endpoints for background task management
@router.get("/admin/background-status")
async def get_background_status(request: Request):
    """Get background task status (admin endpoint)."""
    try:
        status_info = await background_manager.get_status()
        return status_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get background status: {str(e)}",
        ) from e


@router.post("/admin/cleanup-now")
async def trigger_cleanup_now(request: Request):
    """Manually trigger cleanup job (admin endpoint)."""
    try:
        result = await background_manager.run_cleanup_now()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger cleanup: {str(e)}",
        ) from e


@router.post("/admin/check-transactions-now")
async def trigger_transaction_check_now(request: Request):
    """Manually trigger transaction monitoring (admin endpoint)."""
    try:
        result = await background_manager.run_transaction_check_now()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger transaction check: {str(e)}",
        ) from e
