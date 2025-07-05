'use client'

import { usePayment } from '@/hooks/usePayment'
import { useEthPrice } from '@/hooks/useEthPrice'

interface PaymentModalProps {
  isOpen: boolean
  onClose: () => void
  allowances: number
  message: string
}

export default function PaymentModal({ isOpen, onClose, allowances, message }: PaymentModalProps) {
  const { initiatePayment, hash, isTransactionPending, isConfirming, isConfirmed, transactionError, calculateEthAmount } = usePayment()
  const { ethPriceUSD } = useEthPrice()

  if (!isOpen) return null

  const ethAmount = calculateEthAmount(allowances)
  const usdAmount = allowances * 24

  const handlePayment = async () => {
    try {
      await initiatePayment(allowances)
    } catch (error) {
      console.error('Payment failed:', error)
    }
  }

  const getPaymentState = () => {
    if (transactionError) return 'error'
    if (isConfirmed) return 'success'
    if (isConfirming) return 'confirming'
    if (isTransactionPending) return 'pending'
    if (hash) return 'sent'
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

        {paymentState === 'sent' && (
          <div className="payment-sent">
            <p>Transaction sent! Hash: {hash}</p>
          </div>
        )}

        {paymentState === 'confirming' && (
          <div className="payment-confirming">
            <p>Confirming transaction...</p>
            <p>Hash: {hash}</p>
          </div>
        )}

        {paymentState === 'success' && (
          <div className="payment-success">
            <h3>Payment Successful!</h3>
            <p>Your {allowances} CO₂ allowances have been retired.</p>
            <p>Transaction: {hash}</p>
            <button onClick={onClose} className="close-btn">
              Close
            </button>
          </div>
        )}

        {paymentState === 'error' && (
          <div className="payment-error">
            <h3>Payment Failed</h3>
            <p>{transactionError?.message || 'An error occurred'}</p>
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