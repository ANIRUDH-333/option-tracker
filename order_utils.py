"""
Utility functions for processing and filtering orders.
"""
from collections import defaultdict
from datetime import datetime, timedelta


def filter_and_aggregate_orders(orders_data):
    """
    Filter orders to show only completed orders and aggregate by Trading Symbol and Transaction Type.
    For each unique (symbol, transaction_type) pair:
    - Accumulate total quantity
    - Take the highest price
    - Keep only one aggregated entry
    
    Args:
        orders_data: List of order dictionaries from orderBook API
        
    Returns:
        List of aggregated order dictionaries
    """
    # Dictionary to store aggregated data: key = (symbol, transaction_type)
    aggregated = defaultdict(lambda: {
        'total_quantity': 0,
        'max_price': 0,
        'order_ids': [],
        'status': None,
        'symbol': None,
        'transaction_type': None
    })
    
    for order in orders_data:
        symbol = order.get('tradingsymbol', '')
        transaction_type = order.get('transactiontype', '')
        status = order.get('status', '')
        
        # Only process completed option orders
        if (status != 'rejected') and (status != 'cancelled') and ('CE' in symbol or 'PE' in symbol):
            key = (symbol, transaction_type)
            
            # Accumulate quantity
            quantity = float(order.get('quantity', 0))
            aggregated[key]['total_quantity'] += quantity
            
            # Track highest price
            price = float(order.get('price', 0))
            if price > aggregated[key]['max_price']:
                aggregated[key]['max_price'] = price
            
            # Store metadata
            aggregated[key]['order_ids'].append(order.get('orderid'))
            aggregated[key]['status'] = status
            aggregated[key]['symbol'] = symbol
            aggregated[key]['transaction_type'] = transaction_type
    
    # Convert to list of dictionaries
    result = []
    for (symbol, trans_type), data in aggregated.items():
        result.append({
            'tradingsymbol': data['symbol'],
            'transactiontype': data['transaction_type'],
            'total_quantity': data['total_quantity'],
            'highest_price': data['max_price'],
            'order_count': len(data['order_ids']),
            'order_ids': data['order_ids'],
            'status': data['status']
        })
    
    # Sort by symbol and transaction type for consistent output
    result.sort(key=lambda x: (x['tradingsymbol'], x['transactiontype']))
    
    return result


def is_option_order(symbol):
    """
    Check if a trading symbol represents an option order.
    
    Args:
        symbol: Trading symbol string
        
    Returns:
        bool: True if it's an option order (contains CE or PE)
    """
    return 'CE' in symbol or 'PE' in symbol


def filter_trades_by_date(trades, target_date):
    """
    Filter trades by a specific date.
    
    Args:
        trades: List of trade dictionaries
        target_date: datetime.date object
        
    Returns:
        List of trades matching the target date
    """
    filtered_trades = []
    
    for trade in trades:
        # Trade time is typically in ISO 8601 or timestamp format
        trade_date_str = trade.get('tradeDate') or trade.get('date') or trade.get('time')
        if not trade_date_str:
            continue
        
        try:
            # Parse trade_date_str to date object
            trade_date = datetime.strptime(trade_date_str.split(" ")[0], '%Y-%m-%d').date()
            
            if trade_date == target_date:
                filtered_trades.append(trade)
        except ValueError as e:
            print(f"Error parsing date '{trade_date_str}': {e}")
            continue
    
    return filtered_trades
