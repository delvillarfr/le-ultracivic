'use client'

import { useEffect } from 'react'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function Modal({ isOpen, onClose }: ModalProps) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-auto">
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-2xl bg-white rounded-lg shadow-xl">
          <div className="flex items-center justify-between p-6 border-b">
            <h2 className="text-2xl font-bold text-gray-900">
              What is Ultra Civic?
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
              aria-label="Close modal"
            >
              ×
            </button>
          </div>
          
          <div className="p-6 space-y-4">
            <p className="text-gray-700 leading-relaxed">
              Ultra Civic allows you to buy and retire pollution allowances, directly reducing the amount of CO₂ that industries can legally emit into the atmosphere.
            </p>
            
            <p className="text-gray-700 leading-relaxed">
              When you purchase allowances through Ultra Civic:
            </p>
            
            <ul className="list-disc pl-6 space-y-2 text-gray-700">
              <li>You pay $24 per allowance (each allowing 1 ton of CO₂ emissions)</li>
              <li>We permanently retire those allowances from the cap-and-trade system</li>
              <li>This creates a direct, measurable reduction in allowed emissions</li>
              <li>You receive $PR tokens as a reward for your environmental action</li>
              <li>Your message is recorded in our public history</li>
            </ul>
            
            <p className="text-gray-700 leading-relaxed">
              The transaction is recorded on the blockchain for transparency, and the retired allowances can never be used again to pollute.
            </p>
            
            <p className="text-sm text-gray-500 mt-4">
              This is a direct action that makes a real difference in reducing carbon emissions.
            </p>
          </div>
          
          <div className="flex justify-end p-6 border-t">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Got it!
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}