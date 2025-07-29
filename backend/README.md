# School Management System API

Sistem manajemen sekolah berbasis REST API yang memungkinkan pengelolaan data siswa, kelas, ujian, dan analisis hasil ujian.

## Fitur

- Manajemen pengguna (admin dan guru)
- Manajemen kelas dan siswa
- Manajemen ujian dan soal
- Pencatatan jawaban siswa
- Analisis hasil ujian
- Solver soal matematika menggunakan OCR dan CNN

## Persyaratan Sistem

- Python 3.8 atau lebih baru
- MySQL/MariaDB
- Tesseract OCR (untuk fitur solver matematika)
- Virtual environment (opsional, tapi direkomendasikan)

## Instalasi

1. Clone repository ini:
```bash
git clone <repository-url>
cd school-management-api
```

2. Buat dan aktifkan virtual environment (opsional):
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Instal dependensi:
```bash
pip install -r requirements.txt
```

4. Buat file `.env` di root direktori dengan konfigurasi berikut:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=school_db
```

5. Pastikan Tesseract OCR terinstal:
- Windows: Download dan instal dari [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux: `sudo apt-get install tesseract-ocr`
- Mac: `brew install tesseract`

## Menjalankan Aplikasi

1. Buat database dan tabel:
```bash
python create_database.py
```

2. Buat stored procedures:
```bash
python create_procedures.py
```

3. Isi data awal (opsional):
```bash
python seed_database.py
```

4. Jalankan aplikasi:
```bash
python app.py
```

Server akan berjalan di `http://localhost:5000`

## API Endpoints

### Users
- `GET /api/users` - Mendapatkan semua pengguna
- `POST /api/users` - Membuat pengguna baru

### Kelas
- `GET /api/kelas` - Mendapatkan semua kelas
- `POST /api/kelas` - Membuat kelas baru

### Siswa
- `GET /api/siswa` - Mendapatkan semua siswa
- `POST /api/siswa` - Membuat data siswa baru

### Ujian
- `GET /api/ujian` - Mendapatkan semua ujian
- `POST /api/ujian` - Membuat ujian baru

### Ujian Siswa
- `GET /api/ujian-siswa` - Mendapatkan semua hasil ujian
- `POST /api/ujian-siswa` - Membuat hasil ujian baru
- `GET /api/ujian-siswa/<siswa_id>` - Mendapatkan hasil ujian siswa tertentu

### Soal
- `GET /api/soal` - Mendapatkan semua soal
- `POST /api/soal` - Membuat soal baru

### Jawaban Siswa
- `GET /api/jawaban-siswa` - Mendapatkan semua jawaban siswa
- `POST /api/jawaban-siswa` - Membuat jawaban siswa baru

### Statistik
- `GET /api/statistics/total-siswa` - Total siswa
- `GET /api/statistics/total-kelas` - Total kelas
- `GET /api/statistics/total-ujian` - Total ujian
- `GET /api/statistics/capaian` - Statistik capaian
- `GET /api/statistics/kelas/<kelas_id>` - Statistik kelas tertentu

### Math Problem Solver
- `POST /api/solve` - Menyelesaikan soal matematika dari gambar
- `POST /api/solve_text` - Menyelesaikan soal matematika dari teks (**Now with Gemini AI for complex problems**)

### 🆕 Gemini AI Math Analysis
- `POST /api/teacher/test-gemini-analysis` - Test Gemini analysis (Teacher only)
- `GET /api/gemini/setup-check` - Check Gemini setup status

### Student Authentication & Exam
- `POST /api/student/login` - Login siswa dengan NISN dan password
- `GET /api/student/profile` - Mendapatkan profil siswa (memerlukan token)
- `GET /api/student/exams` - Mendapatkan daftar ujian untuk kelas siswa (memerlukan token)
- `GET /api/student/exam/<exam_id>/questions` - Mendapatkan soal ujian tertentu (memerlukan token)
- `POST /api/student/exam/<exam_id>/submit` - Submit jawaban ujian (memerlukan token)

