# Unit Testing Guide untuk Compare Answers Internal

## Overview

Unit testing ini dirancang untuk menguji fungsi `compare_answers_internal` dan sistem scoring 4-point yang digunakan dalam aplikasi Dilla School Management. Testing mencakup berbagai skenario untuk memastikan akurasi perhitungan nilai dan penanganan berbagai format input.

## Struktur Testing

### 1. `test_compare_scoring.py`
File testing utama yang mencakup:

#### Test Classes:
- **TestCompareScoring**: Testing dasar untuk fungsi scoring
- **TestCompareScoringEdgeCases**: Testing untuk edge cases dan error handling

#### Test Categories:
- **Standardization Tests**: Menguji fungsi standarisasi operator, angka, dan jawaban
- **Scoring Tests**: Menguji perhitungan nilai (0-4 poin)
- **Edge Case Tests**: Menguji penanganan input yang tidak standar

### 2. `test_compare_integration.py`
File testing untuk skenario integrasi:

#### Test Categories:
- **Real-world Scenarios**: Testing dengan soal matematika yang realistis
- **Integration Tests**: Testing integrasi dengan Gemini AI
- **Format Compatibility**: Testing kompatibilitas berbagai format input

### 3. `run_compare_tests.py`
Script untuk menjalankan semua test secara bersamaan.

## Sistem Scoring 4-Point

### Komponen Penilaian:
1. **Operator** (1 poin): Jenis operasi matematika
2. **Operan 1** (1 poin): Angka pertama dalam soal
3. **Operan 2** (1 poin): Angka kedua dalam soal
4. **Jawaban** (1 poin): Hasil perhitungan

### Kriteria Penilaian:
- **4 poin (Excellent)**: Semua komponen benar
- **3 poin (Good)**: 3 dari 4 komponen benar
- **2 poin (Fair)**: 2 dari 4 komponen benar
- **1 poin (Poor)**: 1 dari 4 komponen benar
- **0 poin (Incorrect)**: Semua komponen salah

## Cara Menjalankan Tests

### 1. Menjalankan Semua Tests
```bash
cd backend
python run_compare_tests.py
```

### 2. Menjalankan Kategori Tertentu
```bash
# Testing scoring system saja
python run_compare_tests.py scoring

# Testing integration saja
python run_compare_tests.py integration

# Testing semua kategori
python run_compare_tests.py all
```

### 3. Menjalankan File Test Tertentu
```bash
# Testing scoring
python -m unittest test_compare_scoring -v

# Testing integration
python -m unittest test_compare_integration -v
```

### 4. Menjalankan Test Method Tertentu
```bash
# Testing perfect score
python -m unittest test_compare_scoring.TestCompareScoring.test_perfect_score_4_points -v

# Testing standardization
python -m unittest test_compare_scoring.TestCompareScoring.test_standardize_operator -v
```

## Test Cases yang Dicakup

### 1. Standardization Tests
- Operator standardization (`+`, `-`, `*`, `/`, `x`, `:`, `÷`)
- Case sensitivity handling
- Number format standardization
- Answer format standardization

### 2. Scoring Tests
- Perfect score (4/4 points)
- Partial scores (3/4, 2/4, 1/4, 0/4 points)
- Different operator formats
- Different number formats
- Different answer formats

### 3. Integration Tests
- Addition problems
- Subtraction problems
- Multiplication problems
- Division problems
- Mixed operator problems
- Real-world word problems

### 4. Edge Case Tests
- Empty inputs
- None inputs
- Invalid number formats
- Single number operands
- Three or more numbers
- Missing data handling

### 5. Gemini Integration Tests
- Gemini analysis inclusion
- Sleep timing verification
- Error handling for Gemini failures

## Output dan Interpretasi

### Success Rate Categories:
- **100%**: Semua test berhasil - sistem berfungsi sempurna
- **90-99%**: Minor issues - perlu perbaikan kecil
- **70-89%**: Significant issues - perlu perbaikan menengah
- **<70%**: Critical issues - perlu perbaikan besar

