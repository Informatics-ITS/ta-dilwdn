import { api } from '$lib/config/axios'
import type { Soal, SoalForm } from '$lib/types/soal'

export async function getAllSoal(): Promise<Soal[]> {
  const res = await api.get('/api/soal')
  return res.data
}

export async function getSoalById(id: number): Promise<Soal> {
  const res = await api.get(`/api/soal/${id}`)
  return res.data
}

export async function createSoal(data: SoalForm) {
  const res = await api.post('/api/soal', data)
  return res.data
}

export async function updateSoal(id: number, data: SoalForm) {
  const res = await api.put(`/api/soal/${id}`, data)
  return res.data
}

export async function deleteSoal(id: number) {
  const res = await api.delete(`/api/soal/${id}`)
  return res.data
}
