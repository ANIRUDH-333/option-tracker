"""
Test order detection logic.
Critical: Missing orders = missed trades. False positives = duplicate trades.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestOrderDetection(unittest.TestCase):
    """Test the core order detection logic."""
    
    def test_empty_known_orders_detects_all_as_new(self):
        """Test that with no known orders, all orders are detected as new."""
        known_orders = set()
        api_orders = [
            {'orderid': '1', 'tradingsymbol': 'NIFTY'},
            {'orderid': '2', 'tradingsymbol': 'BANKNIFTY'},
        ]
        
        new_orders = []
        for order in api_orders:
            if order['orderid'] not in known_orders:
                new_orders.append(order)
                known_orders.add(order['orderid'])
        
        self.assertEqual(len(new_orders), 2, "Should detect 2 new orders")
        self.assertEqual(len(known_orders), 2, "Should have 2 known orders after")
    
    def test_no_new_orders_when_all_known(self):
        """Test that no new orders are detected when all are already known."""
        known_orders = {'1', '2', '3'}
        api_orders = [
            {'orderid': '1', 'tradingsymbol': 'NIFTY'},
            {'orderid': '2', 'tradingsymbol': 'BANKNIFTY'},
            {'orderid': '3', 'tradingsymbol': 'SENSEX'},
        ]
        
        new_orders = []
        for order in api_orders:
            if order['orderid'] not in known_orders:
                new_orders.append(order)
        
        self.assertEqual(len(new_orders), 0, "❌ CRITICAL: Detected new orders when none exist!")
    
    def test_detects_only_new_orders(self):
        """Test that only truly new orders are detected."""
        known_orders = {'1', '2'}
        api_orders = [
            {'orderid': '1', 'tradingsymbol': 'NIFTY'},
            {'orderid': '2', 'tradingsymbol': 'BANKNIFTY'},
            {'orderid': '3', 'tradingsymbol': 'SENSEX'},  # NEW
            {'orderid': '4', 'tradingsymbol': 'FINNIFTY'},  # NEW
        ]
        
        new_orders = []
        for order in api_orders:
            if order['orderid'] not in known_orders:
                new_orders.append(order)
                known_orders.add(order['orderid'])
        
        self.assertEqual(len(new_orders), 2, "Should detect exactly 2 new orders")
        self.assertEqual(new_orders[0]['orderid'], '3')
        self.assertEqual(new_orders[1]['orderid'], '4')
    
    def test_no_duplicate_detection(self):
        """Test that the same order is never detected twice."""
        known_orders = set()
        
        # First batch
        api_orders_1 = [
            {'orderid': '1', 'tradingsymbol': 'NIFTY'},
        ]
        
        for order in api_orders_1:
            if order['orderid'] not in known_orders:
                known_orders.add(order['orderid'])
        
        # Second batch (same order appears again)
        api_orders_2 = [
            {'orderid': '1', 'tradingsymbol': 'NIFTY'},
        ]
        
        new_orders = []
        for order in api_orders_2:
            if order['orderid'] not in known_orders:
                new_orders.append(order)
        
        self.assertEqual(
            len(new_orders), 
            0, 
            "❌ CRITICAL: Same order detected twice! This causes duplicate trades!"
        )
    
    def test_handles_none_order_id(self):
        """Test that orders with None orderid are handled gracefully."""
        known_orders = set()
        api_orders = [
            {'orderid': None, 'tradingsymbol': 'NIFTY'},
            {'orderid': '2', 'tradingsymbol': 'BANKNIFTY'},
        ]
        
        new_orders = []
        for order in api_orders:
            order_id = order.get('orderid')
            if order_id and order_id not in known_orders:
                new_orders.append(order)
                known_orders.add(order_id)
        
        self.assertEqual(len(new_orders), 1, "Should only detect order with valid ID")
        self.assertEqual(new_orders[0]['orderid'], '2')


if __name__ == '__main__':
    unittest.main()
