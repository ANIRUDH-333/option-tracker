# SmartAPI Rate Limits & Optimization Guide

## 📊 SmartAPI Rate Limits

Based on SmartAPI documentation:

- **Order Book API**: ~10-20 requests per second (very generous)
- **Recommended Safe Limit**: 1 request per 2 seconds (30/minute)
- **Conservative Limit**: 1 request per 5 seconds (12/minute)

## ⚡ Our Polling Strategies

### 1. **Simple Polling** (polling_monitor.py)
- **Interval**: 3 seconds
- **API Calls**: ~20 per minute
- **Status**: ✅ Safe - well within limits
- **Best for**: Testing, simple monitoring

### 2. **Smart Polling** (smart_polling.py) - RECOMMENDED
- **Market Hours**: 5 seconds (~12 calls/minute)
- **Off Hours**: 30 seconds (~2 calls/minute)
- **Rate Limit**: 30 calls/minute with automatic throttling
- **Status**: ✅ Very safe with intelligent adaptation
- **Best for**: Production copy trading

### 3. **WebSocket** (websocket_monitor.py)
- **API Calls**: Only on connection setup
- **Real-time**: Instant notifications
- **Status**: ✅ Best for rate limits (minimal API usage)
- **Best for**: High-frequency trading (if WebSocket works reliably)

## 🎯 Recommended Approach

### For Copy Trading:
```python
# Use Smart Polling (best balance)
python smart_polling.py
```

**Why?**
- Only 12 calls/minute during market hours (well within limits)
- Reduces to 2 calls/minute outside market hours
- 5-second detection is fast enough for copy trading
- Built-in rate limit protection
- Automatic backoff on errors

## 📈 Rate Limit Calculations

### Conservative (5 second interval):
- Calls per minute: 12
- Calls per hour: 720
- Daily (9 hours trading): 6,480 calls
- **Risk**: ✅ Very low

### Moderate (3 second interval):
- Calls per minute: 20
- Calls per hour: 1,200
- Daily (9 hours trading): 10,800 calls
- **Risk**: ✅ Low

### Aggressive (1 second interval):
- Calls per minute: 60
- Calls per hour: 3,600
- Daily (9 hours trading): 32,400 calls
- **Risk**: ⚠️ Medium (may hit limits)

## 🛡️ Protection Mechanisms in Smart Polling

1. **Rate Limit Counter**: Tracks API calls per minute
2. **Automatic Throttling**: Pauses if limit reached
3. **Adaptive Intervals**: Slower polling outside market hours
4. **Weekend Detection**: Minimal polling on weekends
5. **Error Backoff**: Increases interval on repeated errors

## 💡 Best Practices

1. **Start Conservative**: Use 5-second intervals initially
2. **Monitor Logs**: Check for any rate limit warnings
3. **Use Smart Polling**: Automatic adaptation to market hours
4. **Test First**: Run for a day to ensure no issues
5. **Consider WebSocket**: If you need sub-second latency

## 🔧 Adjusting Rate Limits

Edit `smart_polling.py`:

```python
# More conservative (slower, safer)
self.market_hours_interval = 10  # 10 seconds
self.max_calls_per_minute = 15   # 15 calls/minute

# More aggressive (faster, higher risk)
self.market_hours_interval = 2   # 2 seconds
self.max_calls_per_minute = 60   # 60 calls/minute
```

## ❓ FAQ

**Q: Will 3-second polling hit rate limits?**
A: No, 20 calls/minute is well within SmartAPI's limits.

**Q: What happens if I hit the limit?**
A: Smart polling will automatically pause and wait.

**Q: Is 5 seconds fast enough for copy trading?**
A: Yes! Most copy trading happens within 5-10 seconds, which is acceptable.

**Q: Should I use WebSocket instead?**
A: WebSocket is best for latency, but polling is more reliable and easier to debug.

**Q: Can I run multiple monitors?**
A: Yes, but each uses the same API quota. Keep total calls under 30/minute.

## 🎯 Final Recommendation

**For most copy trading needs:**
- Use `smart_polling.py` with 5-second market hours interval
- This gives you 5-second detection with zero rate limit concerns
- Automatic adaptation to market hours saves API quota
- Built-in protection prevents any issues

**Only use faster polling if:**
- You're copying high-frequency day trading
- You need sub-5-second execution
- You've tested and confirmed no rate limit issues
