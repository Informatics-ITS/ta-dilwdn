import { api } from '$lib/config/axios'
import type { Siswa, SiswaForm, SiswaUpload } from '$lib/types/siswa'

export async function getAllSiswa(): Promise<Siswa[]> {
  const res = await api.get('/api/siswa')
  return res.data
}

export async function getSiswaById(id: number): Promise<Siswa> {
  const res = await api.get(`/api/siswa/${id}`)
  return res.data
}

export async function createSiswa(data: SiswaForm) {
  const res = await api.post('/api/siswa', data)
  return res.data
}

export async function uploadSiswa(data: SiswaUpload) {
  const res = await api.post('/api/siswa/excel', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return res.data
}

export async function updateSiswa(no: number, data: SiswaForm) {
  const res = await api.put(`/api/siswa/${no}`, data)
  return res.data
}

export async function deleteSiswa(no: number) {
  const res = await api.delete(`/api/siswa/${no}`)
  return res.data
}
