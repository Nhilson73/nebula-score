import type { EvaluationInput, EvaluationResult, Methodology, Paginated } from './types'

const API_BASE =
  typeof window !== 'undefined' && (window as unknown as { NEBULA_API_BASE?: string }).NEBULA_API_BASE
    ? (window as unknown as { NEBULA_API_BASE: string }).NEBULA_API_BASE
    : '/api'

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

export const api = {
  health: () => fetchJson<{ status: string }>('/health'),

  listProducts: () => fetchJson<{ id: string; name: string; description: string; available: boolean }[]>('/v1/products'),

  getMethodology: (product: string, version = 'v1') =>
    fetchJson<Methodology>(`/v1/methodologies/${product}/${version}`),

  listEvaluations: (params?: { skip?: number; limit?: number }) =>
    fetchJson<Paginated<EvaluationResult>>(`/v1/evaluations?${new URLSearchParams(params as Record<string, string>).toString()}`),

  getEvaluation: (id: string) => fetchJson<EvaluationResult>(`/v1/evaluations/${id}`),

  createEvaluation: (data: EvaluationInput) =>
    fetchJson<EvaluationResult>('/v1/evaluations', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  exportCsv: () => window.open(`${API_BASE}/v1/export/csv`, '_blank'),
}
