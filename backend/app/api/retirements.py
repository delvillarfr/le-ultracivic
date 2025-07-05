from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.middleware.rate_limit import limiter
from app.models.allowances import Allowance
from app.schemas.retirements import (
    ConfirmPaymentRequest,
    ConfirmPaymentResponse,
    OrderStatus,
    OrderStatusResponse,
    RetirementRequest,
    RetirementResponse,
)
from app.services.blockchain import blockchain_service

router = APIRouter(prefix="/retirements", tags=["retirements"])


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
            .where(Allowance.status == "available")
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
            allowance.status = "reserved"
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
    session: AsyncSession = Depends(get_session),
):
    """Confirm payment was sent for an order"""
    try:
        # Verify order exists and is in reserved status
        stmt = select(Allowance).where(Allowance.order_id == str(confirm_request.order_id))
        result = await session.execute(stmt)
        allowances = result.scalars().all()

        if not allowances:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

        first_allowance = allowances[0]
        if first_allowance.status != "reserved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order is not in reserved status: {first_allowance.status}"
            )

        # Store transaction hash in database
        for allowance in allowances:
            allowance.tx_hash = confirm_request.tx_hash

        await session.commit()

        # Process payment confirmation in background
        # For now, just store the tx_hash and return success
        # The background task will verify payment and distribute tokens

        return ConfirmPaymentResponse(
            message="Payment confirmation received and is being processed",
            status="processing"
        )

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
        if first_allowance.status == "reserved":
            if first_allowance.tx_hash and first_allowance.reward_tx_hash:
                status_value = OrderStatus.PAID_BUT_NOT_RETIRED
            elif first_allowance.tx_hash:
                status_value = OrderStatus.PAID_BUT_NOT_RETIRED
            else:
                status_value = OrderStatus.PENDING
        elif first_allowance.status == "retired":
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
