# 🚀 Multi-Account Copy Trading System

A separate, production-ready copy trading system for Angel One accounts that monitors one master account and automatically executes trades in multiple follower accounts.

## ⚡ Quick Links

- **[5-Minute Quick Start](QUICK_START_COPY_TRADING.md)** - Get started immediately
- **[Full Documentation](MULTI_ACCOUNT_COPY_TRADING.md)** - Complete guide
- **Setup Validator** - Run `python validate_setup.py`

## 🎯 What Does This Do?

1. **Monitors** your master Angel One account for new orders
2. **Detects** when you place an order (buy/sell)
3. **Copies** that order to multiple follower accounts automatically
4. **Logs** everything for review and troubleshooting

## 🛡️ Safety First

✅ **DRY RUN MODE** - Test without placing real orders  
✅ **Comprehensive Testing** - Unit tests included  
✅ **Manual Confirmation** - Optional approval before each trade  
✅ **Detailed Logging** - Track every copy attempt  
✅ **Rate Limit Handling** - Automatic retry logic  

## 📦 What's Included

```
multi_account_config.py              # Account configuration manager
multi_account_client.py              # Multi-client manager
multi_account_copy_trader.py         # Core copy trading logic
run_multi_account_copy_trading.py    # Main entry point
validate_setup.py                    # Setup validator
tests/test_multi_account_copy_trading.py  # Unit tests

MULTI_ACCOUNT_COPY_TRADING.md        # Full documentation
QUICK_START_COPY_TRADING.md          # Quick start guide
```

## 🚀 Get Started in 3 Steps

### 1️⃣ Update .env File

```bash
# Your existing master account
API_KEY=master_api_key
CLIENT_ID=master_client_id
PASSWORD=master_password
TOTP_SECRET=master_totp_secret
SECRET_KEY=master_secret_key

# Add follower account(s)
FOLLOWER_1_API_KEY=follower1_api_key
FOLLOWER_1_CLIENT_ID=follower1_client_id
FOLLOWER_1_PASSWORD=follower1_password
FOLLOWER_1_TOTP_SECRET=follower1_totp_secret
FOLLOWER_1_SECRET_KEY=follower1_secret_key
```

### 2️⃣ Validate Setup

```bash
python validate_setup.py
```

Should show: ✅ ALL CHECKS PASSED!

### 3️⃣ Start Copy Trading (Dry Run)

```bash
python run_multi_account_copy_trading.py
```

Place a test order in master account and watch it get detected!

## 🎓 Features

### Core Features
- ✅ Monitor one master account
- ✅ Copy to unlimited follower accounts
- ✅ Support all order types (Market, Limit, Stop Loss)
- ✅ Real-time order detection (3-second polling)
- ✅ Configurable quantity management
- ✅ Symbol filtering (whitelist/blacklist)

### Quantity Options
- **Mirror Mode** - Same quantity as master
- **Fixed Mode** - Always trade fixed quantity
- **Multiplier Mode** - Percentage of master quantity

### Safety Features
- **Dry Run Mode** - Test without placing orders
- **Manual Confirmation** - Approve each trade
- **Order Filtering** - By symbol, order type
- **Comprehensive Logging** - JSON logs of all actions
- **Error Handling** - Graceful failure handling

## 📊 Example Output

```
🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 
NEW ORDER DETECTED AT 2025-01-15 10:30:45

📊 Master Account Order Details:
   Symbol: NIFTY23FEB18000CE
   Type: BUY MARKET
   Quantity: 50
   Price: 0
   Status: complete

✅ Order approved for copying

📤 Copying to 2 follower account(s)...

   ✅ Follower1: Success! Order ID: 987654321
   ✅ Follower2: Success! Order ID: 987654322
```

## 🧪 Testing Workflow

1. ✅ **Validate Setup** - `python validate_setup.py`
2. ✅ **Run Unit Tests** - `cd tests && python test_multi_account_copy_trading.py`
3. ✅ **Dry Run Testing** - Start with `dry_run=True`
4. ✅ **Small Live Test** - One follower, small quantity
5. ✅ **Full Deployment** - All followers, normal quantities

## ⚙️ Configuration Examples

