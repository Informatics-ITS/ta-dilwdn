#!/usr/bin/env python3
"""
Script untuk menjalankan semua unit test compare_answers_internal
"""

import unittest
import sys
import os
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_all_tests():
    """Run all compare_answers_internal tests"""
    
    print("=" * 80)
    print("COMPARE ANSWERS INTERNAL - UNIT TESTING SUITE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Import test modules
    try:
        from test_compare_scoring import TestCompareScoring, TestCompareScoringEdgeCases
        from test_compare_integration import TestCompareIntegration
        print("✓ Test modules imported successfully")
    except ImportError as e:
        print(f"✗ Error importing test modules: {e}")
        return False
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestCompareScoring,
        TestCompareScoringEdgeCases,
        TestCompareIntegration
    ]
    
    for test_class in test_classes:
        test_suite.addTest(unittest.makeSuite(test_class))
    
    print(f"✓ Test suite created with {len(test_classes)} test classes")
    print()
    
    # Run tests
    print("Running tests...")
    print("-" * 40)
    
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    end_time = time.time()
    
    # Calculate statistics
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
    duration = end_time - start_time
    
    # Print detailed summary
    print()
    print("=" * 80)
    print("TEST EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Total tests run: {total_tests}")
    print(f"Successful: {total_tests - failures - errors}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Print failure details
    if failures > 0:
        print()
        print("FAILURES:")
        print("-" * 40)
        for test, traceback in result.failures:
            print(f"❌ {test}")
            print(f"   {traceback}")
            print()
    
    # Print error details
    if errors > 0:
        print()
        print("ERRORS:")
        print("-" * 40)
        for test, traceback in result.errors:
            print(f"💥 {test}")
            print(f"   {traceback}")
            print()
    
    # Print test categories summary
    print()
    print("TEST CATEGORIES SUMMARY")
    print("-" * 40)
    
    category_stats = {
        "Standardization Tests": 0,
        "Scoring Tests": 0,
        "Integration Tests": 0,
        "Edge Case Tests": 0
    }
    
    # Count tests by category (approximate based on test class names)
    for test_class in test_classes:
        class_name = test_class.__name__
        if "Scoring" in class_name and "Edge" not in class_name:
            category_stats["Scoring Tests"] += len(test_class.__dict__.get('__test__', []))
        elif "Edge" in class_name:
            category_stats["Edge Case Tests"] += len(test_class.__dict__.get('__test__', []))
        elif "Integration" in class_name:
            category_stats["Integration Tests"] += len(test_class.__dict__.get('__test__', []))
        else:
            category_stats["Standardization Tests"] += len(test_class.__dict__.get('__test__', []))
    
    for category, count in category_stats.items():
        print(f"{category}: {count} tests")
    
    # Print recommendations
    print()
    print("RECOMMENDATIONS")
    print("-" * 40)
    
    if success_rate == 100:
        print("🎉 All tests passed! The compare_answers_internal function is working correctly.")
        print("   - All standardization functions are working")
        print("   - Scoring system is accurate")
        print("   - Integration with Gemini is functional")
        print("   - Edge cases are handled properly")
    elif success_rate >= 90:
        print("✅ Most tests passed. Minor issues detected:")
        if failures > 0:
            print(f"   - {failures} test(s) failed - check failure details above")
        if errors > 0:
            print(f"   - {errors} test(s) had errors - check error details above")
    elif success_rate >= 70:
        print("⚠️  Significant issues detected:")
        print("   - Multiple test failures indicate problems with the scoring system")
        print("   - Review the failure details and fix the issues")
    else:
        print("❌ Critical issues detected:")
        print("   - High failure rate indicates major problems")
        print("   - The compare_answers_internal function needs significant fixes")
        print("   - Review all failure and error details")
    
    print()
    print("=" * 80)
    
    return success_rate == 100

def run_specific_test_category(category):
    """Run tests for a specific category"""
    
    categories = {
        "scoring": ["test_compare_scoring"],
        "integration": ["test_compare_integration"],
        "all": ["test_compare_scoring", "test_compare_integration"]
    }
    
    if category not in categories:
        print(f"Unknown category: {category}")
        print(f"Available categories: {list(categories.keys())}")
        return False
    
    print(f"Running {category} tests...")
    
    # Import and run specific test modules
    for module_name in categories[category]:
        try:
            module = __import__(module_name)
            test_suite = unittest.defaultTestLoader.loadTestsFromModule(module)
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(test_suite)
            
            print(f"\n{module_name} results:")
            print(f"  Tests: {result.testsRun}")
            print(f"  Failures: {len(result.failures)}")
            print(f"  Errors: {len(result.errors)}")
            
        except ImportError as e:
            print(f"Error importing {module_name}: {e}")
            return False
    
    return True

def main():
    """Main function"""
    
    if len(sys.argv) > 1:
        category = sys.argv[1].lower()
        if category in ["scoring", "integration", "all"]:
            return run_specific_test_category(category)
        else:
            print(f"Unknown category: {category}")
            print("Usage: python run_compare_tests.py [scoring|integration|all]")
            return False
    else:
        return run_all_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 