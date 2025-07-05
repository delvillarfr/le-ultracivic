export default function HistoryTable() {
  return (
    <section className="history">
      <div className="history-title">
        <img src="/media/table-title.svg" alt="History" className="table-title" />
      </div>
      <div className="history-table">
        <div className="table-header">
          <div className="header-col">
            <img src="/media/table-header1.svg" alt="Pollution Right Serial Number" className="table-header1" />
          </div>
          <div className="header-col">
            <img src="/media/table-header2.svg" alt="Message" className="table-header2" />
          </div>
          <div className="header-col">
            <img src="/media/table-header3.svg" alt="Transaction" className="table-header3" />
          </div>
        </div>
        <div className="table-mainline">
          <img src="/media/table-mainline.svg" alt="Main divider" className="main-divider" />
        </div>
        <div className="table-row">
          <div className="row-col">
            <span className="serial-number">2030185690<br />-2030185693</span>
          </div>
          <div className="row-col">
            <span className="message">And they will say, "This land that was laid waste has become like the garden of Eden" Ezekiel 36:35</span>
          </div>
          <div className="row-col">
            <span className="transaction">https://etherscan.io/tx/0xb92d76...</span>
          </div>
        </div>
        <div className="table-line">
          <img src="/media/table-line.svg" alt="Row divider" className="row-divider" />
        </div>
        <div className="table-row">
          <div className="row-col">
            <span className="serial-number">2030185694</span>
          </div>
          <div className="row-col">
            <span className="message">A happy sample message.</span>
          </div>
          <div className="row-col">
            <span className="transaction">https://etherscan.io/tx/0xb92d48...</span>
          </div>
        </div>
      </div>
    </section>
  );
}