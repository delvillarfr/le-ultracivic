'use client'

import LoadingSpinner from './LoadingSpinner'

interface Step {
  id: string
  label: string
  status: 'pending' | 'active' | 'completed' | 'error'
}

interface ProgressStepsProps {
  steps: Step[]
  className?: string
}

export default function ProgressSteps({ steps, className = '' }: ProgressStepsProps) {
  return (
    <div className={`progress-steps ${className}`}>
      {steps.map((step, index) => (
        <div key={step.id} className="step-container">
          <div className={`step-item step-${step.status}`}>
            <div className="step-indicator">
              {step.status === 'active' && (
                <LoadingSpinner size="small" color="#ffffff" />
              )}
              {step.status === 'completed' && (
                <div className="step-checkmark">✓</div>
              )}
              {step.status === 'error' && (
                <div className="step-error">✗</div>
              )}
              {step.status === 'pending' && (
                <div className="step-number">{index + 1}</div>
              )}
            </div>
            <div className="step-label">{step.label}</div>
          </div>
          {index < steps.length - 1 && (
            <div className={`step-connector ${
              step.status === 'completed' ? 'connector-completed' : ''
            }`} />
          )}
        </div>
      ))}
    </div>
  )
}