# Multi-Account Copy Trading System

## Overview

This is a **separate** copy trading system that monitors one master Angel One account and automatically executes trades in multiple follower Angel One accounts. It is designed to work independently of your existing code and can be thoroughly tested before integration.

## Features

✨ **Core Features:**
- Monitor one master account in real-time
- Copy trades to multiple follower accounts automatically
- Support for all order types (Market, Limit, Stop Loss)
- Configurable quantity management (fixed, multiplier, or mirror)
- Symbol filtering (whitelist/blacklist)
- Dry run mode for safe testing

🛡️ **Safety Features:**
- Dry run mode (simulate without placing orders)
- Confirmation prompts before placing orders
- Order filtering by symbol and type
- Comprehensive logging of all actions
- Rate limit handling for multiple account initializations
- Failed order tracking for review

📊 **Monitoring & Reporting:**
- Real-time order detection and copying
- Detailed copy trading statistics
- JSON logs of all copy attempts
- Success/failure tracking per follower

## File Structure

```
multi_account_config.py              # Configuration for multiple accounts
multi_account_client.py              # Client manager for multiple SmartAPI instances
multi_account_copy_trader.py         # Main copy trading logic
run_multi_account_copy_trading.py    # Entry point to start copy trading
tests/test_multi_account_copy_trading.py  # Unit tests
MULTI_ACCOUNT_COPY_TRADING.md        # This documentation
```

## Setup

### 1. Update Your .env File

Add credentials for your follower accounts to your `.env` file:

```bash
# Master Account (already exists)
API_KEY=your_master_api_key
CLIENT_ID=your_master_client_id
PASSWORD=your_master_password
TOTP_SECRET=your_master_totp_secret
SECRET_KEY=your_master_secret_key

# Follower Account 1
FOLLOWER_1_API_KEY=follower1_api_key
FOLLOWER_1_CLIENT_ID=follower1_client_id
FOLLOWER_1_PASSWORD=follower1_password
FOLLOWER_1_TOTP_SECRET=follower1_totp_secret
FOLLOWER_1_SECRET_KEY=follower1_secret_key

# Follower Account 2
FOLLOWER_2_API_KEY=follower2_api_key
FOLLOWER_2_CLIENT_ID=follower2_client_id
FOLLOWER_2_PASSWORD=follower2_password
FOLLOWER_2_TOTP_SECRET=follower2_totp_secret
FOLLOWER_2_SECRET_KEY=follower2_secret_key

# Add more follower accounts as needed (FOLLOWER_3_, FOLLOWER_4_, etc.)
```

### 2. Run Unit Tests

Before using with real accounts, run the test suite:

```bash
cd tests
python test_multi_account_copy_trading.py
```

All tests should pass before proceeding.

### 3. Test Configuration

Verify your configuration is loaded correctly:

```bash
python run_multi_account_copy_trading.py
# Edit the file and uncomment test_configuration_only() to test config only
```

## Usage

### Basic Usage (Dry Run Mode - RECOMMENDED for testing)

```bash
python run_multi_account_copy_trading.py
```

By default, the system starts in **DRY RUN MODE**, which means:
- ✅ Monitors master account for orders
- ✅ Detects new orders
- ✅ Shows what would be copied
- ❌ Does NOT place any orders in follower accounts

This is perfect for testing the system safely!

### Customizing Settings

Edit `run_multi_account_copy_trading.py` and modify the settings:

```python
def main():
    # Configure settings
    settings = CopyTradingSettings()
    
    # IMPORTANT: Set to False to enable real trading
    settings.dry_run = True  # Change to False for live trading
    
    # Order filtering
    settings.copy_all_orders = True  # Copy all symbols
    # OR filter specific symbols:
    # settings.copy_all_orders = False
    # settings.allowed_symbols = ['NIFTY', 'BANKNIFTY']  # Only these
    # settings.blocked_symbols = ['FINNIFTY']  # Never these
    
    # Quantity management
    settings.use_fixed_quantity = False  # Mirror master quantity
    # OR use fixed quantity:
    # settings.use_fixed_quantity = True
    # settings.fixed_quantity = 50
    # OR use a multiplier:
    # settings.quantity_multiplier = 0.5  # 50% of master quantity
    
    # Order type filtering
    settings.copy_market_orders = True
    settings.copy_limit_orders = True
    settings.copy_stop_orders = True
    
    # Safety
    settings.require_confirmation = False  # Ask before each trade
    settings.log_all_actions = True
```

