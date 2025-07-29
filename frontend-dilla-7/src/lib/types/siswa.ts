export interface Siswa {
  no: number
  nama_siswa: string
  kelas: number
  NISN: string
  password: string
}

export type SiswaForm = {
  nama_siswa: string
  kelas: number
  NISN: string
  password: string
}

export type SiswaUpload = {
  file: File
}
