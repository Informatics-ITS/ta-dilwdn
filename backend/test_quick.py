#!/usr/bin/env python3
"""
Quick test untuk soal cerita NLP extraction
Test singkat untuk memverifikasi functionality baru
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import solve_text_internal


def test_story_cases():
    """Test cases soal cerita tanpa jawaban"""
    
    test_cases = [
        # Pengurangan - Level Dasar (≤20)
        {
            'soal': 'Andi memiliki 15 jeruk. Dia memberikan 7 kepada temannya. Berapa yang tersisa?',
            'expected_op': 'Pengurangan',
            'expected_answer': 8,
            'expected_difficulty': 'dasar'
        },
        
        # Pengurangan - Level Menengah (≤100)
        {
            'soal': 'Di perpustakaan ada 85 buku. Siswa meminjam 25 buku. Berapa buku yang masih ada?',
            'expected_op': 'Pengurangan', 
            'expected_answer': 60,
            'expected_difficulty': 'menengah'
        },
        
        # Perkalian - Level Dasar (≤100)
        {
            'soal': 'Setiap kotak berisi 6 pensil. Ada 4 kotak. Berapa total pensil?',
            'expected_op': 'Perkalian',
            'expected_answer': 24,
            'expected_difficulty': 'dasar'
        },
        
        # Perkalian - Level Dasar (≤100)
        {
            'soal': 'Ibu membeli 3 pak telur. Setiap pak berisi 12 telur. Berapa total telur?',
            'expected_op': 'Perkalian',
            'expected_answer': 36,
            'expected_difficulty': 'dasar'
        },
        
        # Pembagian - Level Dasar (≤100)
        {
            'soal': 'Bu guru membagi 48 permen kepada 6 anak sama rata. Berapa permen per anak?',
            'expected_op': 'Pembagian',
            'expected_answer': 8,
            'expected_difficulty': 'dasar'
        },
        
        # Pembagian - Level Lanjut (>100)
        {
            'soal': 'Ada 450 apel akan dimasukkan ke keranjang. Setiap keranjang berisi 150 apel. Berapa keranjang dibutuhkan?',
            'expected_op': 'Pembagian',
            'expected_answer': 3,
            'expected_difficulty': 'lanjut'
        }
    ]
    
    print("="*70)
    print("QUICK TEST: Soal Cerita NLP Extraction")
    print("="*70)
    
    passed = 0
    total = len(test_cases)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['soal'][:50]}...")
        
        try:
            result = solve_text_internal(test['soal'])
            
            # Check operator
            op_correct = result['operator'] == test['expected_op']
            
            # Check answer
            try:
                answer = int(result['jawaban']) if isinstance(result['jawaban'], str) else result['jawaban']
                answer_correct = answer == test['expected_answer']
            except:
                answer_correct = False
                answer = result['jawaban']
            
            print(f"  Operator: {result['operator']} ({'✅' if op_correct else '❌'})")
            print(f"  Jawaban: {answer} ({'✅' if answer_correct else '❌'})")
            
            # Test difficulty analysis (NEW!)
            if op_correct and answer_correct:
                from app import get_difficulty_level
                numbers = result['angka_dalam_soal'].split(',')
                difficulty = get_difficulty_level(result['operator'], numbers)
                
                difficulty_correct = difficulty['level'] == test['expected_difficulty']
                print(f"  Tingkat Kesulitan: {difficulty['level']} ({'✅' if difficulty_correct else '❌'})")
                print(f"  Deskripsi: {difficulty['description']}")
                
                if difficulty_correct:
                    print(f"  🎉 PASS (dengan analisis tingkat kesulitan)")
                    passed += 1
                else:
                    print(f"  ⚠️  PARTIAL (Expected difficulty: {test['expected_difficulty']}, Got: {difficulty['level']})")
                    passed += 0.5  # Partial credit for getting operator and answer right
            else:
                print(f"  ❌ FAIL (Expected: {test['expected_op']}, {test['expected_answer']})")
                
        except Exception as e:
            print(f"  💥 ERROR: {e}")
    
    print(f"\n{'='*70}")
    print(f"HASIL: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 SEMUA TEST BERHASIL!")
        return True
    else:
        print("⚠️  Ada test yang gagal, perlu perbaikan")
        return False


if __name__ == '__main__':
    success = test_story_cases()
    sys.exit(0 if success else 1) 