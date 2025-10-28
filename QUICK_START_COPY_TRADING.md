# Quick Start Guide - Multi-Account Copy Trading

## ⚡ 5-Minute Quick Start

### Step 1: Update .env File (2 minutes)

Add your follower account credentials to `.env`:

```bash
# Your existing master account stays the same
API_KEY=master_api_key
CLIENT_ID=master_client_id
PASSWORD=master_password
TOTP_SECRET=master_totp_secret
SECRET_KEY=master_secret_key

# Add follower accounts (copy this template)
FOLLOWER_1_API_KEY=follower1_api_key
FOLLOWER_1_CLIENT_ID=follower1_client_id
FOLLOWER_1_PASSWORD=follower1_password
FOLLOWER_1_TOTP_SECRET=follower1_totp_secret
FOLLOWER_1_SECRET_KEY=follower1_secret_key
```

### Step 2: Run Tests (1 minute)

```bash
cd tests
python test_multi_account_copy_trading.py
```

Expected output:
```
✅ All tests passed
```

### Step 3: Test Configuration (1 minute)

```bash
python run_multi_account_copy_trading.py
```

You should see:
```
📊 Master Account: YOUR_MASTER_ID
👥 Follower Accounts (1):
   1. Follower1 (Client ID: FOLLOWER_ID)
```

### Step 4: Start Copy Trading in Dry Run Mode (1 minute)

The script already runs in dry run mode by default!

```bash
python run_multi_account_copy_trading.py
```

Output:
```
⚠️  DRY RUN MODE: Orders will be simulated but not actually placed
⏰ Monitoring for new orders... (Press Ctrl+C to stop)
```

Now place a test order in your master account and watch it get detected!

---

## 🧪 Testing Checklist

### ✅ Phase 1: Dry Run Testing (Safe)
- [ ] Configuration loads successfully
- [ ] Master account connects
- [ ] Follower accounts connect
- [ ] System detects when you place an order in master account
- [ ] Order details are displayed correctly
- [ ] "Would copy" message shows correct parameters
- [ ] Try different order types (Market, Limit)
- [ ] Try different symbols

### ✅ Phase 2: Live Testing (With Caution)
- [ ] Change `settings.dry_run = False` in the script
- [ ] Start with ONE follower account only
- [ ] Place a SMALL test order in master (1 lot, small value)
- [ ] Verify order executes in follower account
- [ ] Check Angel One app/web to confirm
- [ ] Review logs for success
- [ ] Try a second small test order

### ✅ Phase 3: Production Use
- [ ] Enable all follower accounts
- [ ] Use normal quantities
- [ ] Monitor first few trades closely
- [ ] Check logs after each trading session

---

## 🎯 Common Use Cases

### Use Case 1: Mirror Trading (Same Quantity)
```python
# In run_multi_account_copy_trading.py
settings.copy_all_orders = True
settings.quantity_multiplier = 1.0
settings.dry_run = False  # After testing
```

### Use Case 2: Proportional Trading (50% of Master)
```python
settings.copy_all_orders = True
settings.quantity_multiplier = 0.5
settings.dry_run = False
```

### Use Case 3: Fixed Quantity (Always Trade 25 Lots)
```python
settings.copy_all_orders = True
settings.use_fixed_quantity = True
settings.fixed_quantity = 25
settings.dry_run = False
```

### Use Case 4: Only Copy NIFTY Orders
```python
settings.copy_all_orders = False
settings.allowed_symbols = ['NIFTY']
settings.dry_run = False
```

---

## 📊 What You'll See

### When Order is Detected:
```
🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 
NEW ORDER DETECTED AT 2025-01-15 10:30:45
🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 

📊 Master Account Order Details:
   Symbol: NIFTY23FEB18000CE
   Type: BUY MARKET
   Quantity: 50
   Price: 0
   Status: complete
   Order ID: 123456789

✅ Order approved for copying
```

### In Dry Run Mode:
```
🔍 DRY RUN MODE: Would copy to 2 followers
   Symbol: NIFTY23FEB18000CE
   Type: BUY
   Quantity: 50 → 50 (follower)
   Price: 0
```

### In Live Mode:
```
📤 Copying to 2 follower account(s)...

   📤 Follower1: Placing order...
   ✅ Follower1: Success! Order ID: 987654321
   📤 Follower2: Placing order...
   ✅ Follower2: Success! Order ID: 987654322
```

---

## ⚠️ Important Safety Tips

1. **Always Test in Dry Run First!**
   - Default is dry run mode
   - Test with real orders from master
   - Verify detection works correctly

2. **Start Small in Live Mode**
   - Use one follower account first
   - Use small quantities
   - Verify execution before scaling

3. **Monitor Regularly**
   - Watch console output
   - Check log files
   - Review Angel One app/web

4. **Handle Rate Limits**
   - Don't restart script repeatedly
   - Wait 5-10 minutes if you hit limits
   - System has automatic retry logic

5. **Keep Credentials Secure**
   - Never commit `.env` file
   - Don't share API keys
   - Use secure environment

---

## 🚨 Emergency Stop

To stop the system immediately:

1. Press `Ctrl+C` in the terminal
2. System will stop and show summary
3. Review logs before restarting

Output:
```
COPY TRADING STOPPED BY USER
========================================
📊 Session Summary:
   Total Orders Copied: 5
   Successful: 5
   Failed: 0
   Success Rate: 100.0%
   💾 Records saved to logs/copy_trading_20250115_103045.json
```

---

## 🔧 Troubleshooting

### Problem: "No follower accounts configured"
**Fix:** Add FOLLOWER_1_* credentials to .env file

### Problem: "Rate limit exceeded"
**Fix:** Wait 5-10 minutes, don't restart quickly

### Problem: Orders not detected
**Fix:** 
- Check master account is placing orders
- Order must be "complete" status
- Check console for "NEW ORDER DETECTED"

### Problem: Orders detected but not copied (in live mode)
**Fix:**
- Check order filters (symbols, order types)
- Look for "Skipping order" messages
- Review settings configuration

---

## 📞 Getting Help

If you encounter issues:

1. ✅ Check this quick start guide
2. ✅ Read MULTI_ACCOUNT_COPY_TRADING.md
3. ✅ Review console error messages
4. ✅ Check log files in `logs/` directory
5. ✅ Run unit tests to verify system integrity

---

## 🎓 Next Steps

After successful testing:

1. **Optimize Settings:** Fine-tune quantity, filters, etc.
2. **Add More Followers:** Add FOLLOWER_2_, FOLLOWER_3_, etc.
3. **Monitor Performance:** Review logs and statistics
4. **Scale Gradually:** Increase quantities over time

---

## ✅ Final Checklist Before Going Live

- [ ] Tested in dry run mode successfully
- [ ] All unit tests pass
- [ ] Configuration is correct
- [ ] Test order executed successfully with one follower
- [ ] Verified order in Angel One app/web
- [ ] Understand how to stop the system
- [ ] Know where logs are saved
- [ ] Comfortable with the settings

**Once all checked, you're ready for live trading! 🚀**

---

## 🎯 Success Metrics

Track these to measure success:

- **Copy Success Rate:** Should be >95%
- **Detection Time:** Should be <5 seconds
- **Order Execution:** All followers should execute
- **Zero Errors:** In normal operation

Happy Trading! 🎉
