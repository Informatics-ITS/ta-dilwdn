# 🎯 Panduan Analisis Tingkat Kesulitan Soal

## Overview

Sistem sekarang dilengkapi dengan **analisis tingkat kesulitan otomatis** berdasarkan range bilangan cacah yang digunakan dalam soal matematika. Fitur ini membantu guru memahami level soal dan memberikan feedback yang lebih tepat kepada siswa.

## 📊 Klasifikasi Tingkat Kesulitan

### Penjumlahan dan Pengurangan

| Range Bilangan | Level | Kategori | Complexity Score | Contoh |
|----------------|-------|----------|------------------|--------|
| ≤ 20 | `dasar` | elementary | 1 | 15 + 5 = 20 |
| ≤ 100 | `menengah` | intermediate | 2 | 85 - 25 = 60 |
| ≤ 1000 | `lanjut` | advanced | 3 | 450 + 350 = 800 |
| > 1000 | `sangat_lanjut` | expert | 4 | 1500 - 800 = 700 |

### Perkalian dan Pembagian

| Range Bilangan | Level | Kategori | Complexity Score | Contoh |
|----------------|-------|----------|------------------|--------|
| ≤ 100 | `dasar` | elementary | 2 | 8 × 12 = 96 |
| > 100 | `lanjut` | advanced | 3 | 25 × 150 = 3750 |

**Catatan:** Perkalian dan pembagian memiliki complexity score yang lebih tinggi karena secara kognitif lebih kompleks dibanding penjumlahan/pengurangan.

## 🔧 Implementasi Teknis

### Function `get_difficulty_level()`

```python
from app import get_difficulty_level

# Contoh penggunaan
result = get_difficulty_level("Penjumlahan", ["15", "5"])
print(result)
# Output:
{
    "level": "dasar",
    "description": "Penjumlahan bilangan cacah hingga 20",
    "max_number": 15,
    "category": "elementary",
    "complexity_score": 1
}
```

### Integrasi dengan Comparison Analysis

Analisis tingkat kesulitan terintegrasi dengan sistem perbandingan jawaban:

```python
from app import compare_answers_internal

ai_answer = {
    "operator": "Pengurangan",
    "angka_dalam_soal": "85,25", 
    "jawaban": "60"
}

student_answer = {
    "operator": "Pengurangan",
    "angka_dalam_soal": "85,25",
    "jawaban": "60"
}

result = compare_answers_internal(ai_answer, student_answer)
print(result['difficulty_analysis'])
# Output:
{
    "level": "menengah",
    "description": "Pengurangan bilangan cacah hingga 100",
    "max_number": 85,
    "category": "intermediate", 
    "complexity_score": 2
}
```

## 📝 Format Response API

### Enhanced API Response

```json
{
  "status": "excellent",
  "deskripsi_analisis": "Siswa telah menjawab dengan benar semua aspek soal (4/4 poin) pada Pengurangan bilangan cacah hingga 100",
  "nilai": 4,
  "nilai_maksimal": 4,
  "persentase": 100.0,
  "parameter_salah": [],
  "parameter_benar": ["operator", "operan_1", "operan_2", "jawaban"],
  "koreksi": [],
  "difficulty_analysis": {
    "level": "menengah",
    "description": "Pengurangan bilangan cacah hingga 100",
    "max_number": 85,
    "category": "intermediate",
    "complexity_score": 2
  }
}
```

## 🎯 Contoh Penggunaan

### Soal Level Dasar

**Input:** `"Andi punya 15 kelereng, temannya beri 5 lagi. Berapa total?"`

**Analisis:**
- Operasi: Penjumlahan
- Angka terbesar: 15 (≤ 20)
- **Level: `dasar`**
- **Complexity Score: 1**
- **Kategori: elementary**

### Soal Level Menengah

**Input:** `"Di perpustakaan ada 85 buku. Siswa meminjam 25 buku. Berapa yang tersisa?"`

**Analisis:**
- Operasi: Pengurangan
- Angka terbesar: 85 (≤ 100)
- **Level: `menengah`**
- **Complexity Score: 2**
- **Kategori: intermediate**

### Soal Level Lanjut

**Input:** `"450 apel dibagi kepada 150 anak sama rata. Berapa apel per anak?"`

**Analisis:**
- Operasi: Pembagian
- Angka terbesar: 450 (> 100)
- **Level: `lanjut`**
- **Complexity Score: 3**
- **Kategori: advanced**

## 🧪 Testing

### Unit Tests untuk Difficulty Analysis

