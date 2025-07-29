import { api } from '$lib/config/axios'
import type { Solve, Compare } from '$lib/types/solve'

export async function solveMathProblemImage(data: Solve) {
  const res = await api.post('/api/solve', data)
  return res.data
}

export async function solveMathProblemText(data: Solve) {
  const res = await api.post('/api/solve_text', data)
  return res.data
}

export async function compareAnswer(data: Compare) {
  const res = await api.post('/api/compare_answer', data)
  return res.data
}

export async function analyzeAnswer(data: { text: string }) {
  const res = await api.post('/api/pedagogic/analyze-text', data)
  return res.data
}
