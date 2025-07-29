# Role Guru - School Management System

## 🎯 Overview
Role guru telah berhasil diimplementasikan dengan fitur lengkap untuk mengelola kelas dan siswa. Guru dapat membuat kelas, menambah siswa, dan mengelola data sekolah dengan password default NISN untuk setiap siswa.

## ✅ Fitur yang Telah Diimplementasikan

### 1. **Autentikasi Guru**
- ✅ Login dengan email dan password
- ✅ Role-based access control (hanya user dengan role 'guru')
- ✅ Session management
- ✅ Logout functionality

### 2. **Manajemen Kelas**
- ✅ Membuat kelas baru
- ✅ Mengupdate nama kelas
- ✅ Menghapus kelas (dengan validasi)
- ✅ Melihat daftar kelas dengan jumlah siswa

### 3. **Manajemen Siswa**
- ✅ Membuat siswa baru dengan password default NISN
- ✅ Import siswa dari file Excel
- ✅ Update data siswa
- ✅ Hapus siswa (dengan validasi)
- ✅ Melihat siswa berdasarkan kelas
- ✅ Bulk create siswa

### 4. **Dashboard Guru**
- ✅ Statistik total kelas, siswa, dan ujian
- ✅ Daftar kelas dengan jumlah siswa

## 🔧 Setup dan Konfigurasi

### 1. **Database Migration**
```bash
# Jalankan script untuk menambahkan kolom yang diperlukan
python add_role_column.py
```

### 2. **Membuat User Guru**
```bash
# Jalankan script untuk membuat user guru contoh
python create_teacher_user.py
```

### 3. **User Guru Default**
- **Email**: `guru@sekolah.com`
- **Password**: `password123`
- **Role**: `guru`

## 📋 API Endpoints Guru

### **Authentication**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/teacher/login` | Login guru |
| GET | `/api/teacher/profile` | Profil guru |
| POST | `/api/teacher/logout` | Logout guru |

### **Dashboard & Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/teacher/dashboard` | Dashboard guru |
| GET | `/api/teacher/kelas` | Daftar kelas |
| POST | `/api/teacher/kelas` | Buat kelas |
| PUT | `/api/teacher/kelas/<id>` | Update kelas |
| DELETE | `/api/teacher/kelas/<id>` | Hapus kelas |

### **Student Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/teacher/kelas/<id>/siswa` | Siswa per kelas |
| POST | `/api/teacher/siswa` | Buat siswa |
| POST | `/api/teacher/siswa/bulk` | Buat multiple siswa |
| PUT | `/api/teacher/siswa/<no>` | Update siswa |
| DELETE | `/api/teacher/siswa/<no>` | Hapus siswa |
| POST | `/api/teacher/siswa/excel` | Import siswa Excel |

## 🔐 Keamanan dan Validasi

### **Role-Based Access Control**
- Semua endpoint guru memerlukan role 'guru'
- Decorator `@teacher_required` untuk validasi
- Session-based authentication

### **Validasi Data**
- **Kelas**: Tidak bisa dihapus jika ada siswa atau ujian
- **Siswa**: Tidak bisa dihapus jika ada hasil ujian atau jawaban
- **NISN**: Harus unik untuk setiap siswa
- **Password**: Default NISN, bisa diubah oleh guru

### **Error Handling**
- Proper error messages untuk setiap validasi
- Database constraint handling
- Session validation

## 📊 Workflow Guru

### **1. Login Guru**
```bash
curl -X POST http://localhost:5000/api/teacher/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "guru@sekolah.com",
    "password": "password123"
  }'
```

### **2. Membuat Kelas**
```bash
curl -X POST http://localhost:5000/api/teacher/kelas \
  -H "Authorization: Bearer <teacher_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "nama": "Kelas X IPA 1"
  }'
```

### **3. Menambah Siswa**
```bash
curl -X POST http://localhost:5000/api/teacher/siswa \
  -H "Authorization: Bearer <teacher_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "NISN": "1234567890",
    "nama_siswa": "John Doe",
    "kelas": 1
  }'
```

