"""
Order monitoring functions for checking and displaying orders.
"""
from datetime import datetime, timedelta
from order_utils import filter_and_aggregate_orders, is_option_order, filter_trades_by_date
from display import display_option_order, display_aggregated_orders, display_trades


def check_option_orders(client):
    """
    Check and display all option orders in the order book.
    
    Args:
        client: SmartAPIClient instance
    """
    try:
        order_book = client.get_order_book()
        if order_book is not None and 'data' in order_book and order_book['data'] is not None:
            print(f"\n{'='*100}")
            print(f"ALL ORDERS - {datetime.now()}")
            print(f"{'='*100}\n")
            print(f"Total orders: {len(order_book['data'])}\n")
            
            for order in order_book['data']:
                symbol = order.get('tradingsymbol', '')
                # Display all orders (not just options, if you want all)
                # Change the condition below to display only specific types
                display_option_order(order)
        else:
            print(f"[{datetime.now()}] No order data returned or empty order book.")
    except Exception as e:
        print(f"Error while fetching order book: {e}")


def check_and_display_aggregated_orders(client):
    """
    Fetch orders and display aggregated view by symbol and transaction type.
    
    Args:
        client: SmartAPIClient instance
    """
    try:
        order_book = client.get_order_book()
        if order_book is not None and 'data' in order_book and order_book['data'] is not None:
            # Get aggregated orders
            aggregated_orders = filter_and_aggregate_orders(order_book['data'])
            display_aggregated_orders(aggregated_orders)
        else:
            print(f"[{datetime.now()}] No order data returned or empty order book.")
    except Exception as e:
        print(f"Error while fetching order book: {e}")


def get_trading_history_for_date(client, days_ago=2):
    """
    Get trading history for a specific date.
    
    Args:
        client: SmartAPIClient instance
        days_ago: Number of days ago to check (default: 2)
    """
    try:
        target_date = (datetime.now() - timedelta(days=days_ago)).date()
        response = client.get_trade_book()
        
        if response and 'data' in response and response['data']:
            filtered_trades = filter_trades_by_date(response['data'], target_date)
            display_trades(filtered_trades, str(target_date))
        else:
            print(f"No trading history data returned from API.")
    except Exception as e:
        print(f"Error fetching trading history: {e}")
