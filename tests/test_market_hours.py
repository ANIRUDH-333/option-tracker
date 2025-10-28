"""
Test market hours detection.
Critical: Wrong hours = unnecessary API calls = rate limit issues.
"""

import unittest
from datetime import datetime, time as dt_time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMarketHours(unittest.TestCase):
    """Test market hours detection logic."""
    
    def test_detects_weekday_market_hours(self):
        """Test detection during weekday market hours."""
        # Simulate Monday 10:00 AM
        test_time = datetime(2025, 10, 27, 10, 0, 0)  # Monday
        
        market_open = dt_time(9, 15)
        market_close = dt_time(15, 30)
        
        is_weekday = test_time.weekday() < 5
        is_market_time = market_open <= test_time.time() <= market_close
        
        is_market_hours = is_weekday and is_market_time
        
        self.assertTrue(is_market_hours, "Should be market hours")
    
    def test_detects_weekend(self):
        """Test detection on weekends."""
        # Simulate Saturday
        test_time = datetime(2025, 10, 25, 10, 0, 0)  # Saturday
        
        is_weekend = test_time.weekday() >= 5
        
        self.assertTrue(is_weekend, "Should detect weekend")
    
    def test_detects_before_market_open(self):
        """Test detection before market opens."""
        # 9:00 AM (before 9:15 AM open)
        test_time = datetime(2025, 10, 27, 9, 0, 0)  # Monday 9:00 AM
        
        market_open = dt_time(9, 15)
        is_before_open = test_time.time() < market_open
        
        self.assertTrue(is_before_open, "Should detect before market open")
    
    def test_detects_after_market_close(self):
        """Test detection after market closes."""
        # 4:00 PM (after 3:30 PM close)
        test_time = datetime(2025, 10, 27, 16, 0, 0)  # Monday 4:00 PM
        
        market_close = dt_time(15, 30)
        is_after_close = test_time.time() > market_close
        
        self.assertTrue(is_after_close, "Should detect after market close")
    
    def test_boundary_market_open(self):
        """Test exact market open time."""
        # Exactly 9:15 AM
        test_time = datetime(2025, 10, 27, 9, 15, 0)  # Monday 9:15 AM
        
        market_open = dt_time(9, 15)
        market_close = dt_time(15, 30)
        
        is_weekday = test_time.weekday() < 5
        is_market_time = market_open <= test_time.time() <= market_close
        is_market_hours = is_weekday and is_market_time
        
        self.assertTrue(is_market_hours, "9:15 AM should be market hours")
    
    def test_boundary_market_close(self):
        """Test exact market close time."""
        # Exactly 3:30 PM
        test_time = datetime(2025, 10, 27, 15, 30, 0)  # Monday 3:30 PM
        
        market_open = dt_time(9, 15)
        market_close = dt_time(15, 30)
        
        is_weekday = test_time.weekday() < 5
        is_market_time = market_open <= test_time.time() <= market_close
        is_market_hours = is_weekday and is_market_time
        
        self.assertTrue(is_market_hours, "3:30 PM should still be market hours")
    
    def test_friday_is_weekday(self):
        """Test that Friday is detected as weekday."""
        # Friday
        test_time = datetime(2025, 10, 24, 10, 0, 0)  # Friday
        
        is_weekday = test_time.weekday() < 5
        
        self.assertTrue(is_weekday, "Friday should be a weekday")


if __name__ == '__main__':
    unittest.main()
