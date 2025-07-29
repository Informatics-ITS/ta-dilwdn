import { api } from '$lib/config/axios'
import type { Kelas, KelasForm } from '$lib/types/kelas'

export async function getAllKelas(): Promise<Kelas[]> {
  const res = await api.get('/api/kelas')
  return res.data
}

export async function getKelasById(id: number): Promise<Kelas> {
  const res = await api.get(`/api/kelas/${id}`)
  return res.data
}

export async function createKelas(data: Kelas) {
  const res = await api.post('/api/kelas', data)
  return res.data
}

export async function updateKelas(id: number, data: KelasForm) {
  const res = await api.put(`/api/kelas/${id}`, data)
  return res.data
}

export async function deleteKelas(id: number) {
  const res = await api.delete(`/api/kelas/${id}`)
  return res.data
}
