import { useHistory } from '@/hooks/useHistory'

export default function HistoryTable() {
  const { history, isLoading, error } = useHistory()
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
        {isLoading && (
          <div className="table-row">
            <div className="row-col" style={{textAlign: 'center', padding: '20px'}}>
              <span>Loading history...</span>
            </div>
          </div>
        )}
        
        {(error || (!isLoading && history.length === 0)) && (
          <div className="table-row">
            <div className="row-col" style={{textAlign: 'center', padding: '20px'}}>
              <span>No retirements yet. Be the first!</span>
            </div>
          </div>
        )}
        
        {!isLoading && !error && history.map((retirement, index) => (
          <div key={retirement.serial_number}>
            <div className="table-row">
              <div className="row-col">
                <span className="serial-number">{retirement.serial_number}</span>
              </div>
              <div className="row-col">
                <span className="message">{retirement.message}</span>
              </div>
              <div className="row-col">
                <span className="transaction">
                  {retirement.reward_tx_hash ? (
                    <a 
                      href={`https://sepolia.etherscan.io/tx/${retirement.reward_tx_hash}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="transaction-link"
                      title="View PR token reward transaction"
                    >
                      {retirement.reward_tx_hash.slice(0, 10)}...{retirement.reward_tx_hash.slice(-8)}
                    </a>
                  ) : retirement.tx_hash ? (
                    <a 
                      href={`https://sepolia.etherscan.io/tx/${retirement.tx_hash}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="transaction-link"
                      title="View payment transaction"
                    >
                      {retirement.tx_hash.slice(0, 10)}...{retirement.tx_hash.slice(-8)}
                    </a>
                  ) : (
                    <span className="no-transaction">Processing...</span>
                  )}
                </span>
              </div>
            </div>
            {index < history.length - 1 && (
              <div className="table-line">
                <img src="/media/table-line.svg" alt="Row divider" className="row-divider" />
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}