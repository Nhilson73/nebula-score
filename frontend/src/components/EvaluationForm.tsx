import { useMemo, useState } from 'react'
import { api } from '../api'
import type { EvaluationInput, Methodology, PenaltyInput } from '../types'
import { normalizedScore } from '../utils/preview'

interface Props {
  methodology: Methodology
  onCancel: () => void
  onCreated: (res: any) => void
}

const emptyPenalty: PenaltyInput = {
  code: '',
  name: '',
  category: 'Manual override',
  severity: 'medium',
  value: '',
  reviewable: true,
}

function EvaluationForm({ methodology, onCancel, onCreated }: Props) {
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const initialModelId = useMemo(() => Object.keys(methodology.process.models)[0] || 'insight', [methodology])

  const initialProcess = useMemo(() => {
    const model = methodology.process.models[initialModelId]
    const values: Record<string, number | string> = {}
    if (model) {
      model.fields.forEach((f) => { values[f.id] = 85 })
    }
    return values
  }, [methodology, initialModelId])

  const initialIntegrity = useMemo(() => {
    const values: Record<string, number | string> = {}
    Object.keys(methodology.integrity.components).forEach((k) => { values[k] = 90 })
    return values
  }, [methodology])

  const qualityLabel = methodology.quality.input_label || methodology.quality.label
  const qualityDefault = methodology.product === 'coffee' ? 86 : 70

  const [form, setForm] = useState<EvaluationInput>({
    product: methodology.product,
    equipment_model: initialModelId,
    origin_plan: 'pro',
    evidence_quality: 4,
    quality_input: qualityDefault,
    process_values: initialProcess,
    integrity_values: initialIntegrity,
    penalties: [],
  })

  const selectedModel = methodology.process.models[form.equipment_model]

  const updateField = (key: keyof EvaluationInput, value: any) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const updateProcess = (id: string, value: string | number) => {
    setForm((prev) => ({ ...prev, process_values: { ...prev.process_values, [id]: value } }))
  }

  const updateIntegrity = (id: string, value: string | number) => {
    setForm((prev) => ({ ...prev, integrity_values: { ...prev.integrity_values, [id]: value } }))
  }

  const handleModelChange = (modelId: string) => {
    const model = methodology.process.models[modelId]
    if (!model) return
    const values: Record<string, number | string> = {}
    model.fields.forEach((f) => { values[f.id] = form.process_values[f.id] ?? 85 })
    setForm((prev) => ({ ...prev, equipment_model: modelId, process_values: values }))
  }

  const addPenalty = () => {
    setForm((prev) => ({ ...prev, penalties: [...prev.penalties, { ...emptyPenalty }] }))
  }

  const updatePenalty = (index: number, field: keyof PenaltyInput, value: any) => {
    setForm((prev) => {
      const penalties = [...prev.penalties]
      penalties[index] = { ...penalties[index], [field]: value }
      return { ...prev, penalties }
    })
  }

  const removePenalty = (index: number) => {
    setForm((prev) => ({ ...prev, penalties: prev.penalties.filter((_, i) => i !== index) }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const payload = {
        ...form,
        quality_input: Number(form.quality_input),
        evidence_quality: Number(form.evidence_quality),
        process_values: Object.fromEntries(
          Object.entries(form.process_values).map(([k, v]) => [k, Number(v)])
        ),
        integrity_values: Object.fromEntries(
          Object.entries(form.integrity_values).map(([k, v]) => [k, Number(v)])
        ),
        penalties: form.penalties.map((p) => ({ ...p, value: Number(p.value) })),
      }
      const result = await api.createEvaluation(payload)
      onCreated(result)
    } catch (err: any) {
      setError(err.message || 'Error al calcular la evaluación')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <div className="section-heading">
        <div>
          <h2>Nueva evaluación</h2>
          <p>Complete los datos del lote y del modelo de fermentación.</p>
        </div>
      </div>

      {error && <div className="notice" style={{ marginBottom: 20 }}>{error}</div>}

      <fieldset>
        <legend>Identificación</legend>
        <div className="grid two">
          <label>
            Lote / microlote
            <input value={form.lot_id || ''} onChange={(e) => updateField('lot_id', e.target.value)} />
          </label>
          <label>
            Productor o finca
            <input value={form.producer || ''} onChange={(e) => updateField('producer', e.target.value)} />
          </label>
        </div>
      </fieldset>

      <fieldset>
        <legend>Calidad sensorial</legend>
        <div className="grid two">
          <label>
            Puntuación {qualityLabel}
            <input
              type="number"
              min={methodology.quality.input_range.min}
              max={methodology.quality.input_range.max}
              step="0.01"
              value={form.quality_input}
              onChange={(e) => updateField('quality_input', e.target.value)}
            />
            <small>{methodology.quality.warning}</small>
          </label>
          <div className="metric-preview">
            <span>Score normalizado</span>
            <strong>
              {normalizedScore(Number(form.quality_input), methodology.quality.normalization.min_input, methodology.quality.normalization.max_input).toFixed(1)}
            </strong>
            <small>{methodology.quality.normalization.formula}</small>
          </div>
        </div>
      </fieldset>

      <fieldset>
        <legend>Modelo y desempeño del proceso</legend>
        <div className="grid two">
          <label>
            Modelo Nebula Fermentation®
            <select value={form.equipment_model} onChange={(e) => handleModelChange(e.target.value)}>
              {Object.entries(methodology.process.models).map(([key, m]) => (
                <option key={key} value={key}>{m.label}</option>
              ))}
            </select>
          </label>
          <div className="metric-preview">
            <span>Fórmula</span>
            <strong style={{ fontSize: '1rem' }}>{selectedModel?.formula || '—'}</strong>
            <small>Equipo permite confianza máxima {selectedModel?.equipment_capability || '—'}/5</small>
          </div>
        </div>
        <div className="grid three" style={{ marginTop: 18 }}>
          {selectedModel?.fields.map((field) => (
            <label key={field.id}>
              {field.label}
              <input
                type="number"
                min={0}
                max={100}
                step="0.1"
                value={form.process_values[field.id] ?? ''}
                onChange={(e) => updateProcess(field.id, e.target.value)}
              />
              <small>Ponderación: {Math.round(field.weight * 100)}%</small>
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend>Integridad y confianza</legend>
        <div className="grid three">
          {Object.entries(methodology.integrity.components).map(([key, component]) => (
            <label key={key}>
              {component.label}
              <input
                type="number"
                min={0}
                max={100}
                step="0.1"
                value={form.integrity_values[key] ?? ''}
                onChange={(e) => updateIntegrity(key, e.target.value)}
              />
              <small>Ponderación: {Math.round(component.weight * 100)}%</small>
            </label>
          ))}
        </div>
        <div className="grid two" style={{ marginTop: 18 }}>
          <label>
            Plan Nebula OriginBlok®
            <select value={form.origin_plan} onChange={(e) => updateField('origin_plan', e.target.value)}>
              {Object.entries(methodology.confidence.plan_caps).map(([plan, cap]) => (
                <option key={plan} value={plan}>{plan.charAt(0).toUpperCase() + plan.slice(1)} — máximo {cap}</option>
              ))}
            </select>
          </label>
          <label>
            Calidad real de la evidencia
            <select value={form.evidence_quality} onChange={(e) => updateField('evidence_quality', Number(e.target.value))}>
              {[0, 1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </label>
        </div>
      </fieldset>

      <fieldset>
        <legend>Penalizaciones</legend>
        {form.penalties.map((penalty, idx) => (
          <div key={idx} className="grid three" style={{ alignItems: 'end' }}>
            <label>
              Código
              <input value={penalty.code} onChange={(e) => updatePenalty(idx, 'code', e.target.value)} />
            </label>
            <label>
              Nombre
              <input value={penalty.name} onChange={(e) => updatePenalty(idx, 'name', e.target.value)} />
            </label>
            <label>
              Valor
              <div style={{ display: 'flex', gap: 8 }}>
                <input
                  type="number"
                  min={0}
                  max={100}
                  step="0.1"
                  value={penalty.value}
                  onChange={(e) => updatePenalty(idx, 'value', e.target.value)}
                  style={{ flex: 1 }}
                />
                <button type="button" className="danger" onClick={() => removePenalty(idx)}>×</button>
              </div>
            </label>
          </div>
        ))}
        <button type="button" className="secondary" onClick={addPenalty}>Agregar penalización</button>
      </fieldset>

      <div className="actions">
        <button type="submit" disabled={saving}>{saving ? 'Calculando...' : 'Calcular Nebula Score®'}</button>
        <button type="button" className="secondary" onClick={onCancel}>Cancelar</button>
      </div>
    </form>
  )
}

export default EvaluationForm
