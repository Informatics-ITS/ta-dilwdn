#!/usr/bin/env python3
"""
Test runner for NLP extraction functionality

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --verbose          # Run with verbose output
    python run_tests.py --quick            # Run only quick tests
    python run_tests.py --integration      # Run only integration tests
"""

import sys
import os
import argparse
import unittest

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import test modules
from test_nlp_extraction import TestNLPExtraction, TestNLPIntegration


def run_tests(test_type='all', verbose=False):
    """
    Run the specified tests
    
    Args:
        test_type (str): Type of tests to run ('all', 'unit', 'integration', 'quick')
        verbose (bool): Whether to run with verbose output
    """
    
    # Set up test loader
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests based on type
    if test_type in ['all', 'unit']:
        print("Adding unit tests...")
        suite.addTests(loader.loadTestsFromTestCase(TestNLPExtraction))
    
    if test_type in ['all', 'integration']:
        print("Adding integration tests...")
        suite.addTests(loader.loadTestsFromTestCase(TestNLPIntegration))
    
    if test_type == 'quick':
        print("Adding quick tests only...")
        # Add only basic functionality tests
        suite.addTest(TestNLPExtraction('test_extract_math_simple_basic_operations'))
        suite.addTest(TestNLPExtraction('test_comparison_analysis_4_point_system'))
        suite.addTest(TestNLPExtraction('test_story_problem_ai_calculation'))
        suite.addTest(TestNLPExtraction('test_difficulty_level_analysis'))
        suite.addTest(TestNLPIntegration('test_full_pipeline'))
    
    # Set up test runner
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        stream=sys.stdout,
        buffer=True,
        descriptions=True
    )
    
    print(f"\n{'='*60}")
    print(f"Running {test_type} tests...")
    print(f"{'='*60}")
    
    # Run tests
    result = runner.run(suite)
    
    # Print detailed summary
    print(f"\n{'='*60}")
    print(f"Test Results Summary")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
        print(f"Success rate: {success_rate:.1f}%")
    
    # Print failure details
    if result.failures:
        print(f"\n{'='*40}")
        print("FAILURES:")
        print(f"{'='*40}")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"\n{i}. {test}")
            print("-" * 40)
            print(traceback)
    
    # Print error details
    if result.errors:
        print(f"\n{'='*40}")
        print("ERRORS:")
        print(f"{'='*40}")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"\n{i}. {test}")
            print("-" * 40)
            print(traceback)
    
    # Final status
    if result.wasSuccessful():
        print(f"\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ Some tests failed!")
        return 1


def main():
    """Main function to parse arguments and run tests"""
    
    parser = argparse.ArgumentParser(
        description='Run NLP extraction tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_tests.py                    # Run all tests
    python run_tests.py --verbose          # Run with verbose output
    python run_tests.py --quick            # Run only quick tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Run tests with verbose output'
    )
    
    parser.add_argument(
        '--quick', '-q',
        action='store_true',
        help='Run only quick/essential tests'
    )
    
    parser.add_argument(
        '--unit', '-u',
        action='store_true',
        help='Run only unit tests'
    )
    
    parser.add_argument(
        '--integration', '-i',
        action='store_true',
        help='Run only integration tests'
    )
    
    args = parser.parse_args()
    
    # Determine test type
    test_type = 'all'
    if args.quick:
        test_type = 'quick'
    elif args.unit:
        test_type = 'unit'
    elif args.integration:
        test_type = 'integration'
    
    # Run tests
    try:
        exit_code = run_tests(test_type=test_type, verbose=args.verbose)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Error running tests: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 