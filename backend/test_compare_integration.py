import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the functions to test
from app import (
    compare_answers_internal, 
    solve_text_internal,
    extract_math_simple
)

class TestCompareIntegration(unittest.TestCase):
    """Integration tests for compare_answers_internal with real-world scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock Gemini sleep to avoid delays in testing
        self.gemini_sleep_patcher = patch('app.time.sleep')
        self.mock_sleep = self.gemini_sleep_patcher.start()
        
        # Mock Gemini analysis to return consistent results
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
        """Clean up after tests"""
        self.gemini_sleep_patcher.stop()
        self.gemini_patcher.stop()
    
    def test_addition_problem_comparison(self):
        """Test comparison for addition problems"""
        test_cases = [
            {
                "soal": "Ana mempunyai 5 apel, kemudian diberi 3 apel lagi. Berapa apel Ana sekarang?",
                "ai_answer": {
                    "operator": "Penjumlahan",
                    "angka_dalam_soal": "5,3",
                    "jawaban": "8"
                },
                "student_answers": [
                    {
                        "operator": "Penjumlahan",
                        "angka_dalam_soal": "5,3",
                        "jawaban": "8",
                        "expected_score": 4
                    },
                    {
                        "operator": "Penjumlahan",
                        "angka_dalam_soal": "5,3",
                        "jawaban": "9",
                        "expected_score": 3
                    },
                    {
                        "operator": "Pengurangan",
                        "angka_dalam_soal": "5,3",
                        "jawaban": "2",
                        "expected_score": 0
                    }
                ]
            }
        ]
        
        for test_case in test_cases:
            ai_answer = test_case["ai_answer"]
            
            for student_case in test_case["student_answers"]:
                with self.subTest(soal=test_case["soal"], student_answer=student_case):
                    student_answer = {
                        "operator": student_case["operator"],
                        "angka_dalam_soal": student_case["angka_dalam_soal"],
                        "jawaban": student_case["jawaban"]
                    }
                    
                    result = compare_answers_internal(ai_answer, student_answer)
                    
                    self.assertEqual(result["nilai"], student_case["expected_score"])
                    self.assertIn("deskripsi_analisis", result)
                    self.assertIn("difficulty_analysis", result)
    
    def test_subtraction_problem_comparison(self):
        """Test comparison for subtraction problems"""
        test_cases = [
            {
                "soal": "Budi mempunyai 10 permen, kemudian memberikan 3 permen kepada temannya. Berapa permen Budi sekarang?",
                "ai_answer": {
                    "operator": "Pengurangan",
                    "angka_dalam_soal": "10,3",
                    "jawaban": "7"
                },
                "student_answers": [
                    {
                        "operator": "Pengurangan",
                        "angka_dalam_soal": "10,3",
                        "jawaban": "7",
                        "expected_score": 4
                    },
                    {
                        "operator": "Penjumlahan",
                        "angka_dalam_soal": "10,3",
                        "jawaban": "13",
                        "expected_score": 0
                    }
                ]
            }
        ]
        
        for test_case in test_cases:
            ai_answer = test_case["ai_answer"]
            
            for student_case in test_case["student_answers"]:
                with self.subTest(soal=test_case["soal"], student_answer=student_case):
                    student_answer = {
                        "operator": student_case["operator"],
                        "angka_dalam_soal": student_case["angka_dalam_soal"],
                        "jawaban": student_case["jawaban"]
                    }
                    
                    result = compare_answers_internal(ai_answer, student_answer)
                    
                    self.assertEqual(result["nilai"], student_case["expected_score"])
    
    def test_multiplication_problem_comparison(self):
        """Test comparison for multiplication problems"""
        test_cases = [
            {
                "soal": "Setiap kotak berisi 4 buku. Jika ada 3 kotak, berapa total buku?",
                "ai_answer": {
                    "operator": "Perkalian",
                    "angka_dalam_soal": "4,3",
                    "jawaban": "12"
                },
                "student_answers": [
                    {
                        "operator": "Perkalian",
                        "angka_dalam_soal": "4,3",
                        "jawaban": "12",
                        "expected_score": 4
                    },
                    {
                        "operator": "Penjumlahan",
                        "angka_dalam_soal": "4,3",
                        "jawaban": "7",
                        "expected_score": 0
                    }
                ]
            }
        ]
        
        for test_case in test_cases:
            ai_answer = test_case["ai_answer"]
            
            for student_case in test_case["student_answers"]:
                with self.subTest(soal=test_case["soal"], student_answer=student_case):
                    student_answer = {
                        "operator": student_case["operator"],
                        "angka_dalam_soal": student_case["angka_dalam_soal"],
                        "jawaban": student_case["jawaban"]
                    }
                    
                    result = compare_answers_internal(ai_answer, student_answer)
                    
                    self.assertEqual(result["nilai"], student_case["expected_score"])
    
    def test_division_problem_comparison(self):
        """Test comparison for division problems"""
        test_cases = [
            {
                "soal": "Ada 12 apel yang akan dibagikan kepada 3 anak sama rata. Berapa apel setiap anak?",
                "ai_answer": {
                    "operator": "Pembagian",
                    "angka_dalam_soal": "12,3",
                    "jawaban": "4"
                },
                "student_answers": [
                    {
                        "operator": "Pembagian",
                        "angka_dalam_soal": "12,3",
                        "jawaban": "4",
                        "expected_score": 4
                    },
                    {
                        "operator": "Perkalian",
                        "angka_dalam_soal": "12,3",
                        "jawaban": "36",
                        "expected_score": 0
                    }
                ]
            }
        ]
        
        for test_case in test_cases:
            ai_answer = test_case["ai_answer"]
            
            for student_case in test_case["student_answers"]:
                with self.subTest(soal=test_case["soal"], student_answer=student_case):
                    student_answer = {
                        "operator": student_case["operator"],
                        "angka_dalam_soal": student_case["angka_dalam_soal"],
                        "jawaban": student_case["jawaban"]
                    }
                    
                    result = compare_answers_internal(ai_answer, student_answer)
                    
                    self.assertEqual(result["nilai"], student_case["expected_score"])
    
    def test_mixed_operator_problem_comparison(self):
        """Test comparison for mixed operator problems"""
        test_cases = [
            {
                "soal": "Ana membeli 3 kotak permen, setiap kotak berisi 5 permen, kemudian membagikan 10 permen. Berapa permen yang tersisa?",
                "ai_answer": {
                    "operator": "Mix",
                    "angka_dalam_soal": "3,5,10",
                    "jawaban": "5"
                },
                "student_answers": [
                    {
                        "operator": "Mix",
                        "angka_dalam_soal": "3,5,10",
                        "jawaban": "5",
                        "expected_score": 4
                    },
                    {
                        "operator": "Penjumlahan",
                        "angka_dalam_soal": "3,5",
                        "jawaban": "8",
                        "expected_score": 0
                    }
                ]
            }
        ]
        
        for test_case in test_cases:
            ai_answer = test_case["ai_answer"]
            
            for student_case in test_case["student_answers"]:
                with self.subTest(soal=test_case["soal"], student_answer=student_case):
                    student_answer = {
                        "operator": student_case["operator"],
                        "angka_dalam_soal": student_case["angka_dalam_soal"],
                        "jawaban": student_case["jawaban"]
                    }
                    
                    result = compare_answers_internal(ai_answer, student_answer)
                    
                    self.assertEqual(result["nilai"], student_case["expected_score"])
    
    def test_different_operator_symbols(self):
        """Test comparison with different operator symbols"""
        test_cases = [
            # (ai_operator, student_operator, expected_score)
            ("Penjumlahan", "+", 4),
            ("Penjumlahan", "penjumlahan", 4),
            ("Pengurangan", "-", 4),
            ("Pengurangan", "pengurangan", 4),
            ("Perkalian", "x", 4),
            ("Perkalian", "*", 4),
            ("Perkalian", "perkalian", 4),
            ("Pembagian", "/", 4),
            ("Pembagian", ":", 4),
            ("Pembagian", "÷", 4),
            ("Pembagian", "pembagian", 4),
        ]
        
        for ai_op, student_op, expected_score in test_cases:
            with self.subTest(ai_op=ai_op, student_op=student_op):
                ai_answer = {
                    "operator": ai_op,
                    "angka_dalam_soal": "5,3",
                    "jawaban": "8"
                }
                
                student_answer = {
                    "operator": student_op,
                    "angka_dalam_soal": "5,3",
                    "jawaban": "8"
                }
                
                result = compare_answers_internal(ai_answer, student_answer)
                self.assertEqual(result["nilai"], expected_score)
    
    def test_different_number_formats(self):
        """Test comparison with different number formats"""
        test_cases = [
            # (ai_numbers, student_numbers, expected_score)
            ("5,3", "5,3", 4),
            ("5,3", " 5 , 3 ", 4),
            ("5,3", ["5", "3"], 4),
            ("10,20", "10,20", 4),
            ("5", "5", 4),
            ("5,3,10", "5,3,10", 4),
        ]
        
        for ai_nums, student_nums, expected_score in test_cases:
            with self.subTest(ai_nums=ai_nums, student_nums=student_nums):
                ai_answer = {
                    "operator": "Penjumlahan",
                    "angka_dalam_soal": ai_nums,
                    "jawaban": "8"
                }
                
                student_answer = {
                    "operator": "Penjumlahan",
                    "angka_dalam_soal": student_nums,
                    "jawaban": "8"
                }
                
                result = compare_answers_internal(ai_answer, student_answer)
                self.assertEqual(result["nilai"], expected_score)
    
    def test_different_answer_formats(self):
        """Test comparison with different answer formats"""
        test_cases = [
            # (ai_answer, student_answer, expected_score)
            ("8", "8", 4),
            (8, "8", 4),
            (8.0, "8", 4),
            ("8", 8, 4),
            ("8", 8.0, 4),
        ]
        
        for ai_ans, student_ans, expected_score in test_cases:
            with self.subTest(ai_ans=ai_ans, student_ans=student_ans):
                ai_answer = {
                    "operator": "Penjumlahan",
                    "angka_dalam_soal": "5,3",
                    "jawaban": ai_ans
                }
                
                student_answer = {
                    "operator": "Penjumlahan",
                    "angka_dalam_soal": "5,3",
                    "jawaban": student_ans
                }
                
                result = compare_answers_internal(ai_answer, student_answer)
                self.assertEqual(result["nilai"], expected_score)
    
    def test_partial_correctness_scenarios(self):
        """Test various partial correctness scenarios"""
        test_cases = [
            {
                "name": "Only operator correct",
                "ai_answer": {
                    "operator": "Penjumlahan",
                    "angka_dalam_soal": "5,3",
                    "jawaban": "8"
                },
                "student_answer": {
                    "operator": "Penjumlahan",
                    "angka_dalam_soal": "6,4",
                    "jawaban": "9"
                },
                "expected_score": 1,
                "expected_correct": ["operator"],
                "expected_wrong": ["operan_1", "operan_2", "jawaban"]
            },
            {
                "name": "Operator and operan_1 correct",
                "ai_answer": {
                    "operator": "Penjumlahan",
                    "angka_dalam_soal": "5,3",
                    "jawaban": "8"
                },
                "student_answer": {
                    "operator": "Penjumlahan",
                    "angka_dalam_soal": "5,4",
                    "jawaban": "9"
                },
                "expected_score": 2,
                "expected_correct": ["operator", "operan_1"],
                "expected_wrong": ["operan_2", "jawaban"]
            },
            {
                "name": "All except jawaban correct",
                "ai_answer": {
                    "operator": "Penjumlahan",
                    "angka_dalam_soal": "5,3",
                    "jawaban": "8"
                },
                "student_answer": {
                    "operator": "Penjumlahan",
                    "angka_dalam_soal": "5,3",
                    "jawaban": "9"
                },
                "expected_score": 3,
                "expected_correct": ["operator", "operan_1", "operan_2"],
                "expected_wrong": ["jawaban"]
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(name=test_case["name"]):
                result = compare_answers_internal(
                    test_case["ai_answer"], 
                    test_case["student_answer"]
                )
                
                self.assertEqual(result["nilai"], test_case["expected_score"])
                
                # Check correct parameters
                for param in test_case["expected_correct"]:
                    self.assertIn(param, result["parameter_benar"])
                
                # Check wrong parameters
                for param in test_case["expected_wrong"]:
                    self.assertIn(param, result["parameter_salah"])
    
    def test_deskripsi_analisis_content(self):
        """Test that deskripsi_analisis contains appropriate content"""
        test_cases = [
            {
                "score": 4,
                "expected_keywords": ["4/4 poin", "semua aspek", "dengan benar"]
            },
            {
                "score": 3,
                "expected_keywords": ["3/4 poin", "3 dari 4 aspek"]
            },
            {
                "score": 2,
                "expected_keywords": ["2/4 poin", "2 dari 4 aspek"]
            },
            {
                "score": 1,
                "expected_keywords": ["1/4 poin", "1 dari 4 aspek"]
            },
            {
                "score": 0,
                "expected_keywords": ["0/4 poin", "belum menjawab dengan benar"]
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(score=test_case["score"]):
                ai_answer = {
                    "operator": "Penjumlahan",
                    "angka_dalam_soal": "5,3",
                    "jawaban": "8"
                }
                
                # Create student answer that will result in the desired score
                if test_case["score"] == 4:
                    student_answer = {
                        "operator": "Penjumlahan",
                        "angka_dalam_soal": "5,3",
                        "jawaban": "8"
                    }
                elif test_case["score"] == 3:
                    student_answer = {
                        "operator": "Penjumlahan",
                        "angka_dalam_soal": "5,3",
                        "jawaban": "9"
                    }
                elif test_case["score"] == 2:
                    student_answer = {
                        "operator": "Penjumlahan",
                        "angka_dalam_soal": "5,4",
                        "jawaban": "9"
                    }
                elif test_case["score"] == 1:
                    student_answer = {
                        "operator": "Penjumlahan",
                        "angka_dalam_soal": "6,4",
                        "jawaban": "9"
                    }
                else:  # score == 0
                    student_answer = {
                        "operator": "Pengurangan",
                        "angka_dalam_soal": "6,4",
                        "jawaban": "9"
                    }
                
                result = compare_answers_internal(ai_answer, student_answer)
                
                # Check that deskripsi_analisis contains expected keywords
                deskripsi = result["deskripsi_analisis"]
                for keyword in test_case["expected_keywords"]:
                    self.assertIn(keyword, deskripsi)
    
    def test_koreksi_messages_content(self):
        """Test that koreksi messages are properly generated"""
        ai_answer = {
            "operator": "Penjumlahan",
            "angka_dalam_soal": "5,3",
            "jawaban": "8"
        }
        
        student_answer = {
            "operator": "Pengurangan",
            "angka_dalam_soal": "6,4",
            "jawaban": "9"
        }
        
        result = compare_answers_internal(ai_answer, student_answer)
        
        # Check that koreksi messages are generated
        self.assertIsInstance(result["koreksi"], list)
        self.assertGreater(len(result["koreksi"]), 0)
        
        # Check specific koreksi messages
        koreksi_text = " ".join(result["koreksi"])
        self.assertIn("Operator yang benar", koreksi_text)
        self.assertIn("Operan 1 yang benar", koreksi_text)
        self.assertIn("Operan 2 yang benar", koreksi_text)
        self.assertIn("Jawaban yang benar", koreksi_text)
        
        # Check that correct values are mentioned
        self.assertIn("Penjumlahan", koreksi_text)
        self.assertIn("5", koreksi_text)
        self.assertIn("3", koreksi_text)
        self.assertIn("8", koreksi_text)
    
    def test_difficulty_analysis_integration(self):
        """Test that difficulty analysis is properly integrated"""
        test_cases = [
            {
                "operator": "Penjumlahan",
                "angka_dalam_soal": "5,3",
                "expected_level": "dasar"
            },
            {
                "operator": "Penjumlahan",
                "angka_dalam_soal": "50,30",
                "expected_level": "menengah"
            },
            {
                "operator": "Perkalian",
                "angka_dalam_soal": "5,3",
                "expected_level": "dasar"
            },
            {
                "operator": "Perkalian",
                "angka_dalam_soal": "50,30",
                "expected_level": "lanjut"
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(operator=test_case["operator"], numbers=test_case["angka_dalam_soal"]):
                ai_answer = {
                    "operator": test_case["operator"],
                    "angka_dalam_soal": test_case["angka_dalam_soal"],
                    "jawaban": "8"
                }
                
                student_answer = {
                    "operator": test_case["operator"],
                    "angka_dalam_soal": test_case["angka_dalam_soal"],
                    "jawaban": "8"
                }
                
                result = compare_answers_internal(ai_answer, student_answer)
                
                # Check that difficulty analysis is included
                self.assertIn("difficulty_analysis", result)
                difficulty = result["difficulty_analysis"]
                
                self.assertIn("level", difficulty)
                self.assertIn("description", difficulty)
                self.assertIn("category", difficulty)
                self.assertIn("complexity_score", difficulty)
                
                # Check that difficulty level matches expected
                self.assertEqual(difficulty["level"], test_case["expected_level"])
    
    def test_gemini_integration(self):
        """Test that Gemini analysis is properly integrated"""
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
        
        # Check that Gemini analysis is included
        self.assertIn("gemini_used", result)
        self.assertIn("gemini_penjelasan", result)
        
        # Check that Gemini was used
        self.assertTrue(result["gemini_used"])
        self.assertIsInstance(result["gemini_penjelasan"], str)
        
        # Check that Gemini analysis is mentioned in deskripsi_analisis
        deskripsi = result["deskripsi_analisis"]
        self.assertIn("[Gemini]", deskripsi)
        self.assertIn("Operator:", deskripsi)
        self.assertIn("Angka:", deskripsi)
        self.assertIn("Jawaban:", deskripsi)
        self.assertIn("Penjelasan:", deskripsi)

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestCompareIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    print(f"\n{'='*60}") 