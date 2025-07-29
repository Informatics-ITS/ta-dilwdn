# Sistem Penilaian 4 Poin dan Testing NLP

## Overview

Sistem penilaian telah diperbarui dari sistem 3 poin menjadi sistem **4 poin** yang lebih detail dan akurat dalam mengevaluasi jawaban siswa pada soal cerita matematika.

## Sistem Penilaian Baru (4 Poin)

### Komponen Penilaian

Setiap soal dinilai berdasarkan 4 komponen, masing-masing bernilai **1 poin**:

1. **Operan 1** (1 poin) - Angka pertama dalam soal
2. **Operan 2** (1 poin) - Angka kedua dalam soal  
3. **Operator** (1 poin) - Jenis operasi matematika (+, -, ×, ÷)
4. **Jawaban** (1 poin) - Hasil akhir perhitungan

### Status Penilaian

Berdasarkan total poin yang diperoleh:

| Poin | Status | Deskripsi |
|------|--------|-----------|
| 4/4 | `excellent` | Semua aspek benar |
| 3/4 | `good` | Hampir sempurna, 1 kesalahan |
| 2/4 | `fair` | Cukup baik, 2 kesalahan |
| 1/4 | `poor` | Perlu perbaikan, 3 kesalahan |
| 0/4 | `incorrect` | Semua aspek salah |

### Contoh Penilaian

**Soal:** `3 + 2 = 5`

**Jawaban Siswa:** `3 + 2 = 6`

**Analisis:**
- ✅ Operan 1: `3` (benar) → +1 poin
- ✅ Operan 2: `2` (benar) → +1 poin  
- ✅ Operator: `+` (benar) → +1 poin
- ❌ Jawaban: `6` (salah, seharusnya `5`) → +0 poin

**Total: 3/4 poin (Status: `good`)**

## Analisis Tingkat Kesulitan (Fitur Baru!)

### Klasifikasi Berdasarkan Range Bilangan Cacah

Sistem sekarang menganalisis tingkat kesulitan soal berdasarkan jenis operasi dan range bilangan cacah:

#### Penjumlahan dan Pengurangan

| Range Bilangan | Level | Kategori | Complexity Score |
|----------------|-------|----------|------------------|
| ≤ 20 | `dasar` | elementary | 1 |
| ≤ 100 | `menengah` | intermediate | 2 |
| ≤ 1000 | `lanjut` | advanced | 3 |
| > 1000 | `sangat_lanjut` | expert | 4 |

#### Perkalian dan Pembagian

| Range Bilangan | Level | Kategori | Complexity Score |
|----------------|-------|----------|------------------|
| ≤ 100 | `dasar` | elementary | 2 |
| > 100 | `lanjut` | advanced | 3 |

### Contoh Analisis Tingkat Kesulitan

**Contoh 1: Level Dasar**
```
Soal: "Andi punya 15 kelereng, temannya beri 5 lagi. Berapa total?"
→ Range: 15 (≤ 20)
→ Operasi: Penjumlahan
→ Level: dasar (elementary, complexity: 1)
```

**Contoh 2: Level Menengah**
```
Soal: "Di toko ada 85 roti, terjual 25. Berapa yang tersisa?"
→ Range: 85 (≤ 100)
→ Operasi: Pengurangan  
→ Level: menengah (intermediate, complexity: 2)
```

**Contoh 3: Level Lanjut**
```
Soal: "450 apel dibagi ke 150 anak sama rata. Berapa per anak?"
→ Range: 450 (> 100)
→ Operasi: Pembagian
→ Level: lanjut (advanced, complexity: 3)
```

## Perubahan pada API

### Response Format Baru

API sekarang mengembalikan informasi yang lebih detail termasuk analisis tingkat kesulitan:

```json
{
  "status": "good",
  "deskripsi_analisis": "Siswa menjawab benar 3 dari 4 aspek: operator, operan 1, operan 2 (3/4 poin) pada Penjumlahan bilangan cacah hingga 20",
  "nilai": 3,
  "nilai_maksimal": 4,
  "persentase": 75.0,
  "parameter_salah": ["jawaban"],
  "parameter_benar": ["operator", "operan_1", "operan_2"],
  "koreksi": ["Jawaban yang benar adalah 5"],
  "difficulty_analysis": {
    "level": "dasar",
    "description": "Penjumlahan bilangan cacah hingga 20",
    "max_number": 15,
    "category": "elementary",
    "complexity_score": 1
  }
}
```

