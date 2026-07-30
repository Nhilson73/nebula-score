import { api } from '../api'
import type { EvaluationResult, Methodology } from '../types'

interface Props {
  evaluation: EvaluationResult
  methodology?: Methodology | null
  onBack: () => void
  onNew: () => void
}

function ResultView({ evaluation, methodology, onBack, onNew }: Props) {
  const angle = Math.min(evaluation.nebula_score * 3.6, 360)
  const qualityLabel = methodology?.quality.input_label || methodology?.quality.label || 'Sensorial'
  const productName = evaluation.product === 'cacao' ? 'Cacao' : 'Coffee'

  const exportJson = () => {
    api.getEvaluation(evaluation.public_id)
      .then((res) => {
        const blob = new Blob([JSON.stringify(res, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        const lot = (res.lot_id || 'lote').replace(/[^a-zA-Z0-9._-]/g, '-')
        a.href = url
        a.download = `nebula-score-${lot}.json`
        a.click()
        URL.revokeObjectURL(url)
      })
  }

  const processInputs = evaluation.components.process.inputs as Record<string, number>

  return (
    <div className="card result-panel">
      <div className="section-heading">
        <div>
          <h2>Resultado</h2>
          <p>{evaluation.classification}</p>
        </div>
      </div>

      <div className="score-ring" style={{ '--score-angle': `${angle}deg` } as React.CSSProperties}>
        <div>
          <span>{evaluation.nebula_score.toFixed(1)}</span>
          <small>/100</small>
        </div>
      </div>

      <h3>{evaluation.classification}</h3>
      <p>{evaluation.interpretation}</p>

      <div className="breakdown">
        <div>
          <span>{qualityLabel} ({evaluation.quality_input})</span>
          <strong>{evaluation.quality_score.toFixed(1)}</strong>
        </div>
        <div>
          <span>Proceso · {evaluation.equipment_model}</span>
          <strong>{evaluation.process_score.toFixed(1)}</strong>
        </div>
        <div>
          <span>Integridad</span>
          <strong>{evaluation.integrity_score.toFixed(1)}</strong>
        </div>
        <div>
          <span>Penalizaciones</span>
          <strong>−{evaluation.total_penalties.toFixed(1)}</strong>
        </div>
      </div>

      {evaluation.penalties.length > 0 && (
        <div style={{ marginTop: 18, textAlign: 'left' }}>
          <h4>Penalizaciones aplicadas</h4>
          <ul>
            {evaluation.penalties.map((p, i) => (
              <li key={i}>{p.name || p.code}: −{Number(p.value).toFixed(1)}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="confidence">
        <span>Confidence Level</span>
        <strong>{evaluation.confidence_level}/5</strong>
        <small>Limitado por equipo, plan OriginBlok® y calidad real de la evidencia.</small>
      </div>

      <div style={{ marginTop: 18, textAlign: 'left', color: 'var(--muted)', fontSize: '0.92rem' }}>
        <p><strong>Producto:</strong> {productName}</p>
        <p><strong>Lote:</strong> {evaluation.lot_id || 'No indicado'}</p>
        <p><strong>Productor:</strong> {evaluation.producer || 'No indicado'}</p>
        <p><strong>Modelo:</strong> {evaluation.equipment_model}</p>
        <p><strong>Metodología:</strong> {evaluation.methodology_id} v{evaluation.methodology_version}</p>
      </div>

      {processInputs && Object.keys(processInputs).length > 0 && (
        <div style={{ marginTop: 18, textAlign: 'left' }}>
          <h4>Inputs del proceso</h4>
          <div className="grid three">
            {Object.entries(processInputs).map(([key, value]) => (
              <div key={key} className="metric-preview" style={{ minHeight: 60 }}>
                <span style={{ fontSize: '0.75rem' }}>{key}</span>
                <strong style={{ fontSize: '1.2rem' }}>{value.toFixed(1)}</strong>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="actions" style={{ marginTop: 24 }}>
        <button onClick={exportJson}>Descargar JSON</button>
        <button className="secondary" onClick={onNew}>Nueva evaluación</button>
        <button className="secondary" onClick={onBack}>Volver al dashboard</button>
      </div>

      <div className="notice" style={{ marginTop: 20 }}>
        <strong>Estado:</strong> Nebula Score® {productName} V1 es un modelo técnico en validación.
        No constituye todavía una certificación oficial ni sustituye evaluaciones sensoriales profesionales.
      </div>
    </div>
  )
}

export default ResultView
