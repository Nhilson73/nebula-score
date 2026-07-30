import { evaluate } from './engine'
import type { EvaluationInput, EvaluationResult, Methodology, Paginated } from './types'

const rawBase =
  typeof window !== 'undefined'
    ? (window as unknown as { NEBULA_API_BASE?: string }).NEBULA_API_BASE
    : undefined

const API_BASE = rawBase === '' ? '' : rawBase || '/api'
const isLocalMode = API_BASE === ''

const STORAGE_KEY = 'nebula-evaluations'

function readEvaluations(): EvaluationResult[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as EvaluationResult[]) : []
  } catch {
    return []
  }
}

function writeEvaluations(items: EvaluationResult[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || response.statusText)
  }
  return response.json() as Promise<T>
}

const rawBaseUrl = ((import.meta as any).env?.BASE_URL as string) || '/'
const baseUrl = rawBaseUrl.endsWith('/') ? rawBaseUrl : rawBaseUrl + '/'

async function localMethodology(product: string, version = 'v1'): Promise<Methodology> {
  const response = await fetch(`${baseUrl}methodologies/${product}/${version}.json`)
  if (!response.ok) throw new Error('No se pudo cargar la metodología')
  return response.json() as Promise<Methodology>
}

async function localCreateEvaluation(data: EvaluationInput): Promise<EvaluationResult> {
  const methodology = await localMethodology(data.product, 'v1')
  const result = evaluate(data, methodology)
  const items = readEvaluations()
  result.id = items.length ? Math.max(...items.map((i) => i.id)) + 1 : 1
  items.unshift(result)
  writeEvaluations(items)
  return result
}

async function localListEvaluations(params?: { skip?: number; limit?: number }): Promise<Paginated<EvaluationResult>> {
  const all = readEvaluations()
  const skip = params?.skip ?? 0
  const limit = params?.limit ?? 100
  return {
    total: all.length,
    page: Math.floor(skip / limit) + 1,
    page_size: limit,
    items: all.slice(skip, skip + limit),
  }
}

async function localGetEvaluation(id: string): Promise<EvaluationResult> {
  const result = readEvaluations().find((e) => String(e.id) === id)
  if (!result) throw new Error('Evaluación no encontrada')
  return result
}

function localExportCsv() {
  const items = readEvaluations()
  if (!items.length) {
    alert('No hay evaluaciones para exportar')
    return
  }
  const headers = ['id', 'product', 'lot_id', 'producer', 'equipment_model', 'nebula_score', 'classification', 'created_at']
  const rows = items.map((e) =>
    [
      e.id,
      e.product,
      e.lot_id || '',
      e.producer || '',
      e.equipment_model,
      e.nebula_score,
      e.classification,
      e.created_at,
    ].join(','),
  )
  const csv = [headers.join(','), ...rows].join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'nebula-score-evaluations.csv'
  a.click()
  URL.revokeObjectURL(url)
}

export const api = {
  health: () =>
    isLocalMode
      ? Promise.resolve({ status: 'ok', mode: 'static' })
      : fetchJson<{ status: string }>('/health'),

  listProducts: () =>
    Promise.resolve([
      {
        id: 'coffee',
        name: 'Nebula Score® Coffee',
        description: 'Evaluación de calidad sensorial, fermentación e integridad para café.',
        available: true,
      },
      {
        id: 'cacao',
        name: 'Nebula Score® Cacao',
        description: 'Evaluación de calidad sensorial, fermentación e integridad para cacao.',
        available: true,
      },
      {
        id: 'wine',
        name: 'Nebula Score® Wine',
        description: 'Evaluación sensorial, fermentación y crianza para vino.',
        available: true,
      },
    ]),

  getMethodology: (product: string, version = 'v1') =>
    isLocalMode ? localMethodology(product, version) : fetchJson<Methodology>(`/v1/methodologies/${product}/${version}`),

  listEvaluations: (params?: { skip?: number; limit?: number }) =>
    isLocalMode ? localListEvaluations(params) : fetchJson<Paginated<EvaluationResult>>(`/v1/evaluations?${new URLSearchParams(params as Record<string, string>).toString()}`),

  getEvaluation: (id: string) =>
    isLocalMode ? localGetEvaluation(id) : fetchJson<EvaluationResult>(`/v1/evaluations/${id}`),

  createEvaluation: (data: EvaluationInput) =>
    isLocalMode ? localCreateEvaluation(data) : fetchJson<EvaluationResult>('/v1/evaluations', { method: 'POST', body: JSON.stringify(data) }),

  exportCsv: () => {
    if (isLocalMode) {
      localExportCsv()
    } else {
      window.open(`${API_BASE}/v1/export/csv`, '_blank')
    }
  },
}
