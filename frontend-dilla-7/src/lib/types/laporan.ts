export interface Laporan {
  id: number
  siswa: number
  deskripsi_analisis: string
  nilai: number
  ujian: number
  label_nilai: string
  nama_siswa: string
  nama_ujian?: string
  nama_kelas?: string
  pelaksanaan?: string | Date
  nama?: string
  kelas_id?: number
}

export type LaporanForm = {
  ujian: number
  siswa?: number
  nisn: string
  deskripsi_analisis: string
  nilai: number
  label_nilai: string
}
