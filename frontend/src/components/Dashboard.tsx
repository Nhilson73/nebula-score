import { useEffect, useState } from 'react'
import { api } from '../api'
import type { EvaluationResult } from '../types'

interface Props {
  onNew: () => void
  onView: (ev: EvaluationResult) => void
}

function Dashboard({ onNew, onView }: Props) {
  const [evaluations, setEvaluations] = useState<EvaluationResult[]>([])
  const [total, setTotal] = useState(0)
  const [avg, setAvg] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.listEvaluations({ limit: 20 })
      .then((data) => {
        setEvaluations(data.items)
        setTotal(data.total)
        const scores = data.items.map((e) => e.nebula_score)
        setAvg(scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : 0)
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="card">
      <div className="section-heading">
        <div>
          <h2>Dashboard</h2>
          <p>Resumen de evaluaciones recientes y métricas del lote.</p>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="kpi">
          <span>Evaluaciones</span>
          <strong>{total}</strong>
        </div>
        <div className="kpi">
          <span>Score promedio</span>
          <strong>{avg.toFixed(1)}</strong>
        </div>
        <div className="kpi">
          <span>Productos activos</span>
          <strong>Coffee · Cacao · Wine</strong>
        </div>
      </div>

      <div className="actions">
        <button onClick={onNew}>Nueva evaluación</button>
        <button className="secondary" onClick={() => api.exportCsv()}>
          Descargar CSV
        </button>
      </div>

      {loading ? (
        <p>Cargando...</p>
      ) : evaluations.length === 0 ? (
        <p className="notice">No hay evaluaciones registradas. Crea la primera para comenzar.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Producto</th>
              <th>Lote</th>
              <th>Productor</th>
              <th>Modelo</th>
              <th>Score</th>
              <th>Confianza</th>
              <th>Estado</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {evaluations.map((ev) => (
              <tr key={ev.public_id}>
                <td>{ev.product === 'cacao' ? 'Cacao' : 'Coffee'}</td>
                <td>{ev.lot_id || '—'}</td>
                <td>{ev.producer || '—'}</td>
                <td>{ev.equipment_model}</td>
                <td><strong>{ev.nebula_score.toFixed(1)}</strong></td>
                <td>{ev.confidence_level}/5</td>
                <td>{ev.status}</td>
                <td>
                  <button className="secondary" onClick={() => onView(ev)}>Ver</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default Dashboard
