"""
Comprehensive test suite for Copy Trading Monitor.
Tests all critical functionality to prevent financial losses.

Run with: python -m pytest tests/ -v
Or: python tests/run_all_tests.py
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_config import TestConfig
from tests.test_order_detection import TestOrderDetection
from tests.test_rate_limiting import TestRateLimiting
from tests.test_smartapi_client import TestSmartAPIClient
from tests.test_market_hours import TestMarketHours

def run_all_tests():
    """Run all test suites."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestOrderDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestRateLimiting))
    suite.addTests(loader.loadTestsFromTestCase(TestSmartAPIClient))
    suite.addTests(loader.loadTestsFromTestCase(TestMarketHours))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED - System is safe to use!")
        return 0
    else:
        print("\n❌ TESTS FAILED - DO NOT USE IN PRODUCTION!")
        return 1

if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
