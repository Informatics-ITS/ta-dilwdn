export interface Solve {
  image?: string
  text_input?: string
}

export interface JsonResult {
  angka_dalam_soal: string
  jawaban: string
  operator: string
  soal_cerita?: string
}
export interface Compare {
  ai_answer?: JsonResult
  student_answer: JsonResult
}
