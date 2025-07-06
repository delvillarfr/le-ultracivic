import { useState } from 'react';
import CONFIG from '@/lib/config';

interface MessageSectionProps {
  messageValue: string;
  onMessageChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
}

export default function MessageSection({ messageValue, onMessageChange }: MessageSectionProps) {
  const maxLength = CONFIG.MAX_MESSAGE_LENGTH;
  const remaining = maxLength - messageValue.length;
  const [hasClicked, setHasClicked] = useState(false);

  const handleClick = () => {
    setHasClicked(true);
  };

  const handleFocus = () => {
    setHasClicked(true);
  };

  return (
    <section className="message-section">
      <div className="message-prompt">
        <img src="/media/history-prompt.svg" alt="Your Message to History:" className="history-prompt" />
      </div>
      <div className="message-input-container">
        <img src="/media/history-prompt-box.svg" alt="Message box" className="message-box" />
        <textarea 
          value={messageValue}
          onChange={onMessageChange}
          onClick={handleClick}
          onFocus={handleFocus}
          placeholder={hasClicked ? '' : 'And they will say, "This land that was laid waste has become like the garden of Eden" Ezekiel 36:35'}
          maxLength={maxLength}
        />
        {messageValue.length > 0 && (
          <div className="character-counter">
            {remaining} characters remaining
          </div>
        )}
      </div>
    </section>
  );
}