export interface Ujian {
  id: number
  nama_ujian: string
  kelas: number
  pelaksanaan: string
  status: string
}

export type UjianForm = {
  nama_ujian: string
  kelas: number
  pelaksanaan: string
  status: string
}
