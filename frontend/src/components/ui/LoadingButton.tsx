'use client'

import LoadingSpinner from './LoadingSpinner'

interface LoadingButtonProps {
  children: React.ReactNode
  isLoading?: boolean
  disabled?: boolean
  onClick?: () => void
  className?: string
  type?: 'button' | 'submit'
  variant?: 'primary' | 'secondary' | 'danger'
}

export default function LoadingButton({
  children,
  isLoading = false,
  disabled = false,
  onClick,
  className = '',
  type = 'button',
  variant = 'primary'
}: LoadingButtonProps) {
  const baseClasses = 'loading-button'
  const variantClasses = {
    primary: 'btn-primary',
    secondary: 'btn-secondary', 
    danger: 'btn-danger'
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || isLoading}
      className={`${baseClasses} ${variantClasses[variant]} ${className} ${
        isLoading ? 'btn-loading' : ''
      } ${disabled ? 'btn-disabled' : ''}`}
    >
      {isLoading && (
        <LoadingSpinner size="small" color="#ffffff" className="btn-spinner" />
      )}
      <span className={isLoading ? 'btn-text-hidden' : ''}>
        {children}
      </span>
    </button>
  )
}