### Live Trading Mode

⚠️ **CAUTION: Use only after thorough testing in dry run mode!**

To enable live trading:

1. Edit `run_multi_account_copy_trading.py`
2. Change `settings.dry_run = False`
3. Run the script
4. Confirm when prompted

```bash
python run_multi_account_copy_trading.py
```

The system will ask for confirmation before starting:
```
🔴 LIVE MODE: Orders WILL BE PLACED in follower accounts!
   Type 'YES' to confirm and continue: YES
```

## Testing Strategy

### Phase 1: Configuration Testing
1. ✅ Run unit tests
2. ✅ Verify configuration loads correctly
3. ✅ Check all accounts are detected

### Phase 2: Dry Run Testing
1. ✅ Start in dry run mode
2. ✅ Place test orders in master account
3. ✅ Verify detection and display is correct
4. ✅ Check order parameters would be correct
5. ✅ Test different order types (Market, Limit, Stop)

### Phase 3: Small Scale Live Testing
1. ✅ Enable live mode with ONE follower account only
2. ✅ Place a small test order in master account
3. ✅ Verify it copies correctly to follower
4. ✅ Check order execution and fills
5. ✅ Review logs for any issues

### Phase 4: Full Scale Testing
1. ✅ Enable all follower accounts
2. ✅ Start with small quantities
3. ✅ Monitor closely for first few orders
4. ✅ Gradually increase to normal quantities

### Phase 5: Production Use
1. ✅ Run continuously during trading hours
2. ✅ Monitor logs regularly
3. ✅ Review copy statistics
4. ✅ Handle any failures promptly

## Monitoring and Logs

### Real-Time Console Output

The system provides detailed real-time output:

```
🔔 🔔 🔔 ... 🔔 🔔 🔔
NEW ORDER DETECTED AT 2025-01-15 10:30:45
🔔 🔔 🔔 ... 🔔 🔔 🔔

📊 Master Account Order Details:
   Symbol: NIFTY23FEB18000CE
   Type: BUY MARKET
   Quantity: 50
   Price: 0
   Product: INTRADAY
   Exchange: NFO
   Status: complete
   Order ID: 123456789

✅ Order approved for copying: Order passes all filters

📤 Copying to 2 follower account(s)...

   📤 Follower1: Placing order...
   ✅ Follower1: Success! Order ID: 987654321
   📤 Follower2: Placing order...
   ✅ Follower2: Success! Order ID: 987654322
```

### Log Files

Copy records are saved to `logs/copy_trading_YYYYMMDD_HHMMSS.json`:

```json
{
  "records": [
    {
      "timestamp": "2025-01-15T10:30:45",
      "master_order_id": "123456789",
      "symbol": "NIFTY23FEB18000CE",
      "transaction_type": "BUY",
      "quantity": "50",
      "price": "0",
      "follower": "Follower1",
      "success": true,
      "follower_order_id": "987654321",
      "error": null
    }
  ],
  "statistics": {
    "total_copies": 2,
    "successful": 2,
    "failed": 0,
    "success_rate": 100.0
  }
}
```

## Common Scenarios

### Scenario 1: Copy All Orders with Same Quantity
```python
settings.copy_all_orders = True
settings.quantity_multiplier = 1.0
```

### Scenario 2: Copy Only NIFTY with 50% Quantity
```python
settings.copy_all_orders = False
settings.allowed_symbols = ['NIFTY']
settings.quantity_multiplier = 0.5
```

### Scenario 3: Fixed Quantity for All Followers
```python
settings.use_fixed_quantity = True
settings.fixed_quantity = 25
```

### Scenario 4: Block Certain Symbols
```python
settings.blocked_symbols = ['FINNIFTY', 'MIDCPNIFTY']
```

### Scenario 5: Require Manual Confirmation
```python
settings.require_confirmation = True
# System will ask: "Copy this order to N followers? (yes/no)"
```

