import { api } from '$lib/config/axios'
import type { Laporan, LaporanForm } from '$lib/types/laporan'

export async function getAllLaporan(): Promise<Laporan[]> {
  const res = await api.get('/api/ujian-siswa')
  return res.data
}

export async function getLaporanById(id: number): Promise<Laporan> {
  const res = await api.get(`/api/ujian-siswa/${id}`)
  return res.data
}

export async function createLaporan(data: LaporanForm) {
  const res = await api.post('/api/ujian-siswa', data)
  return res.data
}
