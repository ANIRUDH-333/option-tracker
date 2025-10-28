"""
Multi-Account Copy Trading - Main Entry Point

This script runs copy trading from one master account to multiple follower accounts.
Run this separately from your existing monitoring scripts.
"""
from multi_account_config import MultiAccountConfig
from multi_account_copy_trader import MultiAccountCopyTrader, CopyTradingSettings


def main():
    """Main function to run multi-account copy trading."""
    
    print("\n" + "🚀 " * 40)
    print("MULTI-ACCOUNT COPY TRADING SYSTEM")
    print("🚀 " * 40 + "\n")
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = MultiAccountConfig()
        config.validate()
        config.print_summary()
        
        # Configure copy trading settings
        settings = CopyTradingSettings()
        
        # === CUSTOMIZE YOUR SETTINGS HERE ===
        
        # Dry run mode (RECOMMENDED for testing)
        settings.dry_run = True  # Set to False to actually place orders
        
        # Order filtering
        settings.copy_all_orders = True  # Copy all symbols
        # settings.allowed_symbols = ['NIFTY', 'BANKNIFTY']  # Only these symbols
        # settings.blocked_symbols = ['FINNIFTY']  # Never copy these
        
        # Quantity management
        settings.use_fixed_quantity = False  # Use same quantity as master
        # settings.use_fixed_quantity = True
        # settings.fixed_quantity = 50  # Use fixed quantity for all followers
        # settings.quantity_multiplier = 0.5  # Use 50% of master quantity
        
        # Order type filtering
        settings.copy_market_orders = True
        settings.copy_limit_orders = True
        settings.copy_stop_orders = True
        
        # Safety features
        settings.require_confirmation = False  # Ask before each trade
        settings.log_all_actions = True
        
        # === END CUSTOMIZATION ===
        
        # Display settings
        print("\n⚙️  Copy Trading Settings:")
        print(f"   Dry Run: {'ON ⚠️  (No orders will be placed)' if settings.dry_run else 'OFF (Orders WILL be placed)'}")
        print(f"   Copy All Orders: {settings.copy_all_orders}")
        if settings.use_fixed_quantity:
            print(f"   Quantity Mode: Fixed ({settings.fixed_quantity})")
        else:
            print(f"   Quantity Mode: Follow Master (×{settings.quantity_multiplier})")
        print(f"   Require Confirmation: {settings.require_confirmation}")
        print()
        
        if settings.dry_run:
            print("⚠️  DRY RUN MODE: Orders will be simulated but not actually placed")
            print("   Change settings.dry_run = False to enable real trading\n")
        else:
            print("🔴 LIVE MODE: Orders WILL BE PLACED in follower accounts!")
            response = input("   Type 'YES' to confirm and continue: ")
            if response != 'YES':
                print("\n   ⏹️  Cancelled by user\n")
                return
            print()
        
        # Initialize copy trader
        copy_trader = MultiAccountCopyTrader(config, settings)
        
        # Start monitoring (checks every 3 seconds)
        copy_trader.start_monitoring(interval=3)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopped by user\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


def test_configuration_only():
    """Test configuration loading without starting copy trading."""
    print("\n" + "🧪 " * 40)
    print("CONFIGURATION TEST MODE")
    print("🧪 " * 40 + "\n")
    
    try:
        config = MultiAccountConfig()
        config.validate()
        config.print_summary()
        
        print("✅ Configuration is valid!")
        print("\nTo start copy trading, run: python run_multi_account_copy_trading.py\n")
        
    except Exception as e:
        print(f"\n❌ Configuration error: {e}\n")


def show_example_env():
    """Show example .env configuration."""
    from multi_account_config import ENV_TEMPLATE
    
    print("\n" + "="*100)
    print("EXAMPLE .env CONFIGURATION FOR MULTI-ACCOUNT COPY TRADING")
    print("="*100)
    print(ENV_TEMPLATE)
    print("="*100)
    print("\nSave this to your .env file and update with your actual credentials.")
    print("You can add as many follower accounts as needed (FOLLOWER_3_, FOLLOWER_4_, etc.)\n")


if __name__ == "__main__":
    # Choose what to run:
    
    # Option 1: Run copy trading
    main()
    
    # Option 2: Test configuration only (uncomment to use)
    # test_configuration_only()
    
    # Option 3: Show example .env format (uncomment to use)
    # show_example_env()
