import { describe, expect, it } from 'vitest'
import { normalizedScore } from './preview'

describe('normalizedScore', () => {
  it('returns 0 for SCA at min input', () => {
    expect(normalizedScore(80, 80, 100)).toBe(0)
  })

  it('returns 100 for SCA at max input', () => {
    expect(normalizedScore(100, 80, 100)).toBe(100)
  })

  it('returns 50 for SCA halfway', () => {
    expect(normalizedScore(90, 80, 100)).toBe(50)
  })

  it('clamps below min to 0', () => {
    expect(normalizedScore(70, 80, 100)).toBe(0)
  })

  it('clamps above max to 100', () => {
    expect(normalizedScore(110, 80, 100)).toBe(100)
  })
})
