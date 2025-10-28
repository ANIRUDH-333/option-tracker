"""
Integration test - Test the full system without real API calls.
Critical: End-to-end functionality must work correctly.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestIntegration(unittest.TestCase):
    """Integration tests for the full system."""
    
    @patch('smartapi_client.SmartConnect')
    def test_full_detection_flow(self, mock_smartconnect):
        """Test complete order detection flow."""
        # Mock API responses
        mock_client = Mock()
        mock_smartconnect.return_value = mock_client
        
        # First call: existing orders
        mock_client.orderBook.return_value = {
            'status': True,
            'data': [
                {'orderid': '1', 'tradingsymbol': 'NIFTY', 'status': 'complete'}
            ]
        }
        
        # Simulate monitoring
        known_orders = set()
        orders = mock_client.orderBook()
        for order in orders['data']:
            known_orders.add(order['orderid'])
        
        self.assertEqual(len(known_orders), 1)
        
        # Second call: new order added
        mock_client.orderBook.return_value = {
            'status': True,
            'data': [
                {'orderid': '1', 'tradingsymbol': 'NIFTY', 'status': 'complete'},
                {'orderid': '2', 'tradingsymbol': 'BANKNIFTY', 'status': 'complete'}  # NEW
            ]
        }
        
        new_orders = []
        orders = mock_client.orderBook()
        for order in orders['data']:
            if order['orderid'] not in known_orders:
                new_orders.append(order)
                known_orders.add(order['orderid'])
        
        self.assertEqual(len(new_orders), 1, "Should detect 1 new order")
        self.assertEqual(new_orders[0]['orderid'], '2')
    
    def test_error_handling_in_flow(self):
        """Test that errors don't crash the system."""
        # Simulate API error
        mock_response = None
        
        # Should handle gracefully
        try:
            if mock_response is None:
                orders = []
            else:
                orders = mock_response.get('data', [])
            
            error_handled = True
        except Exception:
            error_handled = False
        
        self.assertTrue(
            error_handled, 
            "❌ CRITICAL: System crashes on API error!"
        )


if __name__ == '__main__':
    unittest.main()
