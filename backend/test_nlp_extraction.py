import unittest
import sys
import os

# Add the backend directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import extract_math_simple, solve_text_internal, compare_answers_internal


class TestNLPExtraction(unittest.TestCase):
    """
    Unit tests for NLP-based math extraction functionality
    """
    
    def setUp(self):
        """Set up test cases"""
        self.test_cases = [
            # Basic arithmetic operations
            {
                'input': '3+2=5',
                'expected': {
                    'operator': 'Penjumlahan',
                    'angka_dalam_soal': '3,2',
                    'jawaban': '5'
                }
            },
            {
                'input': '10-4=6',
                'expected': {
                    'operator': 'Pengurangan',
                    'angka_dalam_soal': '10,4',
                    'jawaban': '6'
                }
            },
            {
                'input': '7*3=21',
                'expected': {
                    'operator': 'Perkalian',
                    'angka_dalam_soal': '7,3',
                    'jawaban': '21'
                }
            },
            {
                'input': '8/2=4',
                'expected': {
                    'operator': 'Pembagian',
                    'angka_dalam_soal': '8,2',
                    'jawaban': '4'
                }
            },
            # Different operator symbols
            {
                'input': '5x4=20',
                'expected': {
                    'operator': 'Perkalian',
                    'angka_dalam_soal': '5,4',
                    'jawaban': '20'
                }
            },
            {
                'input': '12÷3=4',
                'expected': {
                    'operator': 'Pembagian',
                    'angka_dalam_soal': '12,3',
                    'jawaban': '4'
                }
            },
            # With spaces
            {
                'input': '15 + 25 = 40',
                'expected': {
                    'operator': 'Penjumlahan',
                    'angka_dalam_soal': '15,25',
                    'jawaban': '40'
                }
            },
            # Story problems (simplified text)
            {
                'input': 'Andi punya 5 apel, lalu dia beli 3 apel lagi. Berapa total apel Andi? 5+3=8',
                'expected': {
                    'operator': 'Penjumlahan',
                    'angka_dalam_soal': '5,3',
                    'jawaban': '8'
                }
            },
            # Edge cases
            {
                'input': '0+0=0',
                'expected': {
                    'operator': 'Penjumlahan',
                    'angka_dalam_soal': '0,0',
                    'jawaban': '0'
                }
            },
            {
                'input': '100-50=50',
                'expected': {
                    'operator': 'Pengurangan',
                    'angka_dalam_soal': '100,50',
                    'jawaban': '50'
                }
            }
        ]
        
        # Test cases for comparison analysis
        self.comparison_test_cases = [
            # Perfect match (4 points)
            {
                'ai_answer': {
                    'operator': 'Penjumlahan',
                    'angka_dalam_soal': '3,2',
                    'jawaban': '5'
                },
                'student_answer': {
                    'operator': 'Penjumlahan',
                    'angka_dalam_soal': '3,2',
                    'jawaban': '5'
                },
                'expected_nilai': 4,
                'expected_status': 'excellent'
            },
            # Good match (3 points - wrong final answer)
            {
                'ai_answer': {
                    'operator': 'Penjumlahan',
                    'angka_dalam_soal': '3,2',
                    'jawaban': '5'
                },
                'student_answer': {
                    'operator': 'Penjumlahan',
                    'angka_dalam_soal': '3,2',
                    'jawaban': '6'
                },
                'expected_nilai': 3,
                'expected_status': 'good'
            },
            # Fair match (2 points - wrong operator and answer)
            {
                'ai_answer': {
                    'operator': 'Penjumlahan',
                    'angka_dalam_soal': '3,2',
                    'jawaban': '5'
                },
                'student_answer': {
                    'operator': 'Pengurangan',
                    'angka_dalam_soal': '3,2',
                    'jawaban': '1'
                },
                'expected_nilai': 2,
                'expected_status': 'fair'
            },
            # Poor match (1 point - only operator correct)
            {
                'ai_answer': {
                    'operator': 'Penjumlahan',
                    'angka_dalam_soal': '3,2',
                    'jawaban': '5'
                },
                'student_answer': {
                    'operator': 'Penjumlahan',
                    'angka_dalam_soal': '4,5',
                    'jawaban': '10'
                },
                'expected_nilai': 1,
                'expected_status': 'poor'
            },
            # Incorrect (0 points)
            {
                'ai_answer': {
                    'operator': 'Penjumlahan',
                    'angka_dalam_soal': '3,2',
                    'jawaban': '5'
                },
                'student_answer': {
                    'operator': 'Perkalian',
                    'angka_dalam_soal': '4,5',
                    'jawaban': '20'
                },
                'expected_nilai': 0,
                'expected_status': 'incorrect'
            }
        ]

    def test_extract_math_simple_basic_operations(self):
        """Test basic arithmetic operations extraction"""
        for i, test_case in enumerate(self.test_cases[:7]):  # First 7 are basic operations
            with self.subTest(i=i, input=test_case['input']):
                result = extract_math_simple(test_case['input'])
                
                self.assertEqual(result['operator'], test_case['expected']['operator'], 
                               f"Operator mismatch for input: {test_case['input']}")
                self.assertEqual(result['angka_dalam_soal'], test_case['expected']['angka_dalam_soal'],
                               f"Numbers mismatch for input: {test_case['input']}")
                self.assertEqual(str(result['jawaban']), test_case['expected']['jawaban'],
                               f"Answer mismatch for input: {test_case['input']}")

    def test_solve_text_internal(self):
        """Test the solve_text_internal function"""
        for i, test_case in enumerate(self.test_cases):
            with self.subTest(i=i, input=test_case['input']):
                result = solve_text_internal(test_case['input'])
                
                # Check if result has required keys
                self.assertIn('operator', result)
                self.assertIn('angka_dalam_soal', result)
                self.assertIn('jawaban', result)
                self.assertIn('soal_cerita', result)
                
                # For the first few basic cases, check exact matches
                if i < 7:  # Basic arithmetic operations
                    self.assertEqual(result['operator'], test_case['expected']['operator'])
                    self.assertEqual(result['angka_dalam_soal'], test_case['expected']['angka_dalam_soal'])
                    self.assertEqual(str(result['jawaban']), test_case['expected']['jawaban'])

    def test_comparison_analysis_4_point_system(self):
        """Test the 4-point comparison analysis system"""
        for i, test_case in enumerate(self.comparison_test_cases):
            with self.subTest(i=i, case=f"Expected {test_case['expected_nilai']} points"):
                result = compare_answers_internal(
                    test_case['ai_answer'], 
                    test_case['student_answer']
                )
                
                # Check score
                self.assertEqual(result['nilai'], test_case['expected_nilai'],
                               f"Expected {test_case['expected_nilai']} points, got {result['nilai']}")
                
                # Check status
                self.assertEqual(result['status'], test_case['expected_status'],
                               f"Expected status '{test_case['expected_status']}', got '{result['status']}'")
                
                # Check that nilai_maksimal is 4
                self.assertEqual(result['nilai_maksimal'], 4)
                
                # Check percentage calculation
                expected_percentage = (test_case['expected_nilai'] / 4) * 100
                self.assertEqual(result['persentase'], expected_percentage)
                
                # Check that difficulty analysis is included
                self.assertIn('difficulty_analysis', result)
                self.assertIsInstance(result['difficulty_analysis'], dict)
                self.assertIn('level', result['difficulty_analysis'])
                self.assertIn('description', result['difficulty_analysis'])

    def test_operator_recognition(self):
        """Test different operator symbol recognition"""
        operator_tests = [
            ('+', 'Penjumlahan'),
            ('-', 'Pengurangan'),
            ('*', 'Perkalian'),
            ('x', 'Perkalian'),
            ('×', 'Perkalian'),
            ('/', 'Pembagian'),
            (':', 'Pembagian'),
            ('÷', 'Pembagian'),
        ]
        
        for symbol, expected_label in operator_tests:
            with self.subTest(operator=symbol):
                test_input = f"5{symbol}2=10"
                result = extract_math_simple(test_input)
                self.assertEqual(result['operator'], expected_label,
                               f"Operator '{symbol}' should be recognized as '{expected_label}'")

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        edge_cases = [
            # Empty input
            '',
            # Invalid format
            'abc',
            # Missing equals sign
            '3+2',
            # Missing operands
            '+=5',
            # Only numbers
            '123',
            # Only operators
            '+++'
        ]
        
        for test_input in edge_cases:
            with self.subTest(input=test_input):
                result = extract_math_simple(test_input)
                
                # Should not crash and should return a dict with required keys
                self.assertIsInstance(result, dict)
                self.assertIn('operator', result)
                self.assertIn('angka_dalam_soal', result)
                self.assertIn('jawaban', result)
                self.assertIn('soal_cerita', result)

    def test_comparison_parameter_tracking(self):
        """Test that comparison correctly tracks which parameters are correct/wrong"""
        ai_answer = {
            'operator': 'Penjumlahan',
            'angka_dalam_soal': '3,2',
            'jawaban': '5'
        }
        
        # Test case where only operand 1 is wrong
        student_answer = {
            'operator': 'Penjumlahan',
            'angka_dalam_soal': '4,2',  # First operand wrong
            'jawaban': '5'
        }
        
        result = compare_answers_internal(ai_answer, student_answer)
        
        # Should have 3 points (operator + operand2 + answer correct)
        self.assertEqual(result['nilai'], 3)
        self.assertIn('operan_1', result['parameter_salah'])
        self.assertIn('operator', result['parameter_benar'])
        self.assertIn('operan_2', result['parameter_benar'])
        self.assertIn('jawaban', result['parameter_benar'])

    def test_difficulty_level_analysis(self):
        """Test difficulty level analysis based on number ranges"""
        difficulty_test_cases = [
            # Penjumlahan/Pengurangan - level dasar (hingga 20)
            {
                'operation': 'Penjumlahan',
                'numbers': ['15', '5'],
                'expected_level': 'dasar',
                'expected_category': 'elementary',
                'expected_complexity': 1,
                'description_contains': 'Penjumlahan bilangan cacah hingga 20'
            },
            {
                'operation': 'Pengurangan',
                'numbers': ['18', '7'],
                'expected_level': 'dasar',
                'expected_category': 'elementary',
                'expected_complexity': 1,
                'description_contains': 'Pengurangan bilangan cacah hingga 20'
            },
            
            # Penjumlahan/Pengurangan - level menengah (hingga 100)
            {
                'operation': 'Penjumlahan',
                'numbers': ['45', '35'],
                'expected_level': 'menengah',
                'expected_category': 'intermediate',
                'expected_complexity': 2,
                'description_contains': 'Penjumlahan bilangan cacah hingga 100'
            },
            {
                'operation': 'Pengurangan',
                'numbers': ['85', '25'],
                'expected_level': 'menengah',
                'expected_category': 'intermediate',
                'expected_complexity': 2,
                'description_contains': 'Pengurangan bilangan cacah hingga 100'
            },
            
            # Penjumlahan/Pengurangan - level lanjut (hingga 1000)
            {
                'operation': 'Penjumlahan',
                'numbers': ['450', '350'],
                'expected_level': 'lanjut',
                'expected_category': 'advanced',
                'expected_complexity': 3,
                'description_contains': 'Penjumlahan bilangan cacah hingga 1000'
            },
            
            # Perkalian/Pembagian - level dasar (hingga 100)
            {
                'operation': 'Perkalian',
                'numbers': ['8', '12'],
                'expected_level': 'dasar',
                'expected_category': 'elementary',
                'expected_complexity': 2,
                'description_contains': 'Perkalian bilangan cacah hingga 100'
            },
            {
                'operation': 'Pembagian',
                'numbers': ['48', '6'],
                'expected_level': 'dasar',
                'expected_category': 'elementary',
                'expected_complexity': 2,
                'description_contains': 'Pembagian bilangan cacah hingga 100'
            },
            
            # Perkalian/Pembagian - level lanjut (di atas 100)
            {
                'operation': 'Perkalian',
                'numbers': ['25', '150'],
                'expected_level': 'lanjut',
                'expected_category': 'advanced',
                'expected_complexity': 3,
                'description_contains': 'Perkalian bilangan cacah di atas 100'
            },
        ]
        
        from app import get_difficulty_level
        
        for i, test_case in enumerate(difficulty_test_cases):
            with self.subTest(i=i, operation=test_case['operation'], numbers=test_case['numbers']):
                result = get_difficulty_level(test_case['operation'], test_case['numbers'])
                
                # Check level
                self.assertEqual(result['level'], test_case['expected_level'],
                               f"Expected level '{test_case['expected_level']}', got '{result['level']}'")
                
                # Check category
                self.assertEqual(result['category'], test_case['expected_category'],
                               f"Expected category '{test_case['expected_category']}', got '{result['category']}'")
                
                # Check complexity score
                self.assertEqual(result['complexity_score'], test_case['expected_complexity'],
                               f"Expected complexity {test_case['expected_complexity']}, got {result['complexity_score']}")
                
                # Check description contains expected text
                self.assertIn(test_case['description_contains'], result['description'],
                            f"Description '{result['description']}' should contain '{test_case['description_contains']}'")
                
                # Check max_number is calculated correctly
                expected_max = max([int(num) for num in test_case['numbers']])
                self.assertEqual(result['max_number'], expected_max,
                               f"Expected max_number {expected_max}, got {result['max_number']}")

    def test_difficulty_in_comparison_analysis(self):
        """Test that difficulty analysis is integrated into comparison results"""
        # Test with different difficulty levels
        test_scenarios = [
            {
                'name': 'Dasar - Penjumlahan hingga 20',
                'ai_answer': {
                    'operator': 'Penjumlahan',
                    'angka_dalam_soal': '15,5',
                    'jawaban': '20'
                },
                'student_answer': {
                    'operator': 'Penjumlahan',
                    'angka_dalam_soal': '15,5',
                    'jawaban': '20'
                },
                'expected_difficulty_level': 'dasar',
                'expected_complexity': 1
            },
            {
                'name': 'Menengah - Pengurangan hingga 100',
                'ai_answer': {
                    'operator': 'Pengurangan',
                    'angka_dalam_soal': '85,25',
                    'jawaban': '60'
                },
                'student_answer': {
                    'operator': 'Pengurangan',
                    'angka_dalam_soal': '85,25',
                    'jawaban': '60'
                },
                'expected_difficulty_level': 'menengah',
                'expected_complexity': 2
            },
            {
                'name': 'Lanjut - Perkalian di atas 100',
                'ai_answer': {
                    'operator': 'Perkalian',
                    'angka_dalam_soal': '25,150',
                    'jawaban': '3750'
                },
                'student_answer': {
                    'operator': 'Perkalian',
                    'angka_dalam_soal': '25,150',
                    'jawaban': '3750'
                },
                'expected_difficulty_level': 'lanjut',
                'expected_complexity': 3
            }
        ]
        
        for scenario in test_scenarios:
            with self.subTest(scenario=scenario['name']):
                result = compare_answers_internal(scenario['ai_answer'], scenario['student_answer'])
                
                # Check that difficulty analysis exists
                self.assertIn('difficulty_analysis', result)
                difficulty = result['difficulty_analysis']
                
                # Check difficulty level
                self.assertEqual(difficulty['level'], scenario['expected_difficulty_level'])
                
                # Check complexity score
                self.assertEqual(difficulty['complexity_score'], scenario['expected_complexity'])
                
                # Check that description appears in main analysis
                self.assertIn(difficulty['description'], result['deskripsi_analisis'])
                
                # For perfect matches, should still have high score regardless of difficulty
                self.assertEqual(result['nilai'], 4)
                self.assertEqual(result['status'], 'excellent')

    def test_story_problem_extraction(self):
        """Test extraction from story problems"""
        story_problems = [
            {
                'input': 'Sari memiliki 8 kelereng. Dia memberikan 3 kelereng kepada adiknya. Berapa kelereng Sari sekarang? 8-3=5',
                'should_contain_numbers': ['8', '3', '5'],
                'should_contain_operator': 'Pengurangan'
            },
            {
                'input': 'Di toko ada 12 roti. Ibu membeli 4 roti. Berapa roti yang tersisa? 12-4=8',
                'should_contain_numbers': ['12', '4', '8'],
                'should_contain_operator': 'Pengurangan'
            }
        ]
        
        for story in story_problems:
            with self.subTest(story=story['input'][:50] + "..."):
                result = solve_text_internal(story['input'])
                
                # Check if key numbers are extracted
                extracted_numbers = result['angka_dalam_soal'].split(',')
                for expected_number in story['should_contain_numbers'][:2]:  # First two numbers
                    self.assertIn(expected_number, extracted_numbers,
                                f"Expected number '{expected_number}' not found in extracted numbers")
                
                # Check operator
                if story['should_contain_operator']:
                    self.assertEqual(result['operator'], story['should_contain_operator'])

    def test_story_problem_ai_calculation(self):
        """Test story problems where AI must calculate the answer"""
        story_test_cases = [
            # Pengurangan (subtraction) stories
            {
                'input': 'Andi memiliki 15 buah jeruk. Dia memberikan 7 jeruk kepada temannya. Berapa jeruk yang tersisa?',
                'should_extract': {
                    'numbers': ['15', '7'],
                    'operator': 'Pengurangan',
                    'expected_answer': 8
                },
                'description': 'Subtraction story - giving away items'
            },
            {
                'input': 'Di perpustakaan ada 25 buku. Siswa meminjam 9 buku. Berapa buku yang masih ada di perpustakaan?',
                'should_extract': {
                    'numbers': ['25', '9'],
                    'operator': 'Pengurangan', 
                    'expected_answer': 16
                },
                'description': 'Subtraction story - borrowing items'
            },
            
            # Perkalian (multiplication) stories
            {
                'input': 'Setiap kotak berisi 6 pensil. Jika ada 4 kotak, berapa total pensil?',
                'should_extract': {
                    'numbers': ['6', '4'],
                    'operator': 'Perkalian',
                    'expected_answer': 24
                },
                'description': 'Multiplication story - groups of items'
            },
            {
                'input': 'Ibu membeli 3 pak telur. Setiap pak berisi 12 telur. Berapa total telur yang dibeli ibu?',
                'should_extract': {
                    'numbers': ['3', '12'],
                    'operator': 'Perkalian',
                    'expected_answer': 36
                },
                'description': 'Multiplication story - packages'
            },
            {
                'input': 'Seorang petani menanam 8 baris jagung. Setiap baris ada 15 tanaman. Berapa total tanaman jagung?',
                'should_extract': {
                    'numbers': ['8', '15'],
                    'operator': 'Perkalian',
                    'expected_answer': 120
                },
                'description': 'Multiplication story - rows and columns'
            },
            
            # Pembagian (division) stories
            {
                'input': 'Bu guru akan membagi 24 permen kepada 6 anak secara merata. Berapa permen yang diterima setiap anak?',
                'should_extract': {
                    'numbers': ['24', '6'],
                    'operator': 'Pembagian',
                    'expected_answer': 4
                },
                'description': 'Division story - equal sharing'
            },
            {
                'input': 'Pak Ali memiliki 45 apel. Dia ingin memasukkannya ke dalam keranjang yang masing-masing berisi 9 apel. Berapa keranjang yang dibutuhkan?',
                'should_extract': {
                    'numbers': ['45', '9'],
                    'operator': 'Pembagian',
                    'expected_answer': 5
                },
                'description': 'Division story - grouping'
            },
            {
                'input': 'Di sekolah ada 56 siswa yang akan dibagi menjadi 7 kelompok sama banyak. Berapa siswa di setiap kelompok?',
                'should_extract': {
                    'numbers': ['56', '7'],
                    'operator': 'Pembagian',
                    'expected_answer': 8
                },
                'description': 'Division story - equal groups'
            }
        ]
        
        for i, test_case in enumerate(story_test_cases):
            with self.subTest(i=i, desc=test_case['description']):
                result = solve_text_internal(test_case['input'])
                
                # Check if result has required structure
                self.assertIn('operator', result)
                self.assertIn('angka_dalam_soal', result)
                self.assertIn('jawaban', result)
                self.assertIn('soal_cerita', result)
                
                # Check if numbers are extracted correctly
                extracted_numbers = result['angka_dalam_soal'].split(',')
                expected_numbers = test_case['should_extract']['numbers']
                
                # Should contain the expected numbers (order might vary)
                for expected_num in expected_numbers:
                    self.assertIn(expected_num, extracted_numbers,
                                f"Number '{expected_num}' not found in {extracted_numbers} for: {test_case['input'][:50]}...")
                
                # Check if operator is correctly identified
                expected_operator = test_case['should_extract']['operator']
                self.assertEqual(result['operator'], expected_operator,
                               f"Expected operator '{expected_operator}', got '{result['operator']}' for: {test_case['input'][:50]}...")
                
                # Check if AI calculated the correct answer
                expected_answer = test_case['should_extract']['expected_answer']
                actual_answer = result['jawaban']
                
                # Convert to int for comparison if it's a string
                if isinstance(actual_answer, str):
                    try:
                        actual_answer = int(actual_answer)
                    except ValueError:
                        self.fail(f"AI answer '{actual_answer}' is not a valid number for: {test_case['input'][:50]}...")
                
                self.assertEqual(actual_answer, expected_answer,
                               f"Expected answer {expected_answer}, got {actual_answer} for: {test_case['input'][:50]}...")

    def test_complex_story_problem_scenarios(self):
        """Test more complex story problem scenarios"""
        complex_scenarios = [
            # Mixed operations in story context
            {
                'input': 'Di kebun ada 20 pohon mangga. Setiap pohon menghasilkan 8 buah mangga. Berapa total mangga di kebun?',
                'expected_operation': 'Perkalian',
                'expected_numbers': ['20', '8'],
                'expected_result': 160,
                'difficulty': 'medium'
            },
            {
                'input': 'Seorang penjual memiliki 72 donat. Dia menjual donat dalam kotak yang berisi 12 donat. Berapa kotak yang bisa dia buat?',
                'expected_operation': 'Pembagian', 
                'expected_numbers': ['72', '12'],
                'expected_result': 6,
                'difficulty': 'medium'
            },
            {
                'input': 'Rina mempunyai 50 stiker. Dia memberikan 18 stiker kepada adiknya. Berapa stiker yang masih dimiliki Rina?',
                'expected_operation': 'Pengurangan',
                'expected_numbers': ['50', '18'], 
                'expected_result': 32,
                'difficulty': 'easy'
            }
        ]
        
        for i, scenario in enumerate(complex_scenarios):
            with self.subTest(i=i, difficulty=scenario['difficulty']):
                result = solve_text_internal(scenario['input'])
                
                # Test operator recognition
                self.assertEqual(result['operator'], scenario['expected_operation'],
                               f"Operator mismatch in scenario {i+1}")
                
                # Test number extraction
                extracted_numbers = result['angka_dalam_soal'].split(',')
                for expected_num in scenario['expected_numbers']:
                    self.assertIn(expected_num, extracted_numbers,
                                f"Number {expected_num} not extracted in scenario {i+1}")
                
                # Test calculation
                if isinstance(result['jawaban'], str):
                    try:
                        calculated_result = int(result['jawaban'])
                    except ValueError:
                        calculated_result = result['jawaban']
                else:
                    calculated_result = result['jawaban']
                
                self.assertEqual(calculated_result, scenario['expected_result'],
                               f"Calculation error in scenario {i+1}: expected {scenario['expected_result']}, got {calculated_result}")

    def test_story_problem_edge_cases(self):
        """Test edge cases in story problems"""
        edge_cases = [
            # Zero handling
            {
                'input': 'Andi memiliki 5 kelereng. Dia memberikan semua kelerengnya kepada temannya. Berapa kelereng yang tersisa?',
                'contains_numbers': ['5'],
                'should_handle_gracefully': True
            },
            # Large numbers
            {
                'input': 'Sebuah pabrik memproduksi 1000 botol per hari. Jika ada 30 hari dalam sebulan, berapa total botol yang diproduksi?',
                'contains_numbers': ['1000', '30'],
                'expected_operator': 'Perkalian',
                'should_handle_gracefully': True
            },
            # No clear math operation
            {
                'input': 'Andi pergi ke sekolah setiap hari.',
                'should_handle_gracefully': True
            }
        ]
        
        for i, edge_case in enumerate(edge_cases):
            with self.subTest(i=i, case=edge_case['input'][:30] + "..."):
                # Should not crash
                try:
                    result = solve_text_internal(edge_case['input'])
                    
                    # Should return a valid structure
                    self.assertIsInstance(result, dict)
                    self.assertIn('operator', result)
                    self.assertIn('angka_dalam_soal', result) 
                    self.assertIn('jawaban', result)
                    self.assertIn('soal_cerita', result)
                    
                    # If we expect certain numbers, check they're extracted
                    if 'contains_numbers' in edge_case:
                        extracted_numbers = result['angka_dalam_soal'].split(',')
                        for expected_num in edge_case['contains_numbers']:
                            # Should at least try to extract the number
                            pass  # Just check it doesn't crash
                    
                except Exception as e:
                    if edge_case['should_handle_gracefully']:
                        self.fail(f"Should handle edge case gracefully but got error: {e}")
                    else:
                        pass  # Expected to fail

    def test_performance_basic(self):
        """Test basic performance - extraction should be fast"""
        import time
        
        test_input = "5+3=8"
        start_time = time.time()
        
        # Run extraction 100 times
        for _ in range(100):
            extract_math_simple(test_input)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should complete 100 extractions in less than 1 second
        self.assertLess(elapsed, 1.0, "Extraction should be fast")

    def test_consistent_results(self):
        """Test that same input produces consistent results"""
        test_input = "7*6=42"
        
        # Run extraction multiple times
        results = []
        for _ in range(10):
            result = extract_math_simple(test_input)
            results.append(result)
        
        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            self.assertEqual(result, first_result, "Results should be consistent")


