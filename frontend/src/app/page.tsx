import { Title, Hero1, Hero2Left, Hero2Right, ValueProp1Left } from '../components/svg'
import FormSection from '../components/FormSection'
import ButtonSection from '../components/ButtonSection'
import HistoryTable from '../components/HistoryTable'

export default function Home() {
  return (
    <main className="min-h-screen bg-white font-sans">
      <div className="w-full mx-auto px-4 py-4">
        <div className="text-center space-y-2">
          <Title className="mx-auto" />
          <Hero1 className="mx-auto" />
          <div className="flex justify-center items-center gap-1">
            <Hero2Left />
            <Hero2Right />
          </div>
          <ValueProp1Left className="mx-auto" />
        </div>
        
        <div className="my-4">
          <FormSection />
        </div>
        
        <div className="mb-6">
          <ButtonSection />
        </div>
        
        <div className="mt-6">
          <HistoryTable />
        </div>
      </div>
    </main>
  )
}