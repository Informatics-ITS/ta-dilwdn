import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import compare_answers_internal, solve_text_internal

class DummySoal:
    def __init__(self, id, soal, json_result):
        self.id = id
        self.soal = soal
        self.json_result = json_result

class DummySiswa:
    def __init__(self, no, NISN, user_id):
        self.no = no
        self.NISN = NISN
        self.user_id = user_id

class DummySession(dict):
    pass

class TestExamSubmission(unittest.TestCase):
    def setUp(self):
        # Patch Gemini and sleep
        self.gemini_sleep_patcher = patch('app.time.sleep')
        self.mock_sleep = self.gemini_sleep_patcher.start()
        self.gemini_patcher = patch('app.analyze_math_problem_with_gemini')
        self.mock_gemini = self.gemini_patcher.start()
        self.mock_gemini.return_value = {
            "status": "success",
            "analysis": {
                "operator": "Penjumlahan",
                "angka_dalam_soal": "5,3",
                "jawaban": "8"
            },
            "penjelasan": "Analisis Gemini: 5 + 3 = 8"
        }

    def tearDown(self):
        self.gemini_sleep_patcher.stop()
        self.gemini_patcher.stop()

    def test_exam_submission_and_compare(self):
        # Simulasi data soal dan jawaban siswa
        soal_list = [
            DummySoal(1, "Ana punya 5 apel, diberi 3 lagi. Berapa apel Ana?", {
                "operator": "Penjumlahan",
                "angka_dalam_soal": "5,3",
                "jawaban": "8"
            }),
            DummySoal(2, "Budi punya 10 permen, diberikan 4. Berapa permen Budi?", {
                "operator": "Penjumlahan",
                "angka_dalam_soal": "10,4",
                "jawaban": "14"
            })
        ]
        siswa = DummySiswa(no=1, NISN="12345", user_id=10)
        # Jawaban siswa (benar dan salah)
        answers = [
            {"soal_id": 1, "jawaban_text": "5 + 3 = 8"},  # Benar
            {"soal_id": 2, "jawaban_text": "10 + 4 = 15"}  # Salah
        ]
        # Simulasi proses submit ujian
        total_points = 0
        max_points = 0
        results = []
        for idx, answer_data in enumerate(answers):
            soal = soal_list[idx]
            max_points += 4
            student_answer_extracted = solve_text_internal(answer_data['jawaban_text'])
            comparison_result = compare_answers_internal(soal.json_result, student_answer_extracted)
            total_points += comparison_result['nilai']
            results.append({
                'soal_id': soal.id,
                'soal_text': soal.soal,
                'ai_answer': soal.json_result,
                'student_answer_extracted': student_answer_extracted,
                'comparison_result': comparison_result
            })
        score = int(round((total_points / max_points) * 100)) if max_points > 0 else 0
        label = 'Baik' if score >= 80 else 'Cukup' if score >= 60 else 'Kurang'
        # Assert hasil
        self.assertEqual(score, 50)  # 1 benar (4), 1 salah (0), total 4/8 -> 50%
        self.assertEqual(label, 'Kurang')
        self.assertEqual(results[0]['comparison_result']['nilai'], 4)
        self.assertEqual(results[1]['comparison_result']['nilai'], 0)
        self.assertIn('deskripsi_analisis', results[0]['comparison_result'])
        self.assertIn('gemini_used', results[0]['comparison_result'])
        self.assertTrue(results[0]['comparison_result']['gemini_used'])
        # Cek format response
        for res in results:
            self.assertIn('soal_id', res)
            self.assertIn('ai_answer', res)
            self.assertIn('student_answer_extracted', res)
            self.assertIn('comparison_result', res)
            self.assertIsInstance(res['comparison_result']['nilai'], int)
            self.assertIsInstance(res['comparison_result']['deskripsi_analisis'], str)
        # --- Gemini Analysis Assertions ---
        # Pastikan hasil Gemini muncul di deskripsi_analisis dan field Gemini
        gemini_result = results[0]['comparison_result']
        self.assertIn('[Gemini]', gemini_result['deskripsi_analisis'])
        self.assertIn('Operator:', gemini_result['deskripsi_analisis'])
        self.assertIn('Angka:', gemini_result['deskripsi_analisis'])
        self.assertIn('Jawaban:', gemini_result['deskripsi_analisis'])
        self.assertIn('Penjelasan:', gemini_result['deskripsi_analisis'])
        # Cek isi Gemini
        self.assertEqual(gemini_result['gemini_operator'], 'Penjumlahan')
        self.assertEqual(gemini_result['gemini_angka'], '5,3')
        self.assertEqual(gemini_result['gemini_jawaban'], '8')
        self.assertIn('Gemini', gemini_result['gemini_penjelasan'])

    def test_various_math_problems(self):
        # Daftar soal dan jawaban
        soal_list = [
            DummySoal(1, "Andi memiliki 15 jeruk. Dia memberikan 7 kepada temannya. Berapa yang tersisa?", {
                "operator": "Pengurangan",
                "angka_dalam_soal": "15,7",
                "jawaban": "8"
            }),
            DummySoal(2, "Di perpustakaan ada 85 buku. Siswa meminjam 25 buku. Berapa buku yang masih ada?", {
                "operator": "Pengurangan",
                "angka_dalam_soal": "85,25",
                "jawaban": "60"
            }),
            DummySoal(3, "Setiap kotak berisi 6 pensil. Ada 4 kotak. Berapa total pensil?", {
                "operator": "Perkalian",
                "angka_dalam_soal": "6,4",
                "jawaban": "24"
            }),
            DummySoal(4, "Bu guru membagi 48 permen kepada 6 anak sama rata. Berapa permen per anak?", {
                "operator": "Pembagian",
                "angka_dalam_soal": "48,6",
                "jawaban": "8"
            })
        ]
        # Jawaban siswa benar
        jawaban_benar = [
            "15-7=8",
            "85-25=60",
            "6x4=24",
            "48:6=8"
        ]
        # Jawaban siswa salah
        jawaban_salah = [
            "15-7=7",
            "85-25=50",
            "6x4=20",
            "48:6=7"
        ]
        # Test jawaban benar (gunakan hasil Gemini sebagai kunci)
        for idx, soal in enumerate(soal_list):
            student_answer_extracted = solve_text_internal(jawaban_benar[idx])
            comparison_result = compare_answers_internal(soal.json_result, student_answer_extracted)
            # Gunakan hasil Gemini sebagai kunci pembanding
            kunci_operator = comparison_result.get('gemini_operator')
            kunci_angka = comparison_result.get('gemini_angka')
            kunci_jawaban = comparison_result.get('gemini_jawaban')
            self.assertEqual(student_answer_extracted['operator'], kunci_operator, f"Soal {idx+1} operator harus sama dengan Gemini")
            self.assertEqual(student_answer_extracted['angka_dalam_soal'], kunci_angka, f"Soal {idx+1} angka harus sama dengan Gemini")
            self.assertEqual(str(student_answer_extracted['jawaban']), str(kunci_jawaban), f"Soal {idx+1} jawaban harus sama dengan Gemini")
            self.assertEqual(comparison_result['nilai'], 4, f"Soal {idx+1} jawaban benar harus 4 poin")
            self.assertIn('[Gemini]', comparison_result['deskripsi_analisis'])
            self.assertTrue(comparison_result['gemini_used'])
        # Test jawaban salah (gunakan hasil Gemini sebagai kunci)
        for idx, soal in enumerate(soal_list):
            student_answer_extracted = solve_text_internal(jawaban_salah[idx])
            comparison_result = compare_answers_internal(soal.json_result, student_answer_extracted)
            kunci_operator = comparison_result.get('gemini_operator')
            kunci_angka = comparison_result.get('gemini_angka')
            kunci_jawaban = comparison_result.get('gemini_jawaban')
            # Jawaban siswa salah, minimal satu aspek berbeda
            salah = (
                student_answer_extracted['operator'] != kunci_operator or
                student_answer_extracted['angka_dalam_soal'] != kunci_angka or
                str(student_answer_extracted['jawaban']) != str(kunci_jawaban)
            )
            self.assertTrue(salah, f"Soal {idx+1} jawaban salah harus beda dengan Gemini")
            self.assertEqual(comparison_result['nilai'], 0, f"Soal {idx+1} jawaban salah harus 0 poin")
            self.assertIn('[Gemini]', comparison_result['deskripsi_analisis'])
            self.assertTrue(comparison_result['gemini_used'])

if __name__ == '__main__':
    unittest.main(verbosity=2) 