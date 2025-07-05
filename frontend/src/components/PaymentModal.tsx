'use client'

import { useState, useEffect } from 'react'
import { usePayment } from '@/hooks/usePayment'
import { useEthPrice } from '@/hooks/useEthPrice'
import { useHistory } from '@/hooks/useHistory'
import { api, ReserveResponse, StatusResponse, pollOrderStatus } from '@/lib/api'
import CONFIG from '@/lib/config'
import ProgressSteps from './ui/ProgressSteps'
import LoadingButton from './ui/LoadingButton'
import LoadingSpinner from './ui/LoadingSpinner'

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
  const { refreshHistory } = useHistory()
  const [orderStatus, setOrderStatus] = useState<StatusResponse | null>(null)
  const [isConfirmingPayment, setIsConfirmingPayment] = useState(false)
  const [confirmError, setConfirmError] = useState<string | null>(null)
  const [isPolling, setIsPolling] = useState(false)

  if (!isOpen) return null

  const ethAmount = calculateEthAmount(allowances)
  const usdAmount = allowances * CONFIG.PRICE_PER_ALLOWANCE_USD

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
          // Refresh history when payment completes successfully
          if (finalStatus.status === 'completed') {
            refreshHistory()
          }
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
  
  const getProgressSteps = () => {
    const state = getPaymentState()
    return [
      {
        id: 'reserve',
        label: 'Reserved',
        status: reservation ? 'completed' : 'pending'
      },
      {
        id: 'payment',
        label: 'Payment',
        status: state === 'ready' ? 'pending' : 
                state === 'pending' || state === 'confirming' ? 'active' :
                ['confirmed', 'confirming_payment', 'processing', 'success'].includes(state) ? 'completed' :
                state === 'error' ? 'error' : 'pending'
      },
      {
        id: 'confirm',
        label: 'Confirming',
        status: state === 'confirming_payment' ? 'active' :
                ['processing', 'success'].includes(state) ? 'completed' :
                state === 'error' ? 'error' : 'pending'
      },
      {
        id: 'complete',
        label: 'Complete',
        status: state === 'processing' ? 'active' :
                state === 'success' ? 'completed' :
                state === 'error' ? 'error' : 'pending'
      }
    ]
  }

  const paymentState = getPaymentState()

  return (
    <div className="modal-overlay">
      <div className="modal-content fade-in">
        <h2>Complete Payment</h2>
        
        <ProgressSteps steps={getProgressSteps()} />
        
        <div className="payment-summary">
          <p><strong>Allowances:</strong> {allowances} tons</p>
          <p><strong>Cost:</strong> ~{ethAmount?.toFixed(6)} ETH (${usdAmount})</p>
          <p><strong>Message:</strong> "{message}"</p>
          {reservation && (
            <p><strong>Order ID:</strong> {reservation.order_id}</p>
          )}
        </div>

        {paymentState === 'ready' && (
          <div className="payment-ready slide-in">
            <p>Click confirm to proceed with payment</p>
            <LoadingButton 
              onClick={handlePayment}
              className="confirm-payment-btn"
              variant="primary"
            >
              Confirm Payment
            </LoadingButton>
          </div>
        )}

        {paymentState === 'pending' && (
          <div className="payment-pending slide-in">
            <LoadingSpinner size="large" />
            <p>Please confirm the transaction in your wallet...</p>
          </div>
        )}

        {paymentState === 'confirmed' && (
          <div className="payment-confirmed">
            <p>Transaction confirmed! Hash: {hash}</p>
          </div>
        )}

        {paymentState === 'confirming' && (
          <div className="payment-confirming slide-in">
            <LoadingSpinner size="large" />
            <p>Confirming transaction...</p>
            <p className="hash-display">Hash: {hash}</p>
          </div>
        )}
        
        {paymentState === 'confirming_payment' && (
          <div className="payment-confirming slide-in">
            <LoadingSpinner size="large" />
            <p>Confirming payment with backend...</p>
            <p className="hash-display">Hash: {hash}</p>
          </div>
        )}
        
        {paymentState === 'processing' && (
          <div className="payment-processing slide-in">
            <LoadingSpinner size="large" />
            <p>Processing retirement...</p>
            <p className="hash-display">Transaction: {hash}</p>
            <p>Status: {orderStatus?.status?.replace('_', ' ')}</p>
          </div>
        )}

        {paymentState === 'success' && (
          <div className="payment-success bounce">
            <div className="success-icon">✓</div>
            <h3>Payment Successful!</h3>
            <p>Your {allowances} CO₂ allowances have been retired.</p>
            <p>You've received {allowances * CONFIG.TOKENS_PER_ALLOWANCE} $PR tokens as proof of your environmental impact!</p>
            <p className="hash-display">Payment Transaction: {hash}</p>
            {orderStatus?.reward_tx_hash && (
              <p className="hash-display">
                PR Token Reward: 
                <a 
                  href={`https://sepolia.etherscan.io/tx/${orderStatus.reward_tx_hash}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="etherscan-link"
                  style={{ marginLeft: '8px' }}
                >
                  {orderStatus.reward_tx_hash.slice(0, 10)}...{orderStatus.reward_tx_hash.slice(-8)}
                </a>
              </p>
            )}
            {orderStatus?.serial_numbers && (
              <div className="serial-numbers">
                <p><strong>Serial Numbers:</strong></p>
                <p className="serial-list">{orderStatus.serial_numbers.join(', ')}</p>
              </div>
            )}
            <p>
              <a 
                href={`https://sepolia.etherscan.io/tx/${hash}`} 
                target="_blank" 
                rel="noopener noreferrer"
                className="etherscan-link"
              >
                View Payment on Etherscan
              </a>
            </p>
            <LoadingButton onClick={onClose} variant="primary">
              Close
            </LoadingButton>
          </div>
        )}

        {paymentState === 'error' && (
          <div className="payment-error slide-in">
            <div className="error-icon">✗</div>
            <h3>Payment Failed</h3>
            <p>{confirmError || transactionError?.message || 'An error occurred'}</p>
            <LoadingButton onClick={onClose} variant="danger">
              Close
            </LoadingButton>
          </div>
        )}

        {paymentState !== 'success' && paymentState !== 'error' && (
          <LoadingButton 
            onClick={onClose} 
            variant="secondary"
            className="cancel-btn"
          >
            Cancel
          </LoadingButton>
        )}
      </div>
    </div>
  )
}