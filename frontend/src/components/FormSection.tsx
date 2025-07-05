'use client'

import { useState } from 'react'

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
    <div className="space-y-6">
      <div>
        <label htmlFor="numAllowances" className="block text-sm font-medium text-gray-700 mb-2">
          How many allowances?
        </label>
        <input
          type="number"
          id="numAllowances"
          min="1"
          max="99"
          value={numAllowances}
          onChange={handleNumAllowancesChange}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.numAllowances ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Enter number (1-99)"
        />
        {errors.numAllowances && (
          <p className="text-red-500 text-sm mt-1">{errors.numAllowances}</p>
        )}
      </div>

      <div>
        <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
          Your Message to History:
        </label>
        <textarea
          id="message"
          value={message}
          onChange={handleMessageChange}
          rows={4}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${
            errors.message ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="they will say, 'This land that was laid waste has become like the garden of Eden' Ezequiel 36:35"
        />
        <div className="flex justify-between items-center mt-1">
          <span className={`text-sm ${message.length > 100 ? 'text-red-500' : 'text-gray-500'}`}>
            {message.length}/100 characters
          </span>
          {errors.message && (
            <p className="text-red-500 text-sm">{errors.message}</p>
          )}
        </div>
      </div>
    </div>
  )
}