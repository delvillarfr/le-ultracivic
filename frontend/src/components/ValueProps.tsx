interface ValuePropsProps {
  priceCalc: number;
  tokenCalc: number;
  impactCalc: number;
  allowanceValue: number;
}

export default function ValueProps({ priceCalc, tokenCalc, impactCalc, allowanceValue }: ValuePropsProps) {
  
  return (
    <section className="value-props">
      <div className="vp-line">
        <img src="/media/vp1-1.svg" alt="Pay" className="vp1-1" />
        <span className="price-value">
          <span>{priceCalc.toLocaleString()}</span>
        </span>
        <img src="/media/vp1-2.svg" alt=";" className="vp1-2" />
        <img src="/media/vp2-1.svg" alt="Earn" className="vp2-1" />
        <span className="token-value">
          <span>{tokenCalc.toLocaleString()}</span>
        </span>
        <img src="/media/vp2-2.svg" alt="PR;" className="vp2-2" />
      </div>
      <div className="vp-line">
        <img src="/media/vp3-1.svg" alt="Improve the World by" className="vp3-1" />
        <span className="impact-value">
          <span>{impactCalc.toLocaleString()}</span>
        </span>
        <img src="/media/vp3-2.svg" alt="." className="vp3-2" />
      </div>
    </section>
  );
}