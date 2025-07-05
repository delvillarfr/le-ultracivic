import { Title, Hero1, Hero2Left, Hero2Right, ValueProp1Left } from '../components/svg'
import FormSection from '../components/FormSection'
import ButtonSection from '../components/ButtonSection'
import HistoryTable from '../components/HistoryTable'

export default function Home() {
  return (
    <main className="min-h-screen bg-white font-sans">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <Title className="mx-auto mb-6" />
          <Hero1 className="mx-auto mb-4" />
          <div className="flex justify-center items-center gap-4 mb-4">
            <Hero2Left />
            <Hero2Right />
          </div>
          <ValueProp1Left className="mx-auto mb-8" />
        </div>
        
        <div className="max-w-md mx-auto mb-8">
          <FormSection />
        </div>
        
        <div className="max-w-md mx-auto mb-12">
          <ButtonSection />
        </div>
        
        <div className="max-w-4xl mx-auto">
          <HistoryTable />
        </div>
      </div>
    </main>
  )
}