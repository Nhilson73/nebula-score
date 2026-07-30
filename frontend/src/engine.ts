import type { EvaluationInput, EvaluationResult, Methodology, ProcessModel } from './types'

function asNumber(value: unknown): number {
  const n = Number(value)
  return Number.isNaN(n) ? 0 : n
}

function clamp(value: number, min = 0, max = 100): number {
  let n = asNumber(value)
  if (n < min) n = min
  if (n > max) n = max
  return n
}

function linearClamp(
  value: number,
  inMin: number,
  inMax: number,
  outMin = 0,
  outMax = 100,
): number {
  if (inMin >= inMax) return outMin
  const normalized = (clamp(value, inMin, inMax) - inMin) / (inMax - inMin)
  return outMin + normalized * (outMax - outMin)
}

function roundScore(value: number, decimals = 1): number {
  return Math.round(value * 10 ** decimals) / 10 ** decimals
}

function classify(methodology: Methodology, score: number): { label: string; description: string } {
  const bands = [...methodology.classification.bands].sort((a, b) => b.min - a.min)
  for (const band of bands) {
    if (score >= band.min) return { label: band.label, description: band.description }
  }
  return { label: 'Sin clasificación', description: '' }
}

function computeConfidence(
  methodology: Methodology,
  model: ProcessModel,
  plan: string,
  evidenceQuality: number,
): number {
  const equipmentCap = model.equipment_capability
  const planCap = methodology.confidence.plan_caps[plan.toLowerCase()] || 0
  const evidenceCap = clamp(evidenceQuality, 0, methodology.confidence.range.max)
  return Math.min(equipmentCap, planCap, evidenceCap)
}

function computeIntegrityScore(
  methodology: Methodology,
  values: Record<string, number | string>,
): number {
  let total = 0
  for (const [key, component] of Object.entries(methodology.integrity.components)) {
    const value = asNumber(values[key] ?? 0)
    total += clamp(value) * component.weight
  }
  return total
}

function computeProcessScore(model: ProcessModel, values: Record<string, number | string>): number {
  let total = 0
  for (const field of model.fields) {
    const value = asNumber(values[field.id] ?? 0)
    total += clamp(value) * field.weight
  }
  return total
}

function computeTotalPenalties(penalties: { value: number | string }[]): number {
  return clamp(
    penalties.reduce((sum, p) => sum + asNumber(p.value), 0),
    0,
    100,
  )
}

export function evaluate(input: EvaluationInput, methodology: Methodology): EvaluationResult {
  const quality = methodology.quality
  const qualityValue = clamp(asNumber(input.quality_input), quality.input_range.min, quality.input_range.max)
  const qualityScore = linearClamp(
    qualityValue,
    quality.normalization.min_input,
    quality.normalization.max_input,
    quality.normalization.min_output,
    quality.normalization.max_output,
  )

  const processModel = methodology.process.models[input.equipment_model]
  if (!processModel) {
    throw new Error(`Modelo de proceso '${input.equipment_model}' no encontrado`)
  }

  const processScore = computeProcessScore(processModel, input.process_values)
  const integrityScore = computeIntegrityScore(methodology, input.integrity_values)
  const totalPenalties = computeTotalPenalties(input.penalties)

  const rawScore =
    qualityScore * methodology.weights.quality +
    processScore * methodology.weights.process +
    integrityScore * methodology.weights.integrity -
    totalPenalties

  const totalScore = clamp(rawScore, methodology.score_range.min, methodology.score_range.max)
  const classification = classify(methodology, totalScore)
  const confidenceLevel = computeConfidence(
    methodology,
    processModel,
    input.origin_plan,
    asNumber(input.evidence_quality),
  )

  const now = new Date().toISOString()
  const id = Math.floor(Date.now() / 1000)

  const processInputs: Record<string, number> = {}
  for (const field of processModel.fields) {
    processInputs[field.id] = roundScore(clamp(asNumber(input.process_values[field.id] ?? 0)))
  }

  const integrityComponents: Record<string, number> = {}
  for (const key of Object.keys(methodology.integrity.components)) {
    integrityComponents[key] = roundScore(clamp(asNumber(input.integrity_values[key] ?? 0)))
  }

  return {
    id,
    public_id: `NS-${id}-${Math.floor(Math.random() * 1000)}`,
    product: input.product,
    methodology_id: methodology.id,
    methodology_version: methodology.version,
    status: 'calculated',
    lot_id: input.lot_id || undefined,
    producer: input.producer || undefined,
    farm: input.farm || undefined,
    country: input.country || undefined,
    region: input.region || undefined,
    geo_latitude: input.geo_latitude ? asNumber(input.geo_latitude) : undefined,
    geo_longitude: input.geo_longitude ? asNumber(input.geo_longitude) : undefined,
    variety: input.variety || undefined,
    harvest_date: input.harvest_date || undefined,
    process_start_date: input.process_start_date || undefined,
    process_end_date: input.process_end_date || undefined,
    equipment_model: input.equipment_model,
    origin_plan: input.origin_plan,
    evidence_quality: asNumber(input.evidence_quality),
    protocol: input.protocol || undefined,
    quality_input: asNumber(input.quality_input),
    process_values: Object.fromEntries(
      Object.entries(input.process_values).map(([k, v]) => [k, roundScore(asNumber(v))]),
    ),
    integrity_values: Object.fromEntries(
      Object.entries(input.integrity_values).map(([k, v]) => [k, roundScore(asNumber(v))]),
    ),
    penalties: input.penalties.map((p) => ({ ...p, value: roundScore(asNumber(p.value)) })),
    quality_score: roundScore(qualityScore),
    process_score: roundScore(processScore),
    integrity_score: roundScore(integrityScore),
    total_penalties: roundScore(totalPenalties),
    nebula_score: roundScore(totalScore),
    confidence_level: confidenceLevel,
    classification: classification.label,
    interpretation: classification.description,
    components: {
      quality: {
        label: methodology.quality.label,
        raw_input: roundScore(qualityValue, 2),
        normalized_score: roundScore(qualityScore),
        weight: methodology.weights.quality,
        weighted_score: roundScore(qualityScore * methodology.weights.quality),
        warning: methodology.quality.warning,
      },
      process: {
        label: methodology.process.label,
        model: processModel.label,
        model_formula: processModel.formula,
        score: roundScore(processScore),
        weight: methodology.weights.process,
        weighted_score: roundScore(processScore * methodology.weights.process),
        inputs: processInputs,
      },
      integrity: {
        label: methodology.integrity.label,
        score: roundScore(integrityScore),
        weight: methodology.weights.integrity,
        weighted_score: roundScore(integrityScore * methodology.weights.integrity),
        components: integrityComponents,
      },
      penalties: {
        total: roundScore(totalPenalties),
        items: input.penalties,
      },
    },
    created_at: now,
    updated_at: now,
  }
}