### **4. Import Siswa dari Excel**
```bash
curl -X POST http://localhost:5000/api/teacher/siswa/excel \
  -H "Authorization: Bearer <teacher_token>" \
  -F "file=@siswa_data.xlsx"
```

## 📁 File Excel Format

### **Kolom yang Diperlukan:**
| Kolom | Deskripsi | Contoh |
|-------|-----------|--------|
| NISN | Nomor Induk Siswa Nasional | 1234567890 |
| nama_siswa | Nama lengkap siswa | John Doe |
| kelas | ID kelas | 1 |

### **Contoh Data:**
```csv
NISN,nama_siswa,kelas
1234567890,John Doe,1
1234567891,Jane Smith,1
1234567892,Bob Johnson,2
```

## 🧪 Testing dengan Postman

### **1. Import Collection**
- Import file `Dilla_School Management API.postman_collection.json`
- Set variable `base_url` = `http://localhost:5000`

### **2. Login dan Set Token**
1. Jalankan "Teacher Login"
2. Copy token dari response
3. Set variable `teacher_token` dengan token tersebut

### **3. Test Endpoints**
- Test semua endpoint di section "Teacher Management"
- Verifikasi response dan error handling

## 🔄 Integrasi dengan Role Lain

### **Guru ↔ Admin**
- Admin dapat membuat user guru melalui `/api/users`
- Guru hanya dapat mengakses endpoint khusus guru

### **Guru ↔ Siswa**
- Guru membuat siswa dengan password default NISN
- Siswa dapat login dengan NISN dan password NISN
- Guru dapat melihat hasil ujian siswa

## 📈 Statistik dan Monitoring

### **Dashboard Guru Menampilkan:**
- Total kelas
- Total siswa
- Total ujian
- Daftar kelas dengan jumlah siswa

### **Validasi Real-time:**
- Cek ketersediaan NISN
- Validasi kelas sebelum hapus
- Validasi siswa sebelum hapus

## 🛠️ Troubleshooting

### **Error Umum:**

1. **"Access denied. Teacher role required"**
   - Pastikan user memiliki role 'guru'
   - Periksa token authentication

2. **"Cannot delete kelas with existing students"**
   - Pindahkan siswa ke kelas lain terlebih dahulu
   - Atau hapus siswa dari kelas tersebut

3. **"Student with this NISN already exists"**
   - Gunakan NISN yang berbeda
   - Atau update siswa yang sudah ada

4. **"Kelas not found"**
   - Pastikan kelas sudah dibuat
   - Periksa ID kelas yang digunakan

## 🚀 Deployment

### **Requirements:**
- Python 3.8+
- MySQL/MariaDB
- Flask dan dependencies
- Tesseract OCR (untuk fitur AI)

### **Environment Variables:**
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=school_db
```

### **Setup Commands:**
```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
python create_database.py
python add_role_column.py

# Create users
python create_teacher_user.py

# Run application
python app.py
```

## 📝 Catatan Penting

1. **Password Default**: Setiap siswa baru otomatis mendapat password = NISN
2. **Role Validation**: Semua endpoint guru memerlukan role 'guru'
3. **Data Integrity**: Sistem mencegah penghapusan data yang masih digunakan
4. **Excel Import**: Format file harus sesuai dengan template yang disediakan
5. **Session Management**: Token guru terpisah dari token siswa

## 🎉 Kesimpulan

Role guru telah berhasil diimplementasikan dengan fitur lengkap:
- ✅ Autentikasi dan otorisasi
- ✅ Manajemen kelas dan siswa
- ✅ Import data dari Excel
- ✅ Dashboard dengan statistik
- ✅ Validasi dan error handling
- ✅ Integrasi dengan role lain
- ✅ Dokumentasi lengkap

Sistem siap digunakan untuk manajemen sekolah dengan role guru yang dapat mengelola kelas dan siswa secara efektif! 