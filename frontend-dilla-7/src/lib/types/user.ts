export interface User {
  id: number
  nama_lengkap: string
  email: string
  jenis_kelamin: string
  password: string
}

export type Register = {
  nama_lengkap: string
  email: string
  jenis_kelamin: string
  password: string
  role: string
}