```python
# File: test_nlp_extraction.py
def test_difficulty_level_analysis(self):
    """Test difficulty level analysis based on number ranges"""
    
    # Test penjumlahan level dasar
    result = get_difficulty_level("Penjumlahan", ["15", "5"])
    assert result['level'] == 'dasar'
    assert result['complexity_score'] == 1
    
    # Test pengurangan level menengah
    result = get_difficulty_level("Pengurangan", ["85", "25"])
    assert result['level'] == 'menengah'
    assert result['complexity_score'] == 2
    
    # Test perkalian level lanjut
    result = get_difficulty_level("Perkalian", ["25", "150"])
    assert result['level'] == 'lanjut'
    assert result['complexity_score'] == 3
```

### Quick Test

```bash
cd backend
python test_quick.py
```

Output akan menampilkan analisis tingkat kesulitan:
```
Test 1: Andi memiliki 15 jeruk. Dia memberikan 7 kepada...
  Operator: Pengurangan ✅
  Jawaban: 8 ✅
  Tingkat Kesulitan: dasar ✅
  Deskripsi: Pengurangan bilangan cacah hingga 20
  🎉 PASS (dengan analisis tingkat kesulitan)
```

## 📚 Educational Benefits

### Untuk Guru

1. **Assessment yang Tepat**: Dapat menilai siswa sesuai level kemampuan
2. **Adaptif Learning**: Menyesuaikan soal berdasarkan tingkat kesulitan
3. **Progress Tracking**: Memonitor kemajuan siswa dari level dasar ke lanjut
4. **Targeted Teaching**: Fokus pada area yang sesuai dengan kemampuan siswa

### Untuk Siswa

1. **Appropriate Challenge**: Mendapat soal sesuai kemampuan
2. **Clear Progress**: Memahami level kemampuan mereka
3. **Confidence Building**: Tidak overwhelmed dengan soal yang terlalu sulit
4. **Motivation**: Dapat melihat progres ke level yang lebih tinggi

## 🔄 Workflow Integration

### 1. Penilaian Otomatis
```
Soal Input → NLP Extraction → Difficulty Analysis → 4-Point Scoring → Result
```

### 2. Adaptive Assessment
```
Student Level → Difficulty Filter → Appropriate Questions → Performance Analysis
```

### 3. Progress Tracking
```
Historical Data → Difficulty Trends → Learning Path → Recommendations
```

## 🎨 Frontend Integration Guide

### Menampilkan Level Kesulitan

```javascript
const DifficultyBadge = ({ difficulty }) => {
  const config = {
    'dasar': { color: 'green', icon: '🟢', text: 'Dasar' },
    'menengah': { color: 'blue', icon: '🔵', text: 'Menengah' },
    'lanjut': { color: 'orange', icon: '🟠', text: 'Lanjut' },
    'sangat_lanjut': { color: 'red', icon: '🔴', text: 'Sangat Lanjut' }
  };
  
  const { color, icon, text } = config[difficulty.level] || {};
  
  return (
    <div className={`badge badge-${color}`}>
      {icon} {text} (Score: {difficulty.complexity_score}/4)
    </div>
  );
};
```

### Progress Indicator

```javascript
const ProgressIndicator = ({ currentLevel, targetLevel }) => {
  const levels = ['dasar', 'menengah', 'lanjut', 'sangat_lanjut'];
  const current = levels.indexOf(currentLevel);
  const target = levels.indexOf(targetLevel);
  
  return (
    <div className="progress-bar">
      {levels.map((level, index) => (
        <div key={level} className={`
          progress-step 
          ${index <= current ? 'completed' : ''}
          ${index === target ? 'target' : ''}
        `}>
          {level}
        </div>
      ))}
    </div>
  );
};
```

## 🚀 Roadmap

### Phase 1 (Current) ✅
- [x] Basic difficulty classification
- [x] Integration with comparison analysis
- [x] Unit testing
- [x] Demo functionality

### Phase 2 (Future)
- [ ] Machine learning-based difficulty prediction
- [ ] Adaptive question generation
- [ ] Learning path optimization
- [ ] Performance correlation analysis

### Phase 3 (Future)
- [ ] Multi-operation complexity analysis
- [ ] Individual student adaptation
- [ ] Teacher dashboard analytics
- [ ] Recommendation engine

## 📞 Support & Troubleshooting

### Common Issues

1. **Wrong difficulty level detected**
   - Check number extraction accuracy
   - Verify operation detection
   - Test with different number formats

2. **Missing difficulty analysis in response**
   - Ensure latest API version
   - Check comparison_analysis endpoint
   - Verify input format

3. **Inconsistent complexity scores**
   - Verify operation classification
   - Check number range logic
   - Test edge cases

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Will show detailed difficulty analysis steps
result = get_difficulty_level("Penjumlahan", ["15", "5"])
```

---

*Fitur analisis tingkat kesulitan menghadirkan pembelajaran matematika yang lebih personal dan efektif!* 🎯 