### Teacher Authentication & Management
- `POST /api/teacher/login` - Login guru dengan email dan password
- `GET /api/teacher/profile` - Mendapatkan profil guru (memerlukan token)
- `POST /api/teacher/logout` - Logout guru
- `GET /api/teacher/dashboard` - Dashboard guru dengan statistik
- `GET /api/teacher/kelas` - Mendapatkan semua kelas dengan jumlah siswa
- `POST /api/teacher/kelas` - Membuat kelas baru
- `PUT /api/teacher/kelas/<id>` - Update kelas
- `DELETE /api/teacher/kelas/<id>` - Hapus kelas
- `GET /api/teacher/kelas/<kelas_id>/siswa` - Mendapatkan siswa berdasarkan kelas
- `POST /api/teacher/siswa` - Membuat siswa baru dengan password default NISN
- `POST /api/teacher/siswa/bulk` - Membuat multiple siswa sekaligus
- `PUT /api/teacher/siswa/<no>` - Update data siswa
- `DELETE /api/teacher/siswa/<no>` - Hapus siswa
- `POST /api/teacher/siswa/excel` - Import siswa dari Excel

## Dokumentasi API

Untuk dokumentasi lengkap API, termasuk contoh request dan response, dapat dilihat di file `docs/postman_collection.json`. Anda dapat mengimpor file ini ke Postman untuk pengujian API.

## Fitur Siswa

### Login Siswa
Siswa dapat login menggunakan NISN dan password (default password adalah NISN).

**Contoh Request:**
```json
POST /api/student/login
{
    "nisn": "1234567890",
    "password": "1234567890"
}
```

**Response:**
```json
{
    "message": "Login berhasil",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "siswa": {
        "no": 1,
        "NISN": "1234567890",
        "nama_siswa": "John Doe",
        "kelas": 1,
        "role": "siswa"
    }
}
```

### Mengambil Ujian
Siswa dapat melihat daftar ujian yang tersedia untuk kelasnya dan mengambil ujian dengan menjawab soal dalam bentuk teks.

**Contoh Request:**
```json
POST /api/student/exam/1/submit
Authorization: Bearer <token>
{
    "answers": [
        {
            "soal_id": 1,
            "jawaban_text": "Di meja ada 4 buah apel. Lalu ibu meletakkan 2 buah apel lain. Berapa banyak apel di meja sekarang? Jawabannya adalah 6 apel."
        },
        {
            "soal_id": 2,
            "jawaban_text": "Adik mempunyai 11 ekor ikan. Lalu ayah membelikan 4 ekor ikan. Berapa banyak ikan adik sekarang? Jawabannya adalah 15 ekor ikan."
        }
    ]
}
```

**Response:**
```json
{
    "message": "Ujian berhasil disubmit",
    "nilai": 85,
    "label_nilai": "Baik",
    "total_soal": 2
}
```

## Fitur Guru

### Login Guru
Guru dapat login menggunakan email dan password dengan role 'guru'.

**Contoh Request:**
```json
POST /api/teacher/login
{
    "email": "guru@sekolah.com",
    "password": "password123"
}
```

**Response:**
```json
{
    "message": "Login successful",
    "teacher": {
        "id": 1,
        "email": "guru@sekolah.com",
        "nama_lengkap": "Guru Matematika",
        "role": "guru"
    }
}
```

### Manajemen Kelas
Guru dapat membuat, mengupdate, dan menghapus kelas.

**Contoh Request Membuat Kelas:**
```json
POST /api/teacher/kelas
Authorization: Bearer <teacher_token>
{
    "id": 1,
    "nama": "Kelas X IPA 1"
}
```

### Manajemen Siswa
Guru dapat menambah, mengupdate, dan menghapus siswa dengan password default NISN.

**Contoh Request Membuat Siswa:**
```json
POST /api/teacher/siswa
Authorization: Bearer <teacher_token>
{
    "NISN": "1234567890",
    "nama_siswa": "John Doe",
    "kelas": 1
}
```

**Contoh Request Import Excel:**
```json
POST /api/teacher/siswa/excel
Authorization: Bearer <teacher_token>
Content-Type: multipart/form-data

file: [Excel file dengan kolom NISN, nama_siswa, kelas]
```

