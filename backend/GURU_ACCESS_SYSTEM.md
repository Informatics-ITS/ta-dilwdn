# 🏫 Sistem Akses Guru Berdasarkan Kelas - Dokumentasi

## 📋 Overview

Sistem ini mengimplementasikan pembatasan akses guru dimana setiap guru hanya dapat melihat dan mengelola data kelas yang mereka buat sendiri. Setiap kelas memiliki `guru_id` yang menghubungkannya dengan guru pembuat.

## 🔧 Perubahan Arsitektur Database

### 1. **Struktur Tabel Kelas yang Diperbarui**

```sql
CREATE TABLE kelas (
    id INT PRIMARY KEY,
    nama VARCHAR(50) NOT NULL,
    guru_id INT NOT NULL,
    FOREIGN KEY (guru_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Perubahan:**
- ✅ Ditambahkan kolom `guru_id` dengan foreign key ke tabel `users`
- ✅ Setiap kelas sekarang terikat pada satu guru spesifik

### 2. **Model SQLAlchemy yang Diperbarui**

```python
class Kelas(db.Model):
    __tablename__ = 'kelas'
    
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(50), nullable=False)
    guru_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    siswa = db.relationship('Siswa', backref='kelas_ref', lazy=True)
    ujian = db.relationship('Ujian', backref='kelas_ref', lazy=True)
    guru = db.relationship('User', backref='kelas_mengajar', lazy=True)
```

## 🛡️ Sistem Pembatasan Akses

### **Endpoint yang Diperbarui dengan Filter Guru**

1. **Kelas Management**
   - `GET /api/teacher/kelas` - Hanya tampilkan kelas milik guru
   - `POST /api/teacher/kelas` - Auto-assign guru_id dari session
   - `PUT /api/teacher/kelas/<id>` - Cek kepemilikan sebelum update
   - `DELETE /api/teacher/kelas/<id>` - Cek kepemilikan sebelum delete

2. **Siswa Management**
   - `GET /api/teacher/kelas/<kelas_id>/siswa` - Filter berdasarkan guru_id
   - `POST /api/teacher/siswa` - Hanya bisa tambah ke kelas sendiri
   - `PUT /api/teacher/siswa/<no>` - Hanya bisa edit siswa di kelas sendiri
   - `DELETE /api/teacher/siswa/<no>` - Hanya bisa hapus siswa di kelas sendiri

3. **Dashboard dan Statistik**
   - `GET /api/teacher/dashboard` - Statistik hanya untuk kelas guru
   - `GET /api/teacher/dashboard/stats` - Menggunakan stored procedure

4. **Ujian dan Analisis**
   - `GET /api/teacher/ujian/<ujian_id>/detail-report` - Cek kepemilikan ujian
   - `GET /api/teacher/ujian/<ujian_id>/comparison-report` - Cek kepemilikan ujian
   - `POST /api/teacher/ujian/<ujian_id>/analyze-all-answers` - Cek kepemilikan ujian

## 📊 Stored Procedures Baru

### 1. **get_ujian_siswa_by_guru(guru_id)**
```sql
-- Mendapatkan semua ujian siswa untuk guru tertentu
CALL get_ujian_siswa_by_guru(2); -- Untuk guru dengan ID 2
```

### 2. **get_guru_dashboard_stats(guru_id)**
```sql
-- Mendapatkan statistik dashboard untuk guru tertentu
CALL get_guru_dashboard_stats(2); -- Statistik guru dengan ID 2
```

## 🎯 Data Seed dengan Multi-Guru

### **Guru dalam Sistem:**
1. **Guru Matematika (ID: 2)** - `guru@school.com`
   - Kelas 1: Kelas X IPA 1
   - Kelas 4: Kelas XI IPA 2  
   - Kelas 99: Kelas Test

2. **Guru Fisika (ID: 3)** - `guru2@school.com`
   - Kelas 2: Kelas X IPA 2

3. **Guru Kimia (ID: 4)** - `guru3@school.com`
   - Kelas 3: Kelas XI IPA 1

### **Distribusi Siswa:**
- **Kelas 1 & 4 (Guru Matematika)**: Budi Santoso, Test Siswa, Siti Aminah
- **Kelas 2 (Guru Fisika)**: Ahmad Fauzi
- **Kelas 3 (Guru Kimia)**: Rina Sari

## 🔍 Testing dan Verifikasi

### **Script Test:** `test_guru_access.py`

Mengverifikasi:
- ✅ Pembagian kelas per guru
- ✅ Siswa yang terikat pada kelas guru
- ✅ Ujian yang dibuat per guru
- ✅ Stored procedures berfungsi dengan benar
- ✅ Statistik dashboard akurat per guru

### **Hasil Test:**
```
✅ Guru Matematika: 3 kelas, 3 siswa, 3 ujian (Rata-rata: 91.67)
✅ Guru Fisika: 1 kelas, 1 siswa, 1 ujian (Rata-rata: 75.00)
✅ Guru Kimia: 1 kelas, 1 siswa, 1 ujian (Rata-rata: 95.00)
```

## 🚀 Implementasi dan Deployment

### **Langkah-langkah Reset Database:**

1. **Reset struktur database:**
   ```bash
   python reset_database.py
   ```

2. **Seed data dengan guru_id:**
   ```bash
   python seed_database.py
   ```

3. **Verifikasi sistem:**
   ```bash
   python test_guru_access.py
   ```

### **Login Credentials untuk Testing:**

| Role | Email | Password | Akses |
|------|-------|----------|-------|
| Guru Matematika | `guru@school.com` | `guru123` | Kelas 1, 4, 99 |
| Guru Fisika | `guru2@school.com` | `guru123` | Kelas 2 |
| Guru Kimia | `guru3@school.com` | `guru123` | Kelas 3 |

## 🛡️ Security Features

### **Access Control Measures:**
1. ✅ **Session-based Authentication** - Menggunakan `guru_id` dari session
2. ✅ **Database-level Filtering** - Query JOIN dengan `guru_id`
3. ✅ **Ownership Validation** - Cek kepemilikan sebelum aksi CRUD
4. ✅ **Stored Procedure Security** - Filter data di level database

### **Error Handling:**
- `404` - "Kelas not found or access denied"
- `403` - "Teacher access required"
- `401` - "Login required"

## 📈 Performance Optimizations

1. **Database Indexes** - Index pada `guru_id` untuk query cepat
2. **Stored Procedures** - Reduce round-trip database calls
3. **Efficient JOINs** - Minimize data transfer dengan filter di database
4. **Session Caching** - Store `guru_id` dalam session untuk akses cepat

## 🔄 Migration Path

Untuk sistem yang sudah ada:
1. **Backup data** sebelum migrasi
2. **Tambah kolom** `guru_id` ke tabel `kelas`
3. **Assign guru_id** berdasarkan logic bisnis atau default value
4. **Update aplikasi** dengan endpoint yang diperbarui
5. **Test thoroughly** dengan berbagai skenario guru

---

## ✅ Status Implementasi

- [x] ✅ **Database Schema** - Kolom guru_id ditambahkan
- [x] ✅ **Models Update** - SQLAlchemy models diperbarui
- [x] ✅ **API Endpoints** - Semua endpoint teacher dengan filter guru_id
- [x] ✅ **Stored Procedures** - Procedures baru untuk guru-specific data
- [x] ✅ **Data Seeding** - Multi-guru dengan distribusi kelas yang realistis
- [x] ✅ **Testing** - Comprehensive testing script
- [x] ✅ **Documentation** - Dokumentasi lengkap dengan contoh

**Sistem siap untuk production!** 🎉 