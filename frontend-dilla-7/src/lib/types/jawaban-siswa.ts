export interface JsonResult {
  student_answer: string
  ai_analysis: {
    angka_dalam_soal: string
    jawaban: string
    operator: string
    soal_cerita: string
  }
  comparison: {
    status: string
    nilai: string
  }
}

export interface JawabanSiswa {
  id: number
  siswa: number
  nisn: string
  soal: number
  status: string
  analisis?: string
  json_result: JsonResult
}

export type JawabanSiswaForm = {
  siswa?: number
  nisn: string
  soal: number
  status: string
  json_result: JsonResult
}