### Dashboard Guru
Guru dapat melihat dashboard dengan statistik dan daftar kelas.

**Contoh Request:**
```json
GET /api/teacher/dashboard
Authorization: Bearer <teacher_token>
```

**Response:**
```json
{
    "statistics": {
        "total_kelas": 5,
        "total_siswa": 150,
        "total_ujian": 10
    },
    "kelas": [
        {
            "id": 1,
            "nama": "Kelas X IPA 1",
            "total_siswa": 30
        }
    ]
}
```

## 🆕 Fitur Gemini AI Math Analysis

### Overview
Sistem sekarang dilengkapi dengan integrasi Google Gemini AI untuk menganalisis soal matematika yang kompleks. Fitur ini secara otomatis diaktifkan ketika algoritma NLP sederhana mendeteksi operator campuran (Mix) atau operator tidak diketahui.

### Setup Gemini AI

1. **Install Package:**
```bash
pip install google-generativeai
```

2. **Dapatkan API Key:**
   - Kunjungi [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Buat API key baru

3. **Konfigurasi Environment:**
```env
GEMINI_API_KEY=your_api_key_here
```

4. **Restart aplikasi**

### Kapan Gemini Digunakan

Gemini AI akan dipanggil secara otomatis dalam endpoint `/api/solve_text` ketika:

- **Operator Tidak Diketahui**: Algoritma sederhana tidak dapat mengidentifikasi operator
- **Operator Campuran (Mix)**: Soal mengandung lebih dari satu operasi matematika
- **Soal Kompleks**: Mengandung kata penghubung seperti "kemudian", "lalu", "setelah itu"

### Contoh Penggunaan

**Request ke `/api/solve_text`:**
```json
{
  "text_input": "Ana membeli 3 kotak permen, setiap kotak berisi 5 permen, kemudian dia memberikan 10 permen kepada temannya"
}
```

**Response dengan Gemini Analysis:**
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

### Testing Gemini

**Check Setup Status:**
```bash
GET /api/gemini/setup-check
```

**Test Analysis (Guru Only):**
```json
POST /api/teacher/test-gemini-analysis
Authorization: Bearer <teacher_token>

{
  "soal_text": "Budi membeli 4 kotak pensil, setiap kotak berisi 6 pensil, kemudian dia memberikan 8 pensil kepada adiknya"
}
```

### Error Handling

Sistem akan fallback ke analisis sederhana jika:
- API key tidak tersedia
- Gemini API mengalami error
- Package google-generativeai tidak terinstall

Lihat `GEMINI_MATH_ANALYSIS_GUIDE.md` untuk dokumentasi lengkap.

## Struktur Database

### Tabel Users
- id (PK)
- email
- password
- nama_lengkap
- jenis_kelamin

### Tabel Kelas
- id (PK)
- nama

### Tabel Siswa
- no (PK)
- NISN
- nama_siswa
- kelas (FK)

### Tabel Ujian
- id (PK)
- nama_ujian
- kelas (FK)
- pelaksanaan
- status

### Tabel Ujian Siswa
- id (PK)
- ujian (FK)
- siswa (FK)
- nilai
- label_nilai
- deskripsi_analisis

### Tabel Soal
- id (PK)
- soal
- ujian (FK)

### Tabel Jawaban Siswa
- id (PK)
- siswa (FK)
- soal (FK)
- status

## Troubleshooting

1. Error "No module named 'flask_sqlalchemy'":
```bash
pip install flask-sqlalchemy
```

2. Error koneksi database:
- Pastikan MySQL/MariaDB berjalan
- Periksa konfigurasi di file `.env`
- Pastikan database `school_db` sudah dibuat

3. Error Tesseract OCR:
- Pastikan Tesseract terinstal dengan benar
- Periksa path Tesseract di `app.py`

## Kontribusi

1. Fork repository
2. Buat branch fitur (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## Lisensi

Distribusikan di bawah lisensi MIT. Lihat `LICENSE` untuk informasi lebih lanjut. 