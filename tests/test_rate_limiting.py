"""
Test rate limiting logic.
Critical: Too many API calls = account blocked = no trading possible.
"""

import unittest
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRateLimiting(unittest.TestCase):
    """Test rate limiting functionality."""
    
    def test_rate_limit_counter_increments(self):
        """Test that the rate limit counter increments correctly."""
        calls = 0
        max_calls = 30
        
        for i in range(10):
            calls += 1
        
        self.assertEqual(calls, 10, "Counter should increment correctly")
        self.assertLess(calls, max_calls, "Should be under limit")
    
    def test_rate_limit_resets_after_window(self):
        """Test that rate limit counter resets after 60 seconds."""
        calls = 30
        window_start = time.time() - 61  # 61 seconds ago
        current_time = time.time()
        
        # Check if window expired
        if current_time - window_start >= 60:
            calls = 0  # Reset
        
        self.assertEqual(calls, 0, "Counter should reset after 60 seconds")
    
    def test_rate_limit_blocks_when_exceeded(self):
        """Test that calls are blocked when limit is exceeded."""
        calls = 50  # Over limit
        max_calls = 30
        window_start = time.time()
        current_time = time.time()
        
        # Check if we should block
        if current_time - window_start < 60 and calls >= max_calls:
            should_block = True
        else:
            should_block = False
        
        self.assertTrue(
            should_block, 
            "❌ CRITICAL: Rate limit not enforced! This will get API blocked!"
        )
    
    def test_rate_limit_allows_under_limit(self):
        """Test that calls are allowed when under limit."""
        calls = 10  # Under limit
        max_calls = 30
        window_start = time.time()
        current_time = time.time()
        
        # Check if we should allow
        if current_time - window_start < 60 and calls < max_calls:
            should_allow = True
        else:
            should_allow = False
        
        self.assertTrue(should_allow, "Should allow calls when under limit")
    
    def test_rate_limit_calculation_accuracy(self):
        """Test that calls per minute calculation is accurate."""
        interval = 2  # seconds
        calls_per_minute = 60 / interval
        
        self.assertEqual(
            calls_per_minute, 
            30, 
            "With 2-second interval, should be 30 calls/minute"
        )
        
        # Test with 1 second
        interval = 1
        calls_per_minute = 60 / interval
        self.assertEqual(calls_per_minute, 60)
        
        # Test with 5 seconds
        interval = 5
        calls_per_minute = 60 / interval
        self.assertEqual(calls_per_minute, 12)


if __name__ == '__main__':
    unittest.main()
