export function normalizedScore(sca: number, minInput: number, maxInput: number): number {
  if (minInput >= maxInput) return 0
  const clamped = Math.min(Math.max(sca, minInput), maxInput)
  return ((clamped - minInput) / (maxInput - minInput)) * 100
}
