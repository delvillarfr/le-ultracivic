interface HistoryPromptProps {
  className?: string
}

export default function HistoryPrompt({ className = '' }: HistoryPromptProps) {
  return (
    <img 
      src="/media/history-prompt.svg" 
      alt="Your Message to History"
      className={className}
    />
  )
}