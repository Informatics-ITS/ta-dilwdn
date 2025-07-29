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
    standardize_operator, 
    standardize_angka_dalam_soal, 
    standardize_jawaban,
    get_difficulty_level
)

class TestCompareScoring(unittest.TestCase):
    """Unit tests for compare_answers_internal and scoring system"""
    
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
    
    def test_standardize_operator(self):
        """Test operator standardization"""
        test_cases = [
            ('+', 'Penjumlahan'),
            ('penjumlahan', 'Penjumlahan'),
            ('-', 'Pengurangan'),
            ('pengurangan', 'Pengurangan'),
            ('*', 'Perkalian'),
            ('x', 'Perkalian'),
            ('perkalian', 'Perkalian'),
            ('/', 'Pembagian'),
            (':', 'Pembagian'),
            ('÷', 'Pembagian'),
            ('pembagian', 'Pembagian'),
            ('unknown', 'Unknown'),
            ('MIX', 'Mix'),
        ]
        
        for input_op, expected in test_cases:
            with self.subTest(input_op=input_op):
                result = standardize_operator(input_op)
                self.assertEqual(result, expected)
    
    def test_standardize_angka_dalam_soal(self):
        """Test angka dalam soal standardization"""
        test_cases = [
            ('5,3', '5,3'),
            (['5', '3'], '5,3'),
            (' 5 , 3 ', '5,3'),
            ('10,20,30', '10,20,30'),
            ('5', '5'),
        ]
        
        for input_angka, expected in test_cases:
            with self.subTest(input_angka=input_angka):
                result = standardize_angka_dalam_soal(input_angka)
                self.assertEqual(result, expected)
    
    def test_standardize_jawaban(self):
        """Test jawaban standardization"""
        test_cases = [
            ('8', '8'),
            (8, '8'),
            (8.0, '8'),
            ('8.5', '8'),
            ('abc', 'abc'),
            (' 8 ', '8'),
        ]
        
        for input_jawaban, expected in test_cases:
            with self.subTest(input_jawaban=input_jawaban):
                result = standardize_jawaban(input_jawaban)
                self.assertEqual(result, expected)
    
    def test_perfect_score_4_points(self):
        """Test perfect score (4/4 points)"""
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
        self.assertEqual(result["nilai_maksimal"], 4)
        self.assertEqual(result["persentase"], 100.0)
        self.assertEqual(result["status"], "excellent")
        self.assertEqual(len(result["parameter_benar"]), 4)
        self.assertEqual(len(result["parameter_salah"]), 0)
        self.assertIn("operator", result["parameter_benar"])
        self.assertIn("operan_1", result["parameter_benar"])
        self.assertIn("operan_2", result["parameter_benar"])
        self.assertIn("jawaban", result["parameter_benar"])
    
    def test_score_3_points(self):
        """Test score 3/4 points (operator, operan_1, operan_2 correct, jawaban wrong)"""
        ai_answer = {
            "operator": "Penjumlahan",
            "angka_dalam_soal": "5,3",
            "jawaban": "8"
        }
        
        student_answer = {
            "operator": "Penjumlahan",
            "angka_dalam_soal": "5,3",
            "jawaban": "9"  # Wrong answer
        }
        
        result = compare_answers_internal(ai_answer, student_answer)
        
        self.assertEqual(result["nilai"], 3)
        self.assertEqual(result["persentase"], 75.0)
        self.assertEqual(result["status"], "good")
        self.assertEqual(len(result["parameter_benar"]), 3)
        self.assertEqual(len(result["parameter_salah"]), 1)
        self.assertIn("jawaban", result["parameter_salah"])
    
    def test_score_2_points(self):
        """Test score 2/4 points (operator and operan_1 correct)"""
        ai_answer = {
            "operator": "Penjumlahan",
            "angka_dalam_soal": "5,3",
            "jawaban": "8"
        }
        
        student_answer = {
            "operator": "Penjumlahan",
            "angka_dalam_soal": "5,4",  # Wrong operan_2
            "jawaban": "9"  # Wrong answer
        }
        
        result = compare_answers_internal(ai_answer, student_answer)
        
        self.assertEqual(result["nilai"], 2)
        self.assertEqual(result["persentase"], 50.0)
        self.assertEqual(result["status"], "fair")
        self.assertEqual(len(result["parameter_benar"]), 2)
        self.assertEqual(len(result["parameter_salah"]), 2)
    
    def test_score_1_point(self):
        """Test score 1/4 points (only operator correct)"""
        ai_answer = {
            "operator": "Penjumlahan",
            "angka_dalam_soal": "5,3",
            "jawaban": "8"
        }
        
        student_answer = {
            "operator": "Penjumlahan",
            "angka_dalam_soal": "6,4",  # Wrong operands
            "jawaban": "9"  # Wrong answer
        }
        
        result = compare_answers_internal(ai_answer, student_answer)
        
        self.assertEqual(result["nilai"], 1)
        self.assertEqual(result["persentase"], 25.0)
        self.assertEqual(result["status"], "poor")
        self.assertEqual(len(result["parameter_benar"]), 1)
        self.assertEqual(len(result["parameter_salah"]), 3)
    
    def test_score_0_points(self):
        """Test score 0/4 points (all wrong)"""
        ai_answer = {
            "operator": "Penjumlahan",
            "angka_dalam_soal": "5,3",
            "jawaban": "8"
        }
        
        student_answer = {
            "operator": "Pengurangan",  # Wrong operator
            "angka_dalam_soal": "6,4",  # Wrong operands
            "jawaban": "9"  # Wrong answer
        }
        
        result = compare_answers_internal(ai_answer, student_answer)
        
        self.assertEqual(result["nilai"], 0)
        self.assertEqual(result["persentase"], 0.0)
        self.assertEqual(result["status"], "incorrect")
        self.assertEqual(len(result["parameter_benar"]), 0)
        self.assertEqual(len(result["parameter_salah"]), 4)
    
    def test_different_operator_formats(self):
        """Test different operator formats are standardized correctly"""
        test_cases = [
            # (ai_operator, student_operator, expected_score)
            ('Penjumlahan', '+', 4),  # Standardized to Penjumlahan
            ('Penjumlahan', 'penjumlahan', 4),  # Case insensitive
            ('Perkalian', 'x', 4),  # x standardized to Perkalian
            ('Perkalian', '*', 4),  # * standardized to Perkalian
            ('Pembagian', '/', 4),  # / standardized to Pembagian
            ('Pembagian', ':', 4),  # : standardized to Pembagian
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
        """Test different number formats are handled correctly"""
        test_cases = [
            # (ai_numbers, student_numbers, expected_score)
            ('5,3', '5,3', 4),  # Same format
            ('5,3', ' 5 , 3 ', 4),  # With spaces
            ('5,3', ['5', '3'], 4),  # List format
            ('10,20', '10,20', 4),  # Larger numbers
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
        """Test different answer formats are standardized correctly"""
        test_cases = [
            # (ai_answer, student_answer, expected_score)
            ('8', '8', 4),  # String format
            (8, '8', 4),  # Integer vs string
            (8.0, '8', 4),  # Float vs string
            ('8', 8, 4),  # String vs integer
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
    
    def test_missing_data_handling(self):
        """Test handling of missing data in answers"""
        ai_answer = {
            "operator": "Penjumlahan",
            "angka_dalam_soal": "5,3",
            "jawaban": "8"
        }
        
        # Test with missing fields
        student_answer = {
            "operator": "Penjumlahan",
            # Missing angka_dalam_soal and jawaban
        }
        
        result = compare_answers_internal(ai_answer, student_answer)
        
        # Should handle missing data gracefully
        self.assertIsInstance(result["nilai"], int)
        self.assertIsInstance(result["persentase"], float)
        self.assertIn("status", result)
    
    def test_difficulty_analysis_integration(self):
        """Test that difficulty analysis is included in results"""
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
        
        # Check that difficulty analysis is included
        self.assertIn("difficulty_analysis", result)
        self.assertIsInstance(result["difficulty_analysis"], dict)
        self.assertIn("level", result["difficulty_analysis"])
        self.assertIn("description", result["difficulty_analysis"])
    
    def test_gemini_integration(self):
        """Test that Gemini analysis is included in results"""
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
        self.assertTrue(result["gemini_used"])
        self.assertIsInstance(result["gemini_penjelasan"], str)
    
    def test_deskripsi_analisis_format(self):
        """Test that deskripsi_analisis is properly formatted"""
        test_cases = [
            # (score, expected_keywords)
            (4, ["4/4 poin", "semua aspek"]),
            (3, ["3/4 poin", "3 dari 4 aspek"]),
            (2, ["2/4 poin", "2 dari 4 aspek"]),
            (1, ["1/4 poin", "1 dari 4 aspek"]),
            (0, ["0/4 poin", "belum menjawab dengan benar"]),
        ]
        
        for score, expected_keywords in test_cases:
            with self.subTest(score=score):
                ai_answer = {
                    "operator": "Penjumlahan",
                    "angka_dalam_soal": "5,3",
                    "jawaban": "8"
                }
                
                # Create student answer that will result in the desired score
                if score == 4:
                    student_answer = {
                        "operator": "Penjumlahan",
                        "angka_dalam_soal": "5,3",
                        "jawaban": "8"
                    }
                elif score == 3:
                    student_answer = {
                        "operator": "Penjumlahan",
                        "angka_dalam_soal": "5,3",
                        "jawaban": "9"  # Wrong answer
                    }
                elif score == 2:
                    student_answer = {
                        "operator": "Penjumlahan",
                        "angka_dalam_soal": "5,4",  # Wrong operan_2
                        "jawaban": "9"  # Wrong answer
                    }
                elif score == 1:
                    student_answer = {
                        "operator": "Penjumlahan",
                        "angka_dalam_soal": "6,4",  # Wrong operands
                        "jawaban": "9"  # Wrong answer
                    }
                else:  # score == 0
                    student_answer = {
                        "operator": "Pengurangan",  # Wrong operator
                        "angka_dalam_soal": "6,4",  # Wrong operands
                        "jawaban": "9"  # Wrong answer
                    }
                
                result = compare_answers_internal(ai_answer, student_answer)
                
                # Check that deskripsi_analisis contains expected keywords
                deskripsi = result["deskripsi_analisis"]
                for keyword in expected_keywords:
                    self.assertIn(keyword, deskripsi)
    
    def test_koreksi_messages(self):
        """Test that koreksi messages are properly generated"""
        ai_answer = {
            "operator": "Penjumlahan",
            "angka_dalam_soal": "5,3",
            "jawaban": "8"
        }
        
        student_answer = {
            "operator": "Pengurangan",  # Wrong operator
            "angka_dalam_soal": "6,4",  # Wrong operands
            "jawaban": "9"  # Wrong answer
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
    
    def test_get_difficulty_level(self):
        """Test difficulty level calculation"""
        test_cases = [
            # (operation, numbers, expected_level)
            ("Penjumlahan", ["5", "3"], "dasar"),
            ("Penjumlahan", ["50", "30"], "menengah"),
            ("Penjumlahan", ["500", "300"], "lanjut"),
            ("Perkalian", ["5", "3"], "dasar"),
            ("Perkalian", ["50", "30"], "lanjut"),
            ("Mix", ["5", "3", "10"], "unknown"),
        ]
        
        for operation, numbers, expected_level in test_cases:
            with self.subTest(operation=operation, numbers=numbers):
                result = get_difficulty_level(operation, numbers)
                self.assertEqual(result["level"], expected_level)
                self.assertIn("description", result)
                self.assertIn("category", result)
                self.assertIn("complexity_score", result)

class TestCompareScoringEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock Gemini sleep to avoid delays in testing
        self.gemini_sleep_patcher = patch('app.time.sleep')
        self.mock_sleep = self.gemini_sleep_patcher.start()
        
        # Mock Gemini analysis
        self.gemini_patcher = patch('app.analyze_math_problem_with_gemini')
        self.mock_gemini = self.gemini_patcher.start()
        self.mock_gemini.return_value = {
            "status": "success",
            "analysis": {
                "operator": "Penjumlahan",
                "angka_dalam_soal": "5,3",
                "jawaban": "8"
            },
            "penjelasan": "Analisis Gemini"
        }
    
    def tearDown(self):
        """Clean up after tests"""
        self.gemini_sleep_patcher.stop()
        self.gemini_patcher.stop()
    
    def test_empty_inputs(self):
        """Test with empty inputs"""
        ai_answer = {}
        student_answer = {}
        
        result = compare_answers_internal(ai_answer, student_answer)
        
        # Should handle empty inputs gracefully
        self.assertIsInstance(result["nilai"], int)
        self.assertIsInstance(result["persentase"], float)
        self.assertEqual(result["nilai"], 0)
        self.assertEqual(result["persentase"], 0.0)
    
    def test_none_inputs(self):
        """Test with None inputs"""
        ai_answer = None
        student_answer = None
        
        result = compare_answers_internal(ai_answer, student_answer)
        
        # Should handle None inputs gracefully
        self.assertIsInstance(result["nilai"], int)
        self.assertIsInstance(result["persentase"], float)
    
    def test_invalid_number_formats(self):
        """Test with invalid number formats"""
        ai_answer = {
            "operator": "Penjumlahan",
            "angka_dalam_soal": "abc,def",  # Invalid numbers
            "jawaban": "8"
        }
        
        student_answer = {
            "operator": "Penjumlahan",
            "angka_dalam_soal": "5,3",
            "jawaban": "8"
        }
        
        result = compare_answers_internal(ai_answer, student_answer)
        
        # Should handle invalid formats gracefully
        self.assertIsInstance(result["nilai"], int)
        self.assertIsInstance(result["persentase"], float)
    
    def test_mixed_operator_case_sensitivity(self):
        """Test case sensitivity in operator comparison"""
        test_cases = [
            ("PENJUMLAHAN", "penjumlahan", 4),
            ("Penjumlahan", "PENJUMLAHAN", 4),
            ("penjumlahan", "Penjumlahan", 4),
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
    
    def test_single_number_operands(self):
        """Test with single number operands"""
        ai_answer = {
            "operator": "Penjumlahan",
            "angka_dalam_soal": "5",  # Single number
            "jawaban": "5"
        }
        
        student_answer = {
            "operator": "Penjumlahan",
            "angka_dalam_soal": "5",
            "jawaban": "5"
        }
        
        result = compare_answers_internal(ai_answer, student_answer)
        
        # Should handle single number gracefully
        self.assertIsInstance(result["nilai"], int)
        self.assertIsInstance(result["persentase"], float)
    
    def test_three_or_more_numbers(self):
        """Test with three or more numbers"""
        ai_answer = {
            "operator": "Mix",
            "angka_dalam_soal": "5,3,10",  # Three numbers
            "jawaban": "8"
        }
        
        student_answer = {
            "operator": "Mix",
            "angka_dalam_soal": "5,3,10",
            "jawaban": "8"
        }
        
        result = compare_answers_internal(ai_answer, student_answer)
        
        # Should handle multiple numbers gracefully
        self.assertIsInstance(result["nilai"], int)
        self.assertIsInstance(result["persentase"], float)

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestCompareScoring))
    test_suite.addTest(unittest.makeSuite(TestCompareScoringEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
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