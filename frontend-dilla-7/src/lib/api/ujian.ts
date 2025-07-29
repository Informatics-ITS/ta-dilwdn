import { api } from '$lib/config/axios'
import type { Ujian, UjianForm } from '$lib/types/ujian'

export async function getAllUjian(): Promise<Ujian[]> {
  const res = await api.get('/api/ujian')
  return res.data
}

export async function getUjianById(id: number): Promise<Ujian> {
  const res = await api.get(`/api/ujian/${id}`)
  return res.data
}

export async function createUjian(data: UjianForm) {
  const res = await api.post('/api/ujian', data)
  return res.data
}

export async function updateUjian(id: number, data: UjianForm) {
  const res = await api.put(`/api/ujian/${id}`, data)
  return res.data
}

export async function deleteUjian(id: number) {
  const res = await api.delete(`/api/ujian/${id}`)
  return res.data
}