class TestNLPIntegration(unittest.TestCase):
    """
    Integration tests for NLP extraction with the broader system
    """
    
    def test_full_pipeline(self):
        """Test the full pipeline from text input to comparison analysis"""
        # Simulate a complete workflow
        original_problem = "6+4=10"
        student_answer_text = "6+4=10"  # Correct answer
        
        # Step 1: Extract from original problem (teacher's answer key)
        ai_answer = solve_text_internal(original_problem)
        
        # Step 2: Extract from student answer
        student_answer = solve_text_internal(student_answer_text)
        
        # Step 3: Compare answers
        comparison = compare_answers_internal(ai_answer, student_answer)
        
        # Should get perfect score
        self.assertEqual(comparison['nilai'], 4)
        self.assertEqual(comparison['status'], 'excellent')
        
    def test_partial_credit_scenario(self):
        """Test scenario where student gets partial credit"""
        ai_answer = {
            'operator': 'Penjumlahan',
            'angka_dalam_soal': '5,3',
            'jawaban': '8'
        }
        
        # Student gets numbers right but wrong operation
        student_answer_text = "5*3=15"
        student_extracted = solve_text_internal(student_answer_text)
        
        comparison = compare_answers_internal(ai_answer, student_extracted)
        
        # Should get points for correct operands only
        self.assertGreater(comparison['nilai'], 0)
        self.assertLess(comparison['nilai'], 4)
        self.assertIn('operator', comparison['parameter_salah'])
        self.assertIn('jawaban', comparison['parameter_salah'])


if __name__ == '__main__':
    # Set up test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestNLPExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestNLPIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code) 