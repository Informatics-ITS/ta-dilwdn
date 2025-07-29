# Panduan Role Guru - School Management System

## Overview
Role guru memungkinkan pengguna untuk mengelola kelas dan siswa dengan fitur-fitur khusus yang dirancang untuk kebutuhan administrasi sekolah.

## Fitur Utama

### 1. Autentikasi Guru
- Login menggunakan email dan password
- Role harus diset sebagai 'guru' di database
- Session management dengan token

### 2. Manajemen Kelas
- Membuat kelas baru
- Mengupdate nama kelas
- Menghapus kelas (dengan validasi)
- Melihat daftar kelas dengan jumlah siswa

### 3. Manajemen Siswa
- Membuat siswa baru dengan password default NISN
- Import siswa dari file Excel
- Update data siswa
- Hapus siswa (dengan validasi)
- Melihat siswa berdasarkan kelas

### 4. Dashboard Guru
- Statistik total kelas, siswa, dan ujian
- Daftar kelas dengan jumlah siswa

## Setup Awal

### 1. Membuat User Guru
Jalankan script untuk membuat user guru contoh:
```bash
python create_teacher_user.py
```

Atau buat manual melalui API:
```json
POST /api/users
{
    "email": "guru@sekolah.com",
    "password": "password123",
    "nama_lengkap": "Guru Matematika",
    "jenis_kelamin": "laki-laki",
    "role": "guru"
}
```

### 2. Login Guru
```json
POST /api/teacher/login
{
    "email": "guru@sekolah.com",
    "password": "password123"
}
```

## Workflow Guru

### 1. Membuat Kelas
```json
POST /api/teacher/kelas
Authorization: Bearer <teacher_token>
{
    "id": 1,
    "nama": "Kelas X IPA 1"
}
```

### 2. Menambah Siswa
#### A. Satu per satu:
```json
POST /api/teacher/siswa
Authorization: Bearer <teacher_token>
{
    "NISN": "1234567890",
    "nama_siswa": "John Doe",
    "kelas": 1
}
```

#### B. Multiple siswa:
```json
POST /api/teacher/siswa/bulk
Authorization: Bearer <teacher_token>
{
    "siswa_list": [
        {
            "NISN": "1234567890",
            "nama_siswa": "John Doe",
            "kelas": 1
        },
        {
            "NISN": "1234567891",
            "nama_siswa": "Jane Smith",
            "kelas": 1
        }
    ]
}
```

#### C. Import dari Excel:
```json
POST /api/teacher/siswa/excel
Authorization: Bearer <teacher_token>
Content-Type: multipart/form-data

file: [Excel file dengan kolom NISN, nama_siswa, kelas]
```

### 3. Melihat Dashboard
```json
GET /api/teacher/dashboard
Authorization: Bearer <teacher_token>
```

Response:
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

### 4. Melihat Siswa per Kelas
```json
GET /api/teacher/kelas/1/siswa
Authorization: Bearer <teacher_token>
```

## Validasi dan Keamanan

### 1. Validasi Kelas
- Tidak bisa menghapus kelas yang memiliki siswa
- Tidak bisa menghapus kelas yang memiliki ujian
- ID kelas harus unik

### 2. Validasi Siswa
- NISN harus unik
- Kelas harus sudah ada di database
- Tidak bisa menghapus siswa yang memiliki hasil ujian
- Tidak bisa menghapus siswa yang memiliki jawaban

### 3. Password Default
- Setiap siswa baru otomatis mendapat password = NISN
- Guru dapat mengubah password siswa melalui update

## Error Handling

### 1. Kelas Errors
```json
{
    "error": "Kelas with this ID already exists"
}
```

```json
{
    "error": "Cannot delete kelas with existing students"
}
```

### 2. Siswa Errors
```json
{
    "error": "Student with this NISN already exists"
}
```

```json
{
    "error": "Kelas not found"
}
```

### 3. Authentication Errors
```json
{
    "error": "Access denied. Teacher role required"
}
```

## Contoh File Excel

Buat file Excel dengan format:
| NISN      | nama_siswa   | kelas |
|-----------|--------------|-------|
| 1234567890| John Doe     | 1     |
| 1234567891| Jane Smith   | 1     |
| 1234567892| Bob Johnson  | 2     |

## Testing dengan Postman

1. Import collection `Dilla_School Management API.postman_collection.json`
2. Set variable `base_url` = `http://localhost:5000`
3. Login guru dan copy token ke variable `teacher_token`
4. Test semua endpoint guru

## Tips Penggunaan

1. **Urutan Operasi**: Buat kelas dulu, baru tambah siswa
2. **NISN Unik**: Pastikan NISN tidak duplikat
3. **Password**: Siswa dapat login dengan NISN sebagai password
4. **Excel Import**: Gunakan format yang benar untuk import massal
5. **Validasi**: Sistem akan mencegah penghapusan data yang masih digunakan

## Troubleshooting

### 1. Login Gagal
- Pastikan role user = 'guru'
- Periksa email dan password
- Pastikan user sudah dibuat

### 2. Import Excel Gagal
- Pastikan format file .xlsx
- Periksa nama kolom: NISN, nama_siswa, kelas
- Pastikan kelas sudah ada di database

### 3. Error Validasi
- Periksa apakah data yang akan dihapus masih digunakan
- Pastikan NISN tidak duplikat
- Periksa apakah kelas sudah ada

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/teacher/login` | Login guru |
| GET | `/api/teacher/profile` | Profil guru |
| POST | `/api/teacher/logout` | Logout guru |
| GET | `/api/teacher/dashboard` | Dashboard guru |
| GET | `/api/teacher/kelas` | Daftar kelas |
| POST | `/api/teacher/kelas` | Buat kelas |
| PUT | `/api/teacher/kelas/<id>` | Update kelas |
| DELETE | `/api/teacher/kelas/<id>` | Hapus kelas |
| GET | `/api/teacher/kelas/<id>/siswa` | Siswa per kelas |
| POST | `/api/teacher/siswa` | Buat siswa |
| POST | `/api/teacher/siswa/bulk` | Buat multiple siswa |
| PUT | `/api/teacher/siswa/<no>` | Update siswa |
| DELETE | `/api/teacher/siswa/<no>` | Hapus siswa |
| POST | `/api/teacher/siswa/excel` | Import siswa Excel | 