'use client'

import { useState, useEffect } from 'react'
import { usePayment } from '@/hooks/usePayment'
import { useEthPrice } from '@/hooks/useEthPrice'
import { api, ReserveResponse, StatusResponse, pollOrderStatus } from '@/lib/api'

interface PaymentModalProps {
  isOpen: boolean
  onClose: () => void
  allowances: number
  message: string
  reservation: ReserveResponse | null
}

export default function PaymentModal({ isOpen, onClose, allowances, message, reservation }: PaymentModalProps) {
  const { initiatePayment, hash, isTransactionPending, isConfirming, isConfirmed, transactionError, calculateEthAmount } = usePayment()
  const { ethPriceUSD } = useEthPrice()
  const [orderStatus, setOrderStatus] = useState<StatusResponse | null>(null)
  const [isConfirmingPayment, setIsConfirmingPayment] = useState(false)
  const [confirmError, setConfirmError] = useState<string | null>(null)
  const [isPolling, setIsPolling] = useState(false)

  if (!isOpen) return null

  const ethAmount = calculateEthAmount(allowances)
  const usdAmount = allowances * 24

  const handlePayment = async () => {
    if (!reservation) {
      console.error('No reservation found')
      return
    }
    
    try {
      await initiatePayment(allowances)
    } catch (error) {
      console.error('Payment failed:', error)
    }
  }
  
  // Confirm payment with backend after transaction is sent
  useEffect(() => {
    if (hash && reservation && !isConfirmingPayment && !orderStatus) {
      confirmPaymentWithBackend()
    }
  }, [hash, reservation, isConfirmingPayment, orderStatus])
  
  const confirmPaymentWithBackend = async () => {
    if (!hash || !reservation) return
    
    setIsConfirmingPayment(true)
    setConfirmError(null)
    
    try {
      await api.confirmPayment({
        txHash: hash,
        order_id: reservation.order_id
      })
      
      // Start polling for status
      setIsPolling(true)
      pollOrderStatus(
        reservation.order_id,
        (status) => setOrderStatus(status),
        (finalStatus) => {
          setOrderStatus(finalStatus)
          setIsPolling(false)
        },
        (error) => {
          setConfirmError(error.message)
          setIsPolling(false)
        }
      )
    } catch (error) {
      setConfirmError(error instanceof Error ? error.message : 'Failed to confirm payment')
    } finally {
      setIsConfirmingPayment(false)
    }
  }

  const getPaymentState = () => {
    if (confirmError || transactionError) return 'error'
    if (orderStatus?.status === 'completed') return 'success'
    if (isPolling || orderStatus?.status === 'paid_but_not_retired') return 'processing'
    if (isConfirmingPayment) return 'confirming_payment'
    if (isConfirmed || hash) return 'confirmed'
    if (isConfirming) return 'confirming'
    if (isTransactionPending) return 'pending'
    return 'ready'
  }

  const paymentState = getPaymentState()

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Complete Payment</h2>
        
        <div className="payment-summary">
          <p><strong>Allowances:</strong> {allowances} tons</p>
          <p><strong>Cost:</strong> ~{ethAmount?.toFixed(6)} ETH (${usdAmount})</p>
          <p><strong>Message:</strong> "{message}"</p>
          {reservation && (
            <p><strong>Order ID:</strong> {reservation.order_id}</p>
          )}
        </div>

        {paymentState === 'ready' && (
          <div className="payment-ready">
            <p>Click confirm to proceed with payment</p>
            <button onClick={handlePayment} className="confirm-payment-btn">
              Confirm Payment
            </button>
          </div>
        )}

        {paymentState === 'pending' && (
          <div className="payment-pending">
            <p>Please confirm the transaction in your wallet...</p>
          </div>
        )}

        {paymentState === 'confirmed' && (
          <div className="payment-confirmed">
            <p>Transaction confirmed! Hash: {hash}</p>
          </div>
        )}

        {paymentState === 'confirming' && (
          <div className="payment-confirming">
            <p>Confirming transaction...</p>
            <p>Hash: {hash}</p>
          </div>
        )}
        
        {paymentState === 'confirming_payment' && (
          <div className="payment-confirming">
            <p>Confirming payment with backend...</p>
            <p>Hash: {hash}</p>
          </div>
        )}
        
        {paymentState === 'processing' && (
          <div className="payment-processing">
            <p>Processing retirement...</p>
            <p>Transaction: {hash}</p>
            <p>Status: {orderStatus?.status}</p>
          </div>
        )}

        {paymentState === 'success' && (
          <div className="payment-success">
            <h3>Payment Successful!</h3>
            <p>Your {allowances} CO₂ allowances have been retired.</p>
            <p>Transaction: {hash}</p>
            {orderStatus?.serial_numbers && (
              <div>
                <p><strong>Serial Numbers:</strong></p>
                <p>{orderStatus.serial_numbers.join(', ')}</p>
              </div>
            )}
            <p>
              <a 
                href={`https://sepolia.etherscan.io/tx/${hash}`} 
                target="_blank" 
                rel="noopener noreferrer"
                className="etherscan-link"
              >
                View on Etherscan
              </a>
            </p>
            <button onClick={onClose} className="close-btn">
              Close
            </button>
          </div>
        )}

        {paymentState === 'error' && (
          <div className="payment-error">
            <h3>Payment Failed</h3>
            <p>{confirmError || transactionError?.message || 'An error occurred'}</p>
            <button onClick={onClose} className="close-btn">
              Close
            </button>
          </div>
        )}

        {paymentState !== 'success' && paymentState !== 'error' && (
          <button onClick={onClose} className="cancel-btn">
            Cancel
          </button>
        )}
      </div>
    </div>
  )
}