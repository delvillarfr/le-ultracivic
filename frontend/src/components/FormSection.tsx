'use client'

import { useState } from 'react'
import { HistoryPrompt } from './svg'

export default function FormSection() {
  const [numAllowances, setNumAllowances] = useState<string>('')
  const [message, setMessage] = useState<string>('')
  const [errors, setErrors] = useState<{numAllowances?: string, message?: string}>({})

  const validateNumAllowances = (value: string): boolean => {
    const num = parseInt(value, 10)
    return !isNaN(num) && num >= 1 && num <= 99
  }

  const validateMessage = (value: string): boolean => {
    return value.length <= 100
  }

  const handleNumAllowancesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setNumAllowances(value)
    
    if (value && !validateNumAllowances(value)) {
      setErrors(prev => ({ ...prev, numAllowances: 'Must be between 1 and 99' }))
    } else {
      setErrors(prev => ({ ...prev, numAllowances: undefined }))
    }
  }

  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value
    setMessage(value)
    
    if (!validateMessage(value)) {
      setErrors(prev => ({ ...prev, message: 'Message cannot exceed 100 characters' }))
    } else {
      setErrors(prev => ({ ...prev, message: undefined }))
    }
  }

  return (
    <div className="text-center space-y-2">
      <HistoryPrompt className="mx-auto mb-2" />
      
      <div className="relative inline-block">
        <img 
          src="/media/history-prompt-box.svg" 
          alt="Message Box"
          className="w-full max-w-md mx-auto"
        />
        <textarea
          id="message"
          value={message}
          onChange={handleMessageChange}
          rows={4}
          className="absolute bg-transparent border-none outline-none resize-none text-center"
          style={{ 
            fontFamily: 'Atkinson Hyperlegible',
            fontSize: '14px',
            lineHeight: '1.2',
            top: '20px',
            left: '20px',
            right: '20px',
            bottom: '20px',
            width: 'calc(100% - 40px)',
            height: 'calc(100% - 40px)',
            color: '#333'
          }}
          placeholder="they will say, 'This land that was laid waste has become like the garden of Eden' Ezequiel 36:35"
        />
        {errors.message && (
          <p className="text-red-500 text-xs mt-1">{errors.message}</p>
        )}
        <div className="mt-1 text-xs text-gray-500">
          {message.length}/100 characters
        </div>
      </div>
    </div>
  )
}