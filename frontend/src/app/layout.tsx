import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Ultra Civic',
  description: 'Buy + Retire Polluters\' Legal Rights to Emit 999 Tons of CO2',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}