### Endpoints yang Diperbarui

1. **`/api/compare_answer`** - Perbandingan jawaban dengan sistem 4 poin
2. **`/api/student/exam/submit`** - Pengumpulan ujian dengan analisis detail
3. **`/api/teacher/ujian/{id}/detail-report`** - Laporan detail ujian
4. **`/api/pedagogic/analyze-answer`** - Analisis pedagogik

## Unit Testing untuk NLP Extraction

### Menjalankan Test

```bash
# Jalankan semua test
python run_tests.py

# Jalankan test cepat saja
python run_tests.py --quick

# Jalankan dengan output verbose
python run_tests.py --verbose

# Jalankan hanya unit test
python run_tests.py --unit

# Jalankan hanya integration test
python run_tests.py --integration
```

### Demo Script

Untuk menguji fungsi NLP secara interaktif:

```bash
# Jalankan demo lengkap
python demo_nlp_extraction.py

# Demo akan menampilkan:
# 1. Test soal cerita tanpa jawaban
# 2. Demo sistem penilaian 4 poin  
# 3. Mode interaktif untuk test custom
```

**Contoh Output Demo:**
```
Soal 1 (Perkalian):
'Setiap kotak berisi 6 pensil. Jika ada 4 kotak, berapa total pensil?'
------------------------------------------------------------
✅ HASIL EKSTRAKSI:
   Operator terdeteksi: Perkalian
   Angka yang diekstrak: 6,4
   Jawaban AI: 24

📊 EVALUASI:
   Operator ✅ BENAR (Expected: Perkalian)
   Jawaban ✅ BENAR (Expected: 24, Got: 24)
   🎉 BERHASIL TOTAL!
```

### Test Coverage

#### 1. Test Ekstraksi Dasar
- Operasi aritmatika dasar (+, -, ×, ÷)
- Berbagai simbol operator (x, ×, :, ÷)
- Input dengan spasi
- Soal cerita sederhana

#### 2. Test Soal Cerita Tanpa Jawaban (NEW!)
- **Pengurangan**: Soal tentang memberikan, meminjam, sisa
- **Perkalian**: Soal tentang kelompok, paket, baris-kolom
- **Pembagian**: Soal tentang membagi rata, pengelompokan
- AI harus menghitung jawaban sendiri dari konteks cerita

#### 3. Test Sistem 4 Poin
- Perfect match (4 poin)
- Good match (3 poin) 
- Fair match (2 poin)
- Poor match (1 poin)
- Incorrect (0 poin)

#### 4. Test Edge Cases
- Input kosong
- Format tidak valid
- Missing operands/operators
- Error handling
- Soal tanpa operasi matematika yang jelas

#### 5. Test Performa
- Kecepatan ekstraksi
- Konsistensi hasil
- Handling soal cerita kompleks

### Contoh Test Case

```python
def test_extract_math_simple_basic_operations(self):
    test_cases = [
        {
            'input': '3+2=5',
            'expected': {
                'operator': 'Penjumlahan',
                'angka_dalam_soal': '3,2',
                'jawaban': '5'
            }
        }
    ]
```

## Implementasi dalam Frontend

### Status Handling

Frontend perlu diperbarui untuk menangani status baru:

```javascript
const getStatusColor = (status) => {
  switch (status) {
    case 'excellent': return 'green';
    case 'good': return 'blue';
    case 'fair': return 'yellow';
    case 'poor': return 'orange';
    case 'incorrect': return 'red';
    default: return 'gray';
  }
};

const getStatusText = (status) => {
  switch (status) {
    case 'excellent': return 'Sangat Baik';
    case 'good': return 'Baik';
    case 'fair': return 'Cukup';
    case 'poor': return 'Kurang';
    case 'incorrect': return 'Salah';
    default: return 'Tidak Diketahui';
  }
};
```

### Progress Indicators

Tampilkan progress dengan bar atau circle:

```javascript
const ProgressCircle = ({ nilai, maksimal }) => {
  const percentage = (nilai / maksimal) * 100;
  return (
    <div className="progress-circle">
      <span>{nilai}/{maksimal}</span>
      <span>{percentage}%</span>
    </div>
  );
};
```

## Migration Guide

### Database Changes

Tidak ada perubahan skema database yang diperlukan. Data existing akan tetap kompatibel.

### API Client Updates

1. Update parsing response untuk field baru
2. Handle status enum yang baru
3. Tampilkan informasi detail poin

