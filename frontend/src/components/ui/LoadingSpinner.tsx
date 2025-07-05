'use client'

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large'
  color?: string
  className?: string
}

export default function LoadingSpinner({ 
  size = 'medium', 
  color = '#007bff',
  className = ''
}: LoadingSpinnerProps) {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-6 h-6', 
    large: 'w-8 h-8'
  }

  return (
    <div className={`loading-spinner ${sizeClasses[size]} ${className}`}>
      <div 
        className="spinner-ring"
        style={{ borderTopColor: color }}
      />
    </div>
  )
}