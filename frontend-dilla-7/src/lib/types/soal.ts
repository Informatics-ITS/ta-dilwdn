export interface JsonResult {
  angka_dalam_soal: string
  jawaban: string
  operator: string
  soal_cerita: string
}

export interface Soal {
  id: number
  json_result?: JsonResult
  soal: string
  ujian: number
}

export type SoalForm = {
  soal: string
  ujian?: number
  json_result?: JsonResult
}
