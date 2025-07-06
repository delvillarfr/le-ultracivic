import { useState, useRef } from 'react';

interface HeroSectionProps {
  allowanceValue: number;
  inputValue: string;
  onAllowanceChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onAllowanceBlur: () => void;
}

export default function HeroSection({ allowanceValue, inputValue, onAllowanceChange, onAllowanceBlur }: HeroSectionProps) {
  const [hasInteracted, setHasInteracted] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleInputClick = () => {
    setHasInteracted(true);
  };

  const handleInputFocus = () => {
    setHasInteracted(true);
  };

  return (
    <section className="hero-section">
      <div className="hero-line">
        <img src="/media/hero1.svg" alt="Buy + Retire Polluters' Legal Rights" className="hero1" />
      </div>
      <div className="hero-line">
        <img src="/media/hero2-1.svg" alt="to Emit" className="hero2-1" />
        <div className="allowance-input-wrapper">
          <input 
            ref={inputRef}
            type="number" 
            value={inputValue} 
            onChange={onAllowanceChange}
            onBlur={onAllowanceBlur}
            onClick={handleInputClick}
            onFocus={handleInputFocus}
            className="allowance-input"
            min="1"
            max="99"
          />
          {!hasInteracted && <span className="blinking-cursor">|</span>}
        </div>
        <img src="/media/hero2-2.svg" alt="Tons of CO2." className="hero2-2" />
      </div>
    </section>
  );
}