#!/usr/bin/env python3
"""
Demo script untuk menguji ekstraksi NLP pada soal cerita matematika
Menampilkan kemampuan AI dalam menganalisis soal cerita tanpa jawaban eksplisit
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import extract_math_simple, solve_text_internal, compare_answers_internal


def demo_story_problems():
    """Demo soal cerita tanpa jawaban"""
    print("="*80)
    print("DEMO: Ekstraksi NLP untuk Soal Cerita Matematika")
    print("="*80)
    
    story_problems = [
        # Pengurangan
        {
            'soal': 'Andi memiliki 15 buah jeruk. Dia memberikan 7 jeruk kepada temannya. Berapa jeruk yang tersisa?',
            'expected_operation': 'Pengurangan',
            'expected_answer': 8,
            'category': 'Pengurangan'
        },
        {
            'soal': 'Di perpustakaan ada 25 buku. Siswa meminjam 9 buku. Berapa buku yang masih ada di perpustakaan?',
            'expected_operation': 'Pengurangan',
            'expected_answer': 16,
            'category': 'Pengurangan'
        },
        
        # Perkalian
        {
            'soal': 'Setiap kotak berisi 6 pensil. Jika ada 4 kotak, berapa total pensil?',
            'expected_operation': 'Perkalian',
            'expected_answer': 24,
            'category': 'Perkalian'
        },
        {
            'soal': 'Ibu membeli 3 pak telur. Setiap pak berisi 12 telur. Berapa total telur yang dibeli ibu?',
            'expected_operation': 'Perkalian',
            'expected_answer': 36,
            'category': 'Perkalian'
        },
        {
            'soal': 'Seorang petani menanam 8 baris jagung. Setiap baris ada 15 tanaman. Berapa total tanaman jagung?',
            'expected_operation': 'Perkalian',
            'expected_answer': 120,
            'category': 'Perkalian'
        },
        
        # Pembagian
        {
            'soal': 'Bu guru akan membagi 24 permen kepada 6 anak secara merata. Berapa permen yang diterima setiap anak?',
            'expected_operation': 'Pembagian',
            'expected_answer': 4,
            'category': 'Pembagian'
        },
        {
            'soal': 'Pak Ali memiliki 45 apel. Dia ingin memasukkannya ke dalam keranjang yang masing-masing berisi 9 apel. Berapa keranjang yang dibutuhkan?',
            'expected_operation': 'Pembagian',
            'expected_answer': 5,
            'category': 'Pembagian'
        },
        {
            'soal': 'Di sekolah ada 56 siswa yang akan dibagi menjadi 7 kelompok sama banyak. Berapa siswa di setiap kelompok?',
            'expected_operation': 'Pembagian',
            'expected_answer': 8,
            'category': 'Pembagian'
        }
    ]
    
    successful_extractions = 0
    total_problems = len(story_problems)
    
    for i, problem in enumerate(story_problems, 1):
        print(f"\n{'-'*60}")
        print(f"Soal {i} ({problem['category']}):")
        print(f"'{problem['soal']}'")
        print(f"{'-'*60}")
        
        try:
            # Extract using the NLP function
            result = solve_text_internal(problem['soal'])
            
            print(f"✅ HASIL EKSTRAKSI:")
            print(f"   Operator terdeteksi: {result['operator']}")
            print(f"   Angka yang diekstrak: {result['angka_dalam_soal']}")
            print(f"   Jawaban AI: {result['jawaban']}")
            
            # Check if extraction is correct
            is_operator_correct = result['operator'] == problem['expected_operation']
            
            # Check answer
            try:
                ai_answer = int(result['jawaban']) if isinstance(result['jawaban'], str) and result['jawaban'].isdigit() else result['jawaban']
                is_answer_correct = ai_answer == problem['expected_answer']
            except:
                is_answer_correct = False
                ai_answer = result['jawaban']
            
            print(f"\n📊 EVALUASI:")
            print(f"   Operator {'✅ BENAR' if is_operator_correct else '❌ SALAH'} (Expected: {problem['expected_operation']})")
            print(f"   Jawaban {'✅ BENAR' if is_answer_correct else '❌ SALAH'} (Expected: {problem['expected_answer']}, Got: {ai_answer})")
            
            if is_operator_correct and is_answer_correct:
                successful_extractions += 1
                print(f"   🎉 BERHASIL TOTAL!")
            else:
                print(f"   ⚠️  Perlu perbaikan")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"RINGKASAN HASIL")
    print(f"{'='*80}")
    print(f"Total soal: {total_problems}")
    print(f"Berhasil ekstrak dengan benar: {successful_extractions}")
    print(f"Tingkat keberhasilan: {(successful_extractions/total_problems)*100:.1f}%")
    
    if successful_extractions == total_problems:
        print(f"🎉 SEMPURNA! Semua soal berhasil diekstrak dengan benar!")
    elif successful_extractions >= total_problems * 0.8:
        print(f"👍 BAGUS! Kebanyakan soal berhasil diekstrak dengan benar.")
    else:
        print(f"⚠️  PERLU PERBAIKAN! Masih banyak soal yang gagal diekstrak.")


def demo_comparison_system():
    """Demo sistem perbandingan 4 poin dengan analisis tingkat kesulitan"""
    print(f"\n{'='*80}")
    print("DEMO: Sistem Perbandingan 4 Poin + Analisis Tingkat Kesulitan")
    print("="*80)
    
    # Soal cerita contoh
    soal_text = "Setiap kotak berisi 6 pensil. Jika ada 4 kotak, berapa total pensil?"
    print(f"Soal: '{soal_text}'")
    
    # AI answer (kunci jawaban)
    ai_answer = solve_text_internal(soal_text)
    print(f"\nKunci Jawaban AI:")
    print(f"  Operator: {ai_answer['operator']}")
    print(f"  Angka: {ai_answer['angka_dalam_soal']}")
    print(f"  Jawaban: {ai_answer['jawaban']}")
    
    # Simulasi berbagai jawaban siswa
    student_scenarios = [
        {
            'name': 'Siswa A (Sempurna)',
            'answer': {
                'operator': 'Perkalian',
                'angka_dalam_soal': '6,4',
                'jawaban': '24'
            },
            'expected_score': 4
        },
        {
            'name': 'Siswa B (Salah jawaban)',
            'answer': {
                'operator': 'Perkalian',
                'angka_dalam_soal': '6,4',
                'jawaban': '20'
            },
            'expected_score': 3
        },
        {
            'name': 'Siswa C (Salah operator)',
            'answer': {
                'operator': 'Penjumlahan',
                'angka_dalam_soal': '6,4',
                'jawaban': '10'
            },
            'expected_score': 2
        },
        {
            'name': 'Siswa D (Hanya 1 angka benar)',
            'answer': {
                'operator': 'Penjumlahan',
                'angka_dalam_soal': '6,5',
                'jawaban': '11'
            },
            'expected_score': 1
        },
        {
            'name': 'Siswa E (Semua salah)',
            'answer': {
                'operator': 'Pengurangan',
                'angka_dalam_soal': '8,3',
                'jawaban': '5'
            },
            'expected_score': 0
        }
    ]
    
    print(f"\n{'-'*60}")
    print("ANALISIS JAWABAN SISWA:")
    print(f"{'-'*60}")
    
    for scenario in student_scenarios:
        print(f"\n👤 {scenario['name']}:")
        print(f"   Jawaban: {scenario['answer']}")
        
        # Compare answers
        comparison = compare_answers_internal(ai_answer, scenario['answer'])
        
        print(f"   📊 Hasil Analisis:")
        print(f"     Skor: {comparison['nilai']}/4 poin ({comparison['persentase']}%)")
        print(f"     Status: {comparison['status']}")
        print(f"     Parameter benar: {comparison['parameter_benar']}")
        print(f"     Parameter salah: {comparison['parameter_salah']}")
        print(f"     Koreksi: {'; '.join(comparison['koreksi'])}")
        
        # Show difficulty analysis (NEW!)
        if 'difficulty_analysis' in comparison:
            difficulty = comparison['difficulty_analysis']
            print(f"   🎯 Tingkat Kesulitan:")
            print(f"     Level: {difficulty['level']}")
            print(f"     Kategori: {difficulty['category']}")
            print(f"     Deskripsi: {difficulty['description']}")
            print(f"     Complexity Score: {difficulty['complexity_score']}/4")
        
        # Check if score matches expectation
        if comparison['nilai'] == scenario['expected_score']:
            print(f"     ✅ Skor sesuai ekspektasi ({scenario['expected_score']} poin)")
        else:
            print(f"     ⚠️  Skor tidak sesuai (Expected: {scenario['expected_score']}, Got: {comparison['nilai']})")


def demo_difficulty_levels():
    """Demo berbagai tingkat kesulitan berdasarkan range bilangan cacah"""
    print(f"\n{'='*80}")
    print("DEMO: Analisis Tingkat Kesulitan Bilangan Cacah")
    print("="*80)
    
    difficulty_examples = [
        # Penjumlahan/Pengurangan
        {
            'category': 'Penjumlahan - Dasar (≤20)',
            'soal': 'Andi punya 15 kelereng, temannya beri 5 lagi. Berapa total?',
            'ai_answer': {'operator': 'Penjumlahan', 'angka_dalam_soal': '15,5', 'jawaban': '20'},
            'expected_level': 'dasar'
        },
        {
            'category': 'Pengurangan - Menengah (≤100)', 
            'soal': 'Di toko ada 85 roti, terjual 25. Berapa yang tersisa?',
            'ai_answer': {'operator': 'Pengurangan', 'angka_dalam_soal': '85,25', 'jawaban': '60'},
            'expected_level': 'menengah'
        },
        {
            'category': 'Penjumlahan - Lanjut (≤1000)',
            'soal': 'Sekolah punya 450 buku, dapat sumbangan 350 lagi. Berapa total?',
            'ai_answer': {'operator': 'Penjumlahan', 'angka_dalam_soal': '450,350', 'jawaban': '800'},
            'expected_level': 'lanjut'
        },
        
        # Perkalian/Pembagian
        {
            'category': 'Perkalian - Dasar (≤100)',
            'soal': 'Ada 8 kotak, setiap kotak isi 12 pensil. Berapa total?',
            'ai_answer': {'operator': 'Perkalian', 'angka_dalam_soal': '8,12', 'jawaban': '96'},
            'expected_level': 'dasar'
        },
        {
            'category': 'Pembagian - Lanjut (>100)',
            'soal': '450 apel dibagi ke 150 anak sama rata. Berapa per anak?',
            'ai_answer': {'operator': 'Pembagian', 'angka_dalam_soal': '450,150', 'jawaban': '3'},
            'expected_level': 'lanjut'
        }
    ]
    
    for i, example in enumerate(difficulty_examples, 1):
        print(f"\n{'-'*60}")
        print(f"Contoh {i}: {example['category']}")
        print(f"Soal: '{example['soal']}'")
        print(f"{'-'*60}")
        
        # Simulate perfect student answer to focus on difficulty analysis
        student_answer = example['ai_answer'].copy()
        
        # Compare to get difficulty analysis
        comparison = compare_answers_internal(example['ai_answer'], student_answer)
        
        if 'difficulty_analysis' in comparison:
            difficulty = comparison['difficulty_analysis']
            print(f"🎯 Analisis Tingkat Kesulitan:")
            print(f"   Level: {difficulty['level']}")
            print(f"   Kategori: {difficulty['category']}")
            print(f"   Deskripsi: {difficulty['description']}")
            print(f"   Angka terbesar: {difficulty['max_number']}")
            print(f"   Complexity Score: {difficulty['complexity_score']}/4")
            
            # Check if level matches expectation
            if difficulty['level'] == example['expected_level']:
                print(f"   ✅ Level sesuai ekspektasi ({example['expected_level']})")
            else:
                print(f"   ⚠️  Level tidak sesuai (Expected: {example['expected_level']}, Got: {difficulty['level']})")
        
        print(f"   📝 Deskripsi lengkap: {comparison['deskripsi_analisis']}")


def demo_interactive():
    """Demo interaktif untuk menguji input custom"""
    print(f"\n{'='*80}")
    print("DEMO INTERAKTIF: Uji Soal Cerita Anda Sendiri")
    print("="*80)
    print("Masukkan soal cerita matematika, atau ketik 'exit' untuk keluar.")
    
    while True:
        print(f"\n{'-'*40}")
        user_input = input("Masukkan soal cerita: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'keluar']:
            print("Terima kasih!")
            break
            
        if not user_input:
            continue
            
        try:
            result = solve_text_internal(user_input)
            
            print(f"\n📝 Input: '{user_input}'")
            print(f"🤖 Analisis AI:")
            print(f"   Operator: {result['operator']}")
            print(f"   Angka: {result['angka_dalam_soal']}")
            print(f"   Jawaban: {result['jawaban']}")
            
            # Ask for verification
            verify = input("\nApakah hasil ini benar? (y/n): ").strip().lower()
            if verify in ['y', 'yes', 'ya']:
                print("✅ Bagus! AI berhasil menganalisis dengan benar.")
            else:
                print("❌ AI perlu diperbaiki untuk kasus ini.")
                correct_answer = input("Jawaban yang benar: ").strip()
                if correct_answer:
                    print(f"📝 Catatan: AI menjawab '{result['jawaban']}', yang benar '{correct_answer}'")
                    
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def main():
    """Main function"""
    print("Selamat datang di Demo Ekstraksi NLP untuk Soal Cerita Matematika!")
    print("Demo ini menunjukkan kemampuan AI dalam:")
    print("1. Mengekstrak komponen matematika dari soal cerita")
    print("2. Menghitung jawaban secara otomatis") 
    print("3. Sistem penilaian 4 poin yang detail")
    print("4. Analisis tingkat kesulitan berdasarkan bilangan cacah")
    
    # Run demos
    demo_story_problems()
    demo_comparison_system()
    demo_difficulty_levels()  # NEW!
    
    # Interactive demo
    print(f"\n{'='*80}")
    interactive = input("Ingin mencoba demo interaktif? (y/n): ").strip().lower()
    if interactive in ['y', 'yes', 'ya']:
        demo_interactive()
    
    print(f"\n{'='*80}")
    print("Demo selesai! Semoga bermanfaat.")
    print("="*80)


if __name__ == '__main__':
    main() 