### Teacher Dashboard

1. Update statistik untuk sistem 4 poin
2. Tampilkan breakdown analisis per komponen
3. Grafik performa berdasarkan komponen

## Troubleshooting

### Common Issues

1. **ImportError saat run test**
   ```bash
   # Pastikan di directory backend
   cd backend
   python run_tests.py
   ```

2. **Test gagal untuk NLP extraction**
   - Periksa format input test case
   - Pastikan semua dependency tersedia

3. **Status tidak dikenali di frontend**
   - Update mapping status di frontend
   - Periksa API response format

### Debug Mode

Untuk debugging, aktifkan logging detail:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

### Untuk Developer

1. **Selalu jalankan test** sebelum commit
2. **Update test cases** saat menambah fitur baru
3. **Dokumentasikan** perubahan sistem penilaian

### Untuk Guru

1. **Review laporan detail** untuk memahami kesalahan siswa
2. **Gunakan analisis komponen** untuk targeted teaching
3. **Monitor trend** performa per komponen

### Untuk Siswa

1. **Perhatikan breakdown poin** untuk memahami kesalahan
2. **Fokus pada komponen** yang sering salah
3. **Latihan bertahap** per komponen

## NLP Enhancement (Fitur Baru!)

### Kemampuan Ekstraksi Soal Cerita

Sistem sekarang dapat menganalisis soal cerita **tanpa jawaban eksplisit** menggunakan keyword detection:

#### Keyword Detection untuk Operasi

| Operasi | Keywords |
|---------|----------|
| **Penjumlahan** | tambah, ditambah, jumlah, total, bertambah, menambah, gabungan |
| **Pengurangan** | kurang, dikurangi, sisa, tersisa, memberikan, memberi, berkurang, diambil |
| **Perkalian** | kali, dikali, setiap, per, masing-masing, baris, kelompok, pak, berisi |
| **Pembagian** | bagi, dibagi, rata, merata, sama banyak, per kelompok, ke dalam |

#### Contoh Analisis Soal Cerita

**Input:** `"Setiap kotak berisi 6 pensil. Jika ada 4 kotak, berapa total pensil?"`

**AI Analysis:**
- Keywords terdeteksi: "setiap", "berisi" → **Perkalian**
- Angka diekstrak: `6, 4`
- Kalkulasi AI: `6 × 4 = 24`
- **Output:** `{"operator": "Perkalian", "angka_dalam_soal": "6,4", "jawaban": "24"}`

### Test Cases Soal Cerita

```python
# Contoh test case yang baru ditambahkan
story_cases = [
    # Pengurangan
    "Andi memiliki 15 jeruk. Dia memberikan 7 kepada temannya. Berapa yang tersisa?",
    
    # Perkalian  
    "Setiap kotak berisi 6 pensil. Ada 4 kotak. Berapa total pensil?",
    
    # Pembagian
    "24 permen dibagi rata kepada 6 anak. Berapa permen per anak?"
]
```

## Changelog

### Version 2.1.0 (Current)

- ✅ Sistem penilaian 4 poin
- ✅ Status enum baru (excellent/good/fair/poor/incorrect)
- ✅ Unit testing NLP extraction
- ✅ **Enhanced NLP dengan keyword detection**
- ✅ **Test soal cerita tanpa jawaban eksplisit**
- ✅ **Demo script interaktif**
- ✅ **Analisis tingkat kesulitan berdasarkan bilangan cacah** (NEW!)
- ✅ **Klasifikasi level dasar/menengah/lanjut untuk penjumlahan/pengurangan**
- ✅ **Klasifikasi level dasar/lanjut untuk perkalian/pembagian**
- ✅ **Complexity scoring 1-4 points**
- ✅ Update semua endpoints
- ✅ Enhanced comparison analysis

### Version 1.0.0 (Previous)

- ❌ Sistem penilaian 3 poin (deprecated)
- ❌ Binary correct/incorrect status
- ❌ Basic comparison

## Contributing

Untuk berkontribusi pada sistem penilaian:

1. Fork repository
2. Buat feature branch
3. **Jalankan semua test**: `python run_tests.py`
4. Commit dengan message yang jelas
5. Submit pull request

## Support

Jika ada pertanyaan atau issue terkait sistem penilaian baru:

1. Cek dokumentasi ini terlebih dahulu
2. Jalankan test untuk memastikan functionality
3. Buat issue di repository dengan detail lengkap 