### Test Output Format:
```
==========================================
COMPARE ANSWERS INTERNAL - UNIT TESTING SUITE
==========================================
Started at: 2024-01-15 10:30:00

✓ Test modules imported successfully
✓ Test suite created with 3 test classes

Running tests...
----------------------------------------
test_standardize_operator (test_compare_scoring.TestCompareScoring) ... ok
test_perfect_score_4_points (test_compare_scoring.TestCompareScoring) ... ok
...

==========================================
TEST EXECUTION SUMMARY
==========================================
Total tests run: 45
Successful: 45
Failures: 0
Errors: 0
Success rate: 100.0%
Duration: 2.34 seconds
Completed at: 2024-01-15 10:30:02

TEST CATEGORIES SUMMARY
----------------------------------------
Standardization Tests: 15 tests
Scoring Tests: 20 tests
Integration Tests: 8 tests
Edge Case Tests: 2 tests

RECOMMENDATIONS
----------------------------------------
🎉 All tests passed! The compare_answers_internal function is working correctly.
   - All standardization functions are working
   - Scoring system is accurate
   - Integration with Gemini is functional
   - Edge cases are handled properly
```

## Troubleshooting

### Common Issues:

#### 1. Import Errors
```
Error: No module named 'app'
```
**Solution**: Pastikan berada di direktori `backend` dan file `app.py` ada.

#### 2. Gemini API Errors
```
Error: GEMINI_API_KEY not found
```
**Solution**: Set environment variable atau mock Gemini functions untuk testing.

#### 3. Database Connection Errors
```
Error: Database connection failed
```
**Solution**: Tests tidak memerlukan database, pastikan tidak ada import yang memanggil database.

#### 4. Timeout Errors
```
Error: Tests taking too long
```
**Solution**: Gemini sleep sudah di-mock, jika masih lambat, cek ada loop atau blocking calls.

### Debug Mode:
Untuk debugging, tambahkan `-v` flag:
```bash
python -m unittest test_compare_scoring -v
```

## Menambahkan Test Cases Baru

### 1. Menambahkan Test Method Baru
```python
def test_new_scenario(self):
    """Test untuk skenario baru"""
    ai_answer = {
        "operator": "Penjumlahan",
        "angka_dalam_soal": "5,3",
        "jawaban": "8"
    }
    
    student_answer = {
        "operator": "Penjumlahan",
        "angka_dalam_soal": "5,3",
        "jawaban": "8"
    }
    
    result = compare_answers_internal(ai_answer, student_answer)
    
    self.assertEqual(result["nilai"], 4)
    self.assertEqual(result["status"], "excellent")
```

### 2. Menambahkan Test Class Baru
```python
class TestNewCategory(unittest.TestCase):
    """Test untuk kategori baru"""
    
    def setUp(self):
        # Setup untuk test class baru
        pass
    
    def test_new_functionality(self):
        # Test method baru
        pass
```

## Best Practices

### 1. Test Naming
- Gunakan nama yang deskriptif: `test_perfect_score_4_points`
- Gunakan subTest untuk multiple test cases
- Dokumentasikan setiap test dengan docstring

### 2. Test Organization
- Kelompokkan test berdasarkan fungsionalitas
- Gunakan setUp dan tearDown untuk common setup
- Mock external dependencies (Gemini, database)

### 3. Assertions
- Gunakan assertion yang spesifik
- Test multiple aspects dari result
- Validasi format dan content

### 4. Edge Cases
- Test dengan input kosong/null
- Test dengan format yang tidak standar
- Test dengan data yang tidak valid

## Continuous Integration

### GitHub Actions Example:
```yaml
name: Compare Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run compare tests
      run: python run_compare_tests.py
```

## Monitoring dan Maintenance

### 1. Regular Testing
- Jalankan tests setiap kali ada perubahan pada `compare_answers_internal`
- Monitor success rate secara berkala
- Update test cases ketika ada perubahan requirements

### 2. Performance Monitoring
- Monitor test execution time
- Optimize slow tests
- Remove redundant test cases

### 3. Coverage Analysis
- Pastikan semua code paths ter-cover
- Tambahkan test cases untuk uncovered areas
- Maintain minimum 90% code coverage

## Kesimpulan

Unit testing ini memastikan bahwa sistem scoring `compare_answers_internal` berfungsi dengan akurat dan dapat menangani berbagai skenario input. Dengan menjalankan tests secara regular, kita dapat memastikan kualitas dan reliability dari sistem penilaian matematika. 