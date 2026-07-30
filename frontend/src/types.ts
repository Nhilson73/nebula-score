export interface ProcessModelField {
  id: string
  label: string
  weight: number
}

export interface ProcessModel {
  label: string
  equipment_capability: number
  formula: string
  fields: ProcessModelField[]
}

export interface Methodology {
  id: string
  product: string
  name: string
  version: string
  status: string
  note?: string
  weights: { quality: number; process: number; integrity: number }
  quality: {
    label: string
    input_variable: string
    input_range: { min: number; max: number }
    normalization: { min_input: number; max_input: number; min_output: number; max_output: number; formula?: string }
    warning?: string
  }
  process: { label: string; models: Record<string, ProcessModel> }
  integrity: { label: string; components: Record<string, { label: string; weight: number }> }
  confidence: { range: { min: number; max: number }; plan_caps: Record<string, number> }
  classification: { bands: { min: number; label: string; description: string }[] }
}

export interface EvaluationInput {
  lot_id?: string
  producer?: string
  farm?: string
  country?: string
  region?: string
  geo_latitude?: number | ''
  geo_longitude?: number | ''
  variety?: string
  harvest_date?: string
  process_start_date?: string
  process_end_date?: string
  equipment_model: string
  origin_plan: string
  evidence_quality: number
  protocol?: string
  sca_score: number | string
  process_values: Record<string, number | string>
  integrity_values: Record<string, number | string>
  penalties: PenaltyInput[]
}

export interface PenaltyInput {
  code: string
  name: string
  category?: string
  severity?: string
  value: number | ''
  affected?: string
  description?: string
  justification?: string
  reviewable?: boolean
}

export interface EvaluationResult {
  id: number
  public_id: string
  product: string
  methodology_id: string
  methodology_version: string
  status: string
  lot_id?: string
  producer?: string
  farm?: string
  country?: string
  region?: string
  geo_latitude?: number
  geo_longitude?: number
  variety?: string
  harvest_date?: string
  process_start_date?: string
  process_end_date?: string
  equipment_model: string
  origin_plan: string
  evidence_quality: number
  protocol?: string
  sca_score: number
  process_values: Record<string, number>
  integrity_values: Record<string, number>
  penalties: PenaltyInput[]
  quality_score: number
  process_score: number
  integrity_score: number
  total_penalties: number
  nebula_score: number
  confidence_level: number
  classification: string
  interpretation: string
  components: Record<string, any>
  created_at: string
  updated_at?: string
}

export interface Paginated<T> {
  total: number
  page: number
  page_size: number
  items: T[]
}
