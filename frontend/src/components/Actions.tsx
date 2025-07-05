interface ActionsProps {
  onDoItClick: () => void;
  onWhatClick: () => void;
}

export default function Actions({ onDoItClick, onWhatClick }: ActionsProps) {
  return (
    <section className="actions">
      <button className="action-btn" onClick={onDoItClick}>
        <img src="/media/doit.svg" alt="Do It" className="doit" />
      </button>
      <button className="action-btn" onClick={onWhatClick}>
        <img src="/media/what.svg" alt="What?" className="what" />
      </button>
    </section>
  );
}