### Mirror Trading (Same Quantity)
```python
settings.copy_all_orders = True
settings.quantity_multiplier = 1.0
```

### Proportional Trading (50%)
```python
settings.copy_all_orders = True
settings.quantity_multiplier = 0.5
```

### Fixed Quantity
```python
settings.use_fixed_quantity = True
settings.fixed_quantity = 25
```

### Symbol Filtering
```python
# Only copy these symbols
settings.allowed_symbols = ['NIFTY', 'BANKNIFTY']

# Never copy these symbols
settings.blocked_symbols = ['FINNIFTY']
```

## 📝 Logs

All copy attempts are logged to:
```
logs/copy_trading_YYYYMMDD_HHMMSS.json
```

Example log entry:
```json
{
  "timestamp": "2025-01-15T10:30:45",
  "master_order_id": "123456789",
  "symbol": "NIFTY23FEB18000CE",
  "transaction_type": "BUY",
  "quantity": "50",
  "follower": "Follower1",
  "success": true,
  "follower_order_id": "987654321"
}
```

## 🔒 Security

- ✅ Credentials stored in `.env` file (not committed to git)
- ✅ Sensitive data never logged
- ✅ Each account uses separate API keys
- ✅ No sharing of credentials between accounts

## ⚠️ Important Notes

1. **Separate System** - Does NOT interfere with existing code
2. **Test First** - Always test in dry run mode
3. **Monitor Closely** - Watch first few trades
4. **Rate Limits** - Respect Angel One API limits
5. **Manual Control** - You can stop anytime (Ctrl+C)

## 🚨 Emergency Stop

Press `Ctrl+C` to stop immediately. System will:
- Stop monitoring
- Show session summary
- Save all logs
- Exit cleanly

## 📚 Documentation

- **[Quick Start Guide](QUICK_START_COPY_TRADING.md)** - 5-minute setup
- **[Full Documentation](MULTI_ACCOUNT_COPY_TRADING.md)** - Complete guide
- **[Unit Tests](tests/test_multi_account_copy_trading.py)** - Test suite

## 🛠️ Troubleshooting

### Problem: "Rate limit exceeded"
**Solution:** Wait 5-10 minutes before restarting

### Problem: "No follower accounts"
**Solution:** Add `FOLLOWER_1_*` credentials to `.env`

### Problem: Orders not detected
**Solution:** Ensure orders are "complete" status, check polling interval

### Problem: Configuration errors
**Solution:** Run `python validate_setup.py`

## 🎯 Best Practices

1. **Start Small** - Test with one follower first
2. **Use Dry Run** - Always test new configurations
3. **Monitor Logs** - Review logs regularly
4. **Handle Failures** - Check failed_copies in logs
5. **Scale Gradually** - Add followers slowly

## 📞 Support

If you encounter issues:
1. Run `python validate_setup.py`
2. Check console error messages
3. Review log files in `logs/`
4. Verify `.env` configuration
5. Run unit tests

## ✅ Pre-Flight Checklist

Before going live:
- [ ] Validated setup (green checkmarks)
- [ ] All unit tests pass
- [ ] Tested in dry run mode
- [ ] Placed test order successfully
- [ ] Verified in Angel One app
- [ ] Understand how to stop system
- [ ] Know where logs are saved

## 🎉 Success Criteria

Your system is working when:
- ✅ Orders detected within 5 seconds
- ✅ 95%+ copy success rate
- ✅ All followers execute orders
- ✅ Logs show no errors

## 🔄 Updates and Maintenance

This is a standalone system that:
- ✅ Doesn't modify your existing code
- ✅ Can be tested independently
- ✅ Can be integrated later if desired
- ✅ Updates don't affect main system

## 📈 Scaling

To add more follower accounts:
1. Add `FOLLOWER_N_*` credentials to `.env`
2. Restart the system
3. Verify new accounts in logs
4. Test with small order

No code changes needed!

## 🌟 Features Coming Soon

- WebSocket support for instant detection
- Account-specific quantity rules
- Time-based filtering
- Symbol-specific followers
- Advanced risk management

---

**Ready to start?** Run `python validate_setup.py` now! 🚀

For detailed instructions, see [QUICK_START_COPY_TRADING.md](QUICK_START_COPY_TRADING.md)
