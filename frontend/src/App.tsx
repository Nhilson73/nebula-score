import { useEffect, useState } from 'react'
import { api } from './api'
import type { EvaluationResult, Methodology } from './types'
import Dashboard from './components/Dashboard'
import EvaluationForm from './components/EvaluationForm'
import ResultView from './components/ResultView'

type View = 'dashboard' | 'new' | 'result'
type Product = 'coffee' | 'cacao'

function App() {
  const [product, setProduct] = useState<Product>('coffee')
  const [view, setView] = useState<View>('dashboard')
  const [methodology, setMethodology] = useState<Methodology | null>(null)
  const [result, setResult] = useState<EvaluationResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setError(null)
    api.getMethodology(product, 'v1')
      .then(setMethodology)
      .catch((err) => setError(err.message))
  }, [product])

  const handleCreated = (res: EvaluationResult) => {
    setResult(res)
    setView('result')
  }

  const handleView = (res: EvaluationResult) => {
    if (res.product === 'coffee' || res.product === 'cacao') {
      setProduct(res.product)
    }
    setResult(res)
    setView('result')
  }

  const handleNew = () => {
    setView('new')
  }

  return (
    <>
      <header className="hero">
        <div className="hero__content">
          <p className="eyebrow">Nebula Ecosystem®</p>
          <h1>Nebula Score® {product === 'cacao' ? 'Cacao' : 'Coffee'} V1</h1>
          <p className="hero__lead">
            Calidad sensorial, control de fermentación e integridad de evidencia en una sola puntuación verificable.
          </p>
          <div className="product-selector" style={{ marginTop: 18 }}>
            <button
              type="button"
              className={product === 'coffee' ? 'primary' : 'secondary'}
              onClick={() => { setProduct('coffee'); setView('dashboard') }}
            >
              Coffee
            </button>
            <button
              type="button"
              className={product === 'cacao' ? 'primary' : 'secondary'}
              onClick={() => { setProduct('cacao'); setView('dashboard') }}
            >
              Cacao
            </button>
          </div>
        </div>
      </header>

      <main className="layout">
        {error && <div className="card notice">{error}</div>}
        {view === 'dashboard' && (
          <Dashboard onNew={handleNew} onView={handleView} />
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
            methodology={methodology}
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
