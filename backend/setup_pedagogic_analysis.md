# 🚀 Setup Analisis Pedagogik - School Management System

## 📋 Prerequisites

### 1. **Python Environment**
- Python 3.8 atau lebih baru
- Virtual environment (recommended)

### 2. **Google AI Studio Account**
- Daftar di [Google AI Studio](https://makersuite.google.com/app/apikey)
- Buat API key untuk Gemini

### 3. **Database Setup**
- MySQL/MariaDB sudah terinstall
- Database `school_db` sudah dibuat
- Kolom `json_result` sudah ditambahkan

## 🔧 Installation Steps

### **Step 1: Install Dependencies**
```bash
# Install Google Generative AI package
pip install google-generativeai==0.3.2

# Atau update requirements.txt dan install semua
pip install -r requirements.txt
```

### **Step 2: Setup Environment Variables**
Buat atau update file `.env`:
```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=school_db

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Flask Configuration
SECRET_KEY=your-secret-key-here
```

### **Step 3: Get Gemini API Key**
1. Kunjungi [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Login dengan Google account
3. Klik "Create API Key"
4. Copy API key yang dihasilkan
5. Paste ke file `.env`

### **Step 4: Verify Database Schema**
Pastikan kolom `json_result` sudah ada:
```bash
python add_role_column.py
```

### **Step 5: Create Test Users**
```bash
python create_teacher_user.py
```

## 🧪 Testing Setup

### **Test 1: Check Service Status**
```bash
curl http://localhost:5000/api/pedagogic/status
```

**Expected Response:**
```json
{
    "available": true,
    "model": "gemini-2.0-flash-exp",
    "message": "Pedagogic analysis service is ready"
}
```

### **Test 2: Run Automated Tests**
```bash
python test_pedagogic_analysis.py
```

### **Test 3: Manual Testing dengan Postman**
1. Import collection `Dilla_School Management API.postman_collection.json`
2. Set variable `base_url` = `http://localhost:5000`
3. Login sebagai guru
4. Test endpoint pedagogic analysis

## 📊 Sample Data untuk Testing

### **1. Create Sample Soal**
```json
POST /api/soal
{
    "soal": "Budi memiliki 5 apel dan membeli 3 apel lagi. Berapa total apel yang dimiliki Budi?",
    "ujian": 1,
    "json_result": {
        "operator": "Penjumlahan",
        "angka_dalam_soal": "5,3",
        "jawaban": "8"
    }
}
```

### **2. Create Sample Jawaban Siswa**
```json
POST /api/jawaban-siswa
{
    "siswa": 1,
    "soal": 1,
    "status": "incorrect",
    "json_result": {
        "operator": "Penjumlahan",
        "angka_dalam_soal": "5,3",
        "jawaban": "7"
    }
}
```

### **3. Test Pedagogic Analysis**
```json
POST /api/pedagogic/analyze-answer
{
    "soal_id": 1,
    "jawaban_siswa_id": 1
}
```

## 🔍 Troubleshooting

### **Error: "Pedagogic analysis not available"**
**Solution:**
1. Install package: `pip install google-generativeai==0.3.2`
2. Set environment variable: `GEMINI_API_KEY=your_key`
3. Restart aplikasi

### **Error: "Invalid API key"**
**Solution:**
1. Periksa API key di Google AI Studio
2. Pastikan API key valid dan aktif
3. Periksa quota dan limits

### **Error: "Module not found"**
**Solution:**
1. Install dependencies: `pip install -r requirements.txt`
2. Aktifkan virtual environment
3. Periksa Python path

### **Error: "Database connection failed"**
**Solution:**
1. Periksa konfigurasi database di `.env`
2. Pastikan MySQL server running
3. Periksa credentials database

## 📈 Monitoring dan Logs

### **Check Application Logs**
```bash
# Run dengan debug mode
python app.py

# Monitor logs untuk error
tail -f app.log
```

### **Check API Response**
```bash
# Test endpoint status
curl -X GET http://localhost:5000/api/pedagogic/status

# Test dengan authentication
curl -X POST http://localhost:5000/api/teacher/login \
  -H "Content-Type: application/json" \
  -d '{"email": "guru@sekolah.com", "password": "password123"}'
```

## 🎯 Expected Results

### **Successful Setup:**
- ✅ Service status shows "available: true"
- ✅ Model shows "gemini-2.0-flash-exp"
- ✅ Teacher login successful
- ✅ Pedagogic analysis returns detailed results
- ✅ Database saves analysis results

### **Sample Analysis Output:**
```json
{
    "status": "success",
    "analisis_pedagogik": {
        "analisis_kognitif": {
            "tingkat_pemahaman": "Siswa menunjukkan pemahaman dasar...",
            "kesimpulan_kognitif": "Siswa berada pada tahap pemahaman dasar..."
        },
        "rekomendasi_pembelajaran": {
            "strategi_pembelajaran": "Gunakan pendekatan visual dan konkret...",
            "metode_remedial": "Pembelajaran individual dengan scaffolding..."
        }
    },
    "model_used": "gemini-2.0-flash-exp",
    "timestamp": "2024-01-15T10:30:00"
}
```

## 🚀 Production Deployment

### **Environment Variables (Production)**
```env
# Production Database
DB_HOST=production-db-host
DB_USER=production-user
DB_PASSWORD=secure-password
DB_NAME=production-db

# Production Gemini API
GEMINI_API_KEY=production-api-key

# Security
SECRET_KEY=very-secure-secret-key
FLASK_ENV=production
```

### **Security Considerations**
1. Use strong passwords
2. Enable HTTPS
3. Implement rate limiting
4. Monitor API usage
5. Regular security updates

## 📞 Support

### **Common Issues:**
- API quota exceeded
- Database connection issues
- Authentication problems
- Model response errors

### **Contact:**
- Check application logs
- Verify environment variables
- Test with sample data
- Review API documentation

## ✅ Checklist Setup

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Gemini API key obtained
- [ ] Environment variables set
- [ ] Database schema updated
- [ ] Test users created
- [ ] Service status checked
- [ ] Sample data created
- [ ] Analysis tested
- [ ] Results verified

**Setup selesai! Analisis pedagogik siap digunakan dengan Gemini 2.0 Flash! 🎉** 