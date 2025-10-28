"""
SmartAPI Order Monitor - Main Entry Point

This script monitors option orders from SmartAPI and displays them in an aggregated view.
"""
import time
from smartapi_client import SmartAPIClient
from order_monitor import (
    check_option_orders,
    check_and_display_aggregated_orders,
    get_trading_history_for_date
)
from config import Config


def main():
    """Main function to run the order monitor."""
    try:
        # Initialize SmartAPI client
        client = SmartAPIClient()
        
        # Choose which monitoring function to run:
        
        # Option 1: Show detailed view of individual option orders (like Angel One dashboard)
        check_option_orders(client)
        
        # Option 2: Show aggregated view by symbol and transaction type
        # check_and_display_aggregated_orders(client)
        
        # Option 3: Get trading history for a specific date (e.g., 2 days ago)
        # get_trading_history_for_date(client, days_ago=2)
        
    except Exception as e:
        print(f"Error in main execution: {e}")


def run_continuous_monitoring():
    """Run continuous monitoring with polling interval."""
    try:
        client = SmartAPIClient()
        
        print(f"Starting continuous monitoring (polling every {Config.POLL_INTERVAL_SECONDS} seconds)")
        print("Press Ctrl+C to stop\n")
        
        while True:
            check_and_display_aggregated_orders(client)
            time.sleep(Config.POLL_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except Exception as e:
        print(f"Error in continuous monitoring: {e}")


if __name__ == "__main__":
    # Run once
    main()
    
    # Or run continuous monitoring (uncomment below and comment out main() above)
    # run_continuous_monitoring()