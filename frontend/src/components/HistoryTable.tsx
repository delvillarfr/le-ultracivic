'use client'

import { useState, useEffect } from 'react'

interface HistoryEntry {
  serialNumbers: string[]
  message: string
  transactionUrl: string
}

export default function HistoryTable() {
  const [historyData, setHistoryData] = useState<HistoryEntry[]>([])

  useEffect(() => {
    const mockData: HistoryEntry[] = [
      {
        serialNumbers: ['2030185690', '2030185692'],
        message: "And they will say, 'This land that was laid waste has become like the garden of Eden' Ezequiel 36:35",
        transactionUrl: 'https://etherscan.io/tx/0xb92d76...'
      },
      {
        serialNumbers: ['2030185694'],
        message: 'A happy sample message.',
        transactionUrl: 'https://etherscan.io/tx/0xb92d48...'
      }
    ]
    setHistoryData(mockData)
  }, [])

  return (
    <div className="space-y-6">
      <div className="text-center">
        <img 
          src="/media/table-title.svg" 
          alt="History"
          className="mx-auto"
        />
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr>
              <th className="text-left p-2">
                <img 
                  src="/media/table-header1.svg" 
                  alt="Pollution Right Serial Number"
                  className="h-8"
                />
              </th>
              <th className="text-left p-2">
                <img 
                  src="/media/table-header2.svg" 
                  alt="Message"
                  className="h-8"
                />
              </th>
              <th className="text-left p-2">
                <img 
                  src="/media/table-header3.svg" 
                  alt="Transaction"
                  className="h-8"
                />
              </th>
            </tr>
          </thead>
          <tbody>
            {historyData.map((entry, index) => (
              <tr key={index} className="border-b">
                <td className="p-2 font-mono text-sm">
                  {entry.serialNumbers.join(', ')}
                </td>
                <td className="p-2 text-sm">
                  {entry.message}
                </td>
                <td className="p-2 text-sm">
                  <a 
                    href={entry.transactionUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 underline"
                  >
                    {entry.transactionUrl}
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        <div className="mt-4">
          <img 
            src="/media/table-line.svg" 
            alt="Table line"
            className="w-full"
          />
        </div>
      </div>
    </div>
  )
}