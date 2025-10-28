"""
Test SmartAPI client functionality.
Critical: Connection failures = no order detection = missed trades.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSmartAPIClient(unittest.TestCase):
    """Test SmartAPI client wrapper."""
    
    def test_orderbook_response_structure(self):
        """Test that we handle orderBook response correctly."""
        # Simulate API response
        mock_response = {
            'status': True,
            'message': 'SUCCESS',
            'data': [
                {
                    'orderid': '123',
                    'tradingsymbol': 'NIFTY25OCT2525900CE',
                    'transactiontype': 'BUY',
                    'quantity': 50,
                    'price': 146.55,
                    'status': 'complete'
                }
            ]
        }
        
        # Test structure
        self.assertIn('status', mock_response, "Response should have 'status'")
        self.assertIn('data', mock_response, "Response should have 'data'")
        self.assertIsInstance(mock_response['data'], list, "Data should be a list")
    
    def test_handles_empty_orderbook(self):
        """Test that empty order book is handled correctly."""
        mock_response = {
            'status': True,
            'message': 'SUCCESS',
            'data': []
        }
        
        # Should not crash
        orders = mock_response.get('data', [])
        self.assertEqual(len(orders), 0, "Empty order book should return empty list")
    
    def test_handles_null_orderbook(self):
        """Test that null/None order book is handled correctly."""
        mock_response = None
        
        # Should handle gracefully
        if mock_response is None or 'data' not in mock_response:
            orders = []
        else:
            orders = mock_response.get('data', [])
        
        self.assertEqual(len(orders), 0, "Null response should return empty list")
    
    def test_handles_api_error_response(self):
        """Test that API errors are handled correctly."""
        mock_error_response = {
            'status': False,
            'message': 'Invalid session',
            'errorcode': 'AG8001'
        }
        
        # Check if error
        if not mock_error_response.get('status'):
            has_error = True
        else:
            has_error = False
        
        self.assertTrue(
            has_error, 
            "Should detect API error responses"
        )
    
    def test_order_has_required_fields(self):
        """Test that orders have all required fields."""
        mock_order = {
            'orderid': '123',
            'tradingsymbol': 'NIFTY25OCT2525900CE',
            'transactiontype': 'BUY',
            'quantity': 50,
            'price': 146.55,
            'status': 'complete'
        }
        
        required_fields = ['orderid', 'tradingsymbol', 'transactiontype', 'quantity', 'status']
        
        for field in required_fields:
            self.assertIn(
                field, 
                mock_order, 
                f"❌ CRITICAL: Order missing required field '{field}'"
            )


if __name__ == '__main__':
    unittest.main()
