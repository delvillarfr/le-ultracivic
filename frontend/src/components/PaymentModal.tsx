'use client'

import { useState, useEffect } from 'react'
import { usePayment } from '@/hooks/usePayment'
import { useEthPrice } from '@/hooks/useEthPrice'
import { useHistory } from '@/hooks/useHistory'
import { api, ReserveResponse, StatusResponse, pollOrderStatus } from '@/lib/api'
import CONFIG from '@/lib/config'
import ProgressSteps from './ui/ProgressSteps'

interface Step {
  id: string
  label: string
  status: 'pending' | 'active' | 'completed' | 'error'
}
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
  // Always call hooks first, regardless of isOpen
  const { ethPriceUSD } = useEthPrice()
  const { refreshHistory } = useHistory()
  const [orderStatus, setOrderStatus] = useState<StatusResponse | null>(null)
  const [isConfirmingPayment, setIsConfirmingPayment] = useState(false)
  const [confirmError, setConfirmError] = useState<string | null>(null)
  const [isPolling, setIsPolling] = useState(false)

  if (!isOpen) return null

  // Demo mode - calculate ETH amount directly
  const ethAmount = ethPriceUSD ? (allowances * CONFIG.PRICE_PER_ALLOWANCE_USD) / ethPriceUSD : null
  const usdAmount = allowances * CONFIG.PRICE_PER_ALLOWANCE_USD

  const handlePayment = async () => {
    // Demo mode - just show success after 2 seconds
    setTimeout(() => {
      onClose()
    }, 2000)
  }

  const getPaymentState = () => {
    // Demo mode - just show ready state
    return 'ready'
  }
  
  const getProgressSteps = (): Step[] => {
    return [
      {
        id: 'reserve',
        label: 'Reserved',
        status: 'completed'
      },
      {
        id: 'payment',
        label: 'Payment',
        status: 'active'
      },
      {
        id: 'confirm',
        label: 'Confirming',
        status: 'pending'
      },
      {
        id: 'complete',
        label: 'Complete',
        status: 'pending'
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
        </div>

        <div className="payment-ready slide-in">
          <p>Demo mode - Click confirm to close modal</p>
          <LoadingButton 
            onClick={handlePayment}
            className="confirm-payment-btn"
            variant="primary"
          >
            Confirm Payment
          </LoadingButton>
        </div>

        <LoadingButton 
          onClick={onClose} 
          variant="secondary"
          className="cancel-btn"
        >
          Cancel
        </LoadingButton>
      </div>
    </div>
  )
}