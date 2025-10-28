"""
Display functions for formatting and printing order/trade information.
"""
from datetime import datetime


def display_option_order(order):
    """
    Display a single order in formatted output (like Angel One dashboard).
    
    Args:
        order: Order dictionary from orderBook API
    """
    print(f"{'='*100}")
    print(f"Order ID: {order.get('orderid', 'N/A')}")
    print(f"Trading Symbol: {order.get('tradingsymbol', 'N/A')}")
    print(f"Exchange: {order.get('exchange', 'N/A')}")
    print(f"Product Type: {order.get('producttype', 'N/A')}")
    print(f"Transaction Type: {order.get('transactiontype', 'N/A')}")
    print(f"Order Type: {order.get('ordertype', 'N/A')}")
    print(f"Status: {order.get('status', 'N/A')}")
    print(f"Price: ₹{order.get('price', 0)}")
    print(f"Trigger Price: ₹{order.get('triggerprice', 0)}")
    print(f"Quantity: {order.get('quantity', 0)}")
    print(f"Filled Quantity: {order.get('filledshares', 0)}")
    print(f"Pending Quantity: {order.get('unfilledshares', 0)}")
    print(f"Average Price: ₹{order.get('averageprice', 0)}")
    print(f"Order Time: {order.get('ordertagtime', 'N/A') or order.get('updatetime', 'N/A')}")
    print(f"Variety: {order.get('variety', 'N/A')}")
    print(f"Duration: {order.get('duration', 'N/A')}")
    
    # Show any rejection or cancellation reason if available
    if order.get('text'):
        print(f"Message: {order.get('text')}")
    
    print(f"{'='*100}\n")


def display_aggregated_orders(aggregated_orders):
    """
    Display aggregated orders in formatted output.
    
    Args:
        aggregated_orders: List of aggregated order dictionaries
    """
    print(f"\n{'='*80}")
    print(f"AGGREGATED OPTION ORDERS - {datetime.now()}")
    print(f"{'='*80}\n")
    
    if aggregated_orders:
        for agg_order in aggregated_orders:
            print(f"Trading Symbol: {agg_order['tradingsymbol']}")
            print(f"Transaction Type: {agg_order['transactiontype']}")
            print(f"Total Quantity: {agg_order['total_quantity']:.0f}")
            print(f"Highest Price: {agg_order['highest_price']:.2f}")
            print(f"Number of Orders: {agg_order['order_count']}")
            print(f"Status: {agg_order['status']}")
            print(f"{'-'*80}\n")
    else:
        print("No completed option orders found.")


def display_trades(trades, date_str):
    """
    Display trades for a specific date.
    
    Args:
        trades: List of trade dictionaries
        date_str: String representation of the date
    """
    print(f"\nTrading History for {date_str}:")
    
    if trades:
        for trade in trades:
            print(trade)
    else:
        print(f"No trades found for {date_str}")