## Rate Limits and Best Practices

### Angel One Rate Limits
- **Session Creation:** 3-5 per minute per account
- **Order Placement:** ~100 per minute per account
- **Order Book Fetch:** ~20 per minute per account

### Best Practices

1. **Initialization Delays:** The system automatically adds 5-second delays between account initializations

2. **Polling Interval:** Default is 3 seconds. Don't make it too aggressive:
   ```python
   copy_trader.start_monitoring(interval=3)  # 3 seconds is good
   ```

3. **Handle Rate Limits:** If you hit rate limits:
   - Wait 5-10 minutes
   - Increase polling interval
   - Reduce number of simultaneous follower accounts

4. **Error Handling:** Failed copies are logged but don't stop the system

## Troubleshooting

### Issue: "Rate limit exceeded"
**Solution:** 
- Wait 5-10 minutes before restarting
- Don't restart the script multiple times quickly
- System has built-in retry logic with exponential backoff

### Issue: "Master account not configured"
**Solution:**
- Check your `.env` file has all master account credentials
- Run `test_configuration_only()` to diagnose

### Issue: "No follower accounts configured"
**Solution:**
- Add follower credentials to `.env` with FOLLOWER_1_, FOLLOWER_2_ prefix
- Check environment variables are loaded: `python -c "import os; print(os.getenv('FOLLOWER_1_API_KEY'))"`

### Issue: Orders detected but not copied
**Solution:**
- Check if `settings.dry_run = True` (dry run mode)
- Check order filters (symbols, order types)
- Review console output for skip reasons

### Issue: Some followers fail to initialize
**Solution:**
- Check credentials for those accounts
- Rate limits may have been hit - wait and retry
- Check if those accounts are active

## Integration with Existing Code

This system is **completely separate** from your existing code and won't interfere with it. However, when you're ready to integrate:

### Option 1: Keep Separate (Recommended)
- Run `run_multi_account_copy_trading.py` in a separate terminal
- Keep your existing monitoring scripts unchanged
- Easiest and safest approach

### Option 2: Partial Integration
- Use the multi-account client manager in your existing code
- Import only the parts you need:
  ```python
  from multi_account_config import MultiAccountConfig
  from multi_account_client import ClientManager
  ```

### Option 3: Full Integration
- After thorough testing, merge the copy trading logic into your existing `copy_trading.py`
- Replace the single target client with the client manager
- Carefully test all existing functionality

## Security Notes

⚠️ **Important Security Considerations:**

1. **Credentials Storage:** 
   - Keep `.env` file secure and never commit to git
   - Add `.env` to `.gitignore`
   - Consider using environment variables in production

2. **API Keys:**
   - Each account needs its own API key from Angel One
   - Don't share API keys between accounts
   - Rotate keys periodically

3. **Monitoring:**
   - Always monitor the first few trades closely
   - Review logs regularly
   - Set up alerts for failures

## FAQ

**Q: Can I use this with non-Angel One accounts?**
A: Currently only Angel One is supported, but the architecture allows for adding other brokers.

**Q: How many follower accounts can I have?**
A: Technically unlimited, but be mindful of rate limits. Start with 2-3 and scale up.

**Q: What happens if master order fails?**
A: The order is not copied to followers (only completed orders are copied).

**Q: What happens if a follower order fails?**
A: It's logged but doesn't stop other followers. Check logs for failed orders.

**Q: Can I have different quantities for different followers?**
A: Currently not directly, but you can modify `calculate_follower_quantity()` in the code.

**Q: Does this work with WebSocket?**
A: Currently uses polling. WebSocket support can be added later.

**Q: Can I test without follower accounts?**
A: Yes! Run in dry run mode with master account only. It will show what would be copied.

## Support and Updates

For issues or questions:
1. Check the logs in `logs/` directory
2. Review console output for error messages
3. Run unit tests to verify system integrity
4. Test in dry run mode first

## Summary

This multi-account copy trading system provides a safe, tested way to copy trades from one master account to multiple follower accounts. Start with dry run testing, move to small scale live testing, and gradually scale up to production use.

🚀 Happy Trading!
