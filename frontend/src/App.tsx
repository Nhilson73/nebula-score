import { useEffect, useState } from 'react'
import { api } from './api'
import type { EvaluationResult, Methodology } from './types'
import Dashboard from './components/Dashboard'
import EvaluationForm from './components/EvaluationForm'
import ResultView from './components/ResultView'

type View = 'dashboard' | 'new' | 'result'

function App() {
  const [view, setView] = useState<View>('dashboard')
  const [methodology, setMethodology] = useState<Methodology | null>(null)
  const [result, setResult] = useState<EvaluationResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.getMethodology('coffee', 'v1')
      .then(setMethodology)
      .catch((err) => setError(err.message))
  }, [])

  const handleCreated = (res: EvaluationResult) => {
    setResult(res)
    setView('result')
  }

  const handleView = (res: EvaluationResult) => {
    setResult(res)
    setView('result')
  }

  return (
    <>
      <header className="hero">
        <div className="hero__content">
          <p className="eyebrow">Nebula Ecosystem®</p>
          <h1>Nebula Score® Coffee V1</h1>
          <p className="hero__lead">
            Calidad sensorial, control de fermentación e integridad de evidencia en una sola puntuación verificable.
          </p>
        </div>
      </header>

      <main className="layout">
        {error && <div className="card notice">{error}</div>}
        {view === 'dashboard' && (
          <Dashboard onNew={() => setView('new')} onView={handleView} />
        )}
        {view === 'new' && methodology && (
          <EvaluationForm
            methodology={methodology}
            onCancel={() => setView('dashboard')}
            onCreated={handleCreated}
          />
        )}
        {view === 'result' && result && (
          <ResultView
            evaluation={result}
            onBack={() => setView('dashboard')}
            onNew={() => setView('new')}
          />
        )}
      </main>

      <footer>
        <p>Nebula Score® · Nebula Fermentation® · Nebula OriginBlok®</p>
      </footer>
    </>
  )
}

export default App
