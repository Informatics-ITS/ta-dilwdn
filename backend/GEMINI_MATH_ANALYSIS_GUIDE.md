# Panduan Analisis Soal Matematika dengan Gemini AI

## Overview
Fitur ini mengintegrasikan Google Gemini AI untuk menganalisis soal matematika yang kompleks, terutama ketika algoritma sederhana tidak dapat mendeteksi operator atau ketika soal mengandung operasi campuran (Mix).

## Setup Requirements

### 1. Instalasi Package
```bash
pip install google-generativeai
```

### 2. API Key Setup
1. Dapatkan API key dari [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Tambahkan ke file `.env`:
```env
GEMINI_API_KEY=your_api_key_here
```

### 3. Restart Aplikasi
Setelah menambahkan API key, restart aplikasi Flask.

## Kapan Gemini Digunakan

Gemini AI akan dipanggil secara otomatis dalam endpoint `/api/solve_text` ketika:

1. **Operator Tidak Diketahui**: Algoritma sederhana tidak dapat mengidentifikasi operator
2. **Operator Campuran (Mix)**: Soal mengandung lebih dari satu operasi matematika
3. **Soal Kompleks**: Soal mengandung indikator kompleksitas seperti:
   - Kata penghubung: "kemudian", "lalu", "setelah itu", "selanjutnya"
   - Lebih dari 2 angka dalam soal
   - Multiple operator eksplisit

## Contoh Penggunaan

### Request ke `/api/solve_text`
```json
{
  "text_input": "Ana membeli 3 kotak permen, setiap kotak berisi 5 permen, kemudian dia memberikan 10 permen kepada temannya"
}
```

### Response dengan Gemini Analysis
```json
{
  "soal_cerita": "Ana membeli 3 kotak permen, setiap kotak berisi 5 permen, kemudian dia memberikan 10 permen kepada temannya",
  "operator": "Mix",
  "angka_dalam_soal": "3,5,10",
  "jawaban": "5",
  "analysis_method": "gemini",
  "gemini_confidence": "high",
  "penjelasan": "Operasi perkalian diikuti pengurangan",
  "operasi_detail": "3×5=15, 15-10=5",
  "original_analysis": {
    "operator": "Mix",
    "angka_dalam_soal": "3,5,10",
    "jawaban": "Perlu analisis lanjutan"
  }
}
```

## Testing Endpoints

### 1. Check Gemini Setup
```
GET /api/gemini/setup-check
```

Response:
```json
{
  "gemini_available": true,
  "api_key_configured": true,
  "api_key_length": 39,
  "setup_instructions": null
}
```

### 2. Test Gemini Analysis (Guru Only)
```
POST /api/teacher/test-gemini-analysis
Authorization: Required (Teacher role)

{
  "soal_text": "Budi membeli 4 kotak pensil, setiap kotak berisi 6 pensil, kemudian dia memberikan 8 pensil kepada adiknya"
}
```

Response:
```json
{
  "available": true,
  "input_soal": "...",
  "simple_analysis": {
    "operator": "Mix",
    "angka_dalam_soal": "4,6,8",
    "jawaban": "Perlu analisis lanjutan"
  },
  "gemini_analysis": {
    "status": "success",
    "analysis": {
      "operator": "Mix",
      "angka_dalam_soal": "4,6,8",
      "jawaban": "16",
      "soal_cerita": "..."
    },
    "confidence": "high",
    "penjelasan": "Operasi perkalian (4×6=24) diikuti pengurangan (24-8=16)",
    "operasi_detail": "4×6=24, 24-8=16"
  },
  "comparison": {
    "simple_operator": "Mix",
    "gemini_operator": "Mix",
    "needs_gemini": true,
    "gemini_triggered": true
  }
}
```

## Flow Diagram

```
Input Soal Matematika
         ↓
extract_math_simple()
         ↓
Operator = "Mix" OR "Tidak diketahui"?
         ↓ YES
PEDAGOGIC_ANALYSIS_AVAILABLE?
         ↓ YES
analyze_math_problem_with_gemini()
         ↓
Gemini Response Success?
         ↓ YES
Merge Results with Original Analysis
         ↓
Return Enhanced Response
```

## Error Handling

### 1. API Key Tidak Tersedia
```json
{
  "analysis_method": "simple_fallback",
  "gemini_error": "GEMINI_API_KEY not found in environment variables",
  "note": "Gemini analysis not available"
}
```

### 2. Gemini API Error
```json
{
  "analysis_method": "simple_fallback",
  "gemini_error": "Gemini API error: [error details]"
}
```

### 3. Package Tidak Terinstall
```json
{
  "analysis_method": "simple",
  "note": "Gemini analysis not available"
}
```

## Deteksi Operator Campuran

### Kriteria untuk Mix/Complex:
1. **Multiple Operation Keywords**: Lebih dari satu jenis kata kunci operasi
2. **Complex Indicators**: Kata penghubung yang menunjukkan urutan operasi
3. **Multiple Numbers**: Lebih dari 2 angka dalam soal
4. **Multiple Explicit Operators**: Lebih dari satu operator eksplisit (+, -, ×, ÷)

### Contoh Soal yang Memicu Gemini:
- "Ana mempunyai 20 permen, dia membeli 5 kotak lagi yang masing-masing berisi 4 permen, kemudian memberikan 10 permen"
- "Budi membeli 3 pak buku, setiap pak berisi 5 buku, lalu dia mengembalikan 2 buku"
- "Kelas A ada 25 siswa, kelas B ada 30 siswa, kemudian dibagi menjadi 5 kelompok"

## Performance Considerations

- Gemini hanya dipanggil untuk soal kompleks (tidak semua request)
- Fallback ke algoritma sederhana jika Gemini gagal
- Response time: ~2-5 detik untuk analisis Gemini
- Rate limiting: Sesuai dengan limit Google Gemini API

## Troubleshooting

### 1. Gemini Tidak Aktif
- Pastikan `google-generativeai` terinstall
- Pastikan `GEMINI_API_KEY` ada di .env
- Restart aplikasi Flask

### 2. Response Tidak Akurat
- Periksa prompt di fungsi `analyze_math_problem_with_gemini()`
- Coba test dengan endpoint `/api/teacher/test-gemini-analysis`

### 3. API Quota Exceeded
- Periksa usage di Google AI Studio
- Implementasi caching jika diperlukan

## Security Notes

- API Key disimpan di environment variables, tidak di code
- Endpoint testing hanya untuk role guru
- Validasi input dilakukan sebelum kirim ke Gemini
- Error details tidak mengekspos API key 