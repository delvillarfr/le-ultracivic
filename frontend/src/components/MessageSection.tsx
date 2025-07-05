interface MessageSectionProps {
  messageValue: string;
  onMessageChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
}

export default function MessageSection({ messageValue, onMessageChange }: MessageSectionProps) {
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
          placeholder='And they will say, "This land that was laid waste has become like the garden of Eden" Ezekiel 36:35'
        />
      </div>
    </section>
  );
}