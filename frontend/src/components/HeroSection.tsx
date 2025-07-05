interface HeroSectionProps {
  allowanceValue: number;
  onAllowanceChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export default function HeroSection({ allowanceValue, onAllowanceChange }: HeroSectionProps) {
  return (
    <section className="hero-section">
      <div className="hero-line">
        <img src="/media/hero1.svg" alt="Buy + Retire Polluters' Legal Rights" className="hero1" />
      </div>
      <div className="hero-line">
        <img src="/media/hero2-1.svg" alt="to Emit" className="hero2-1" />
        <input 
          type="number" 
          value={allowanceValue} 
          onChange={onAllowanceChange}
          className="allowance-input"
        />
        <img src="/media/hero2-2.svg" alt="Tons of CO2." className="hero2-2" />
      </div>
    </section>
  );
}