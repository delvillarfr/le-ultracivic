export default function Home() {
  return (
    <main className="min-h-screen bg-white font-sans">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8">
          Ultra Civic
        </h1>
        
        {/* Font Weight Test */}
        <div className="max-w-2xl mx-auto space-y-4 mb-8">
          <p className="font-normal text-lg">
            Regular (400): Buy + Retire Polluters&apos; Legal Rights to Emit 999 Tons of CO2
          </p>
          <p className="font-medium text-lg">
            Medium (500): Buy + Retire Polluters&apos; Legal Rights to Emit 999 Tons of CO2
          </p>
          <p className="font-semibold text-lg">
            Semibold (600): Buy + Retire Polluters&apos; Legal Rights to Emit 999 Tons of CO2
          </p>
          <p className="font-bold text-lg">
            Bold (700): Buy + Retire Polluters&apos; Legal Rights to Emit 999 Tons of CO2
          </p>
          <p className="font-extrabold text-lg">
            Extra Bold (800): Buy + Retire Polluters&apos; Legal Rights to Emit 999 Tons of CO2
          </p>
        </div>
        
        <p className="text-center text-gray-600">
          Landing page coming soon...
        </p>
      </div>
    </main>
  )
}