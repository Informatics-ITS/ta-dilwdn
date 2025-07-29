import { api } from '$lib/config/axios'
import type { JawabanSiswa, JawabanSiswaForm } from '$lib/types/jawaban-siswa'

export async function getAllJawabanSiswa(): Promise<JawabanSiswa[]> {
  const res = await api.get('/api/jawaban-siswa')
  return res.data
}

export async function getJawabanSiswaById(id: number): Promise<JawabanSiswa> {
  const res = await api.get(`/api/jawaban-siswa/${id}`)
  return res.data
}

export async function createJawabanSiswa(data: JawabanSiswaForm) {
  const res = await api.post('/api/student/jawaban-siswa', data)
  return res.data
}

export async function updateJawabanSiswa(no: number, data: JawabanSiswaForm) {
  const res = await api.put(`/api/jawaban-siswa/${no}`, data)
  return res.data
}

export async function deleteJawabanSiswa(no: number) {
  const res = await api.delete(`/api/jawaban-siswa/${no}`)
  return res.data
}
