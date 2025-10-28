# SmartAPI Order Monitor

A Python application for monitoring and displaying option orders from SmartAPI.

## Setup

1. **Clone the repository** (or create the project directory)

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your SmartAPI credentials in the `.env` file:
     ```
     API_KEY=your_api_key_here
     CLIENT_ID=your_client_id_here
     PASSWORD=your_password_here
     TOTP_SECRET=your_totp_secret_here
     SECRET_KEY=your_secret_key_here
     ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## Project Structure

- `main.py` - Main entry point for the application
- `config.py` - Configuration management and environment variables
- `smartapi_client.py` - SmartAPI client wrapper for session management
- `order_utils.py` - Utility functions for processing and filtering orders
- `order_monitor.py` - Order monitoring and checking functions
- `display.py` - Display functions for formatted output
- `.env` - Environment variables (not tracked in git)
- `.env.example` - Example environment file template
- `requirements.txt` - Python dependencies

## Features

- Monitor option orders (CE/PE) from SmartAPI
- Display aggregated orders by symbol and transaction type
- View trading history for specific dates
- **Real-time order monitoring** for copy trading
- **Automatic order mirroring** to another account
- Secure credential management using environment variables

## Usage

### 🌐 Web UI (Recommended - Visual Dashboard)
```bash
# Install dependencies first
pip install -r requirements.txt

# Start the web UI
python web_ui.py
```
Then open **http://localhost:5000** in your browser.

**Features:**
- 📊 Real-time dashboard with live order updates
- 🔔 Visual notifications when new orders are detected
- 📈 Statistics: order count, status, last check time, API usage
- 🎨 Beautiful, responsive UI
- ⚡ **1-second polling** - feels instant for your 3-4 trades/day
- 🛡️ Rate limit protection with 90% safety buffer
- 🕐 Auto-refreshes every 2 seconds

### 1. View Current Orders (One-time)
```bash
python main.py
```

### 2. Real-time Order Monitoring (Recommended for Copy Trading)

**Option A: Polling Method (Most Reliable)**
```bash
python polling_monitor.py
```
This checks for new orders every 3 seconds. Simple and reliable.

**Option B: WebSocket Method (Real-time)**
```bash
python websocket_monitor.py
```
Uses WebSocket for instant notifications (may need additional setup).

### 3. Copy Trading (Mirror Orders to Another Account)

1. First, set up credentials for the second account in `.env`:
   ```
   # Target account credentials
   TARGET_API_KEY=...
   TARGET_CLIENT_ID=...
   TARGET_PASSWORD=...
   TARGET_TOTP_SECRET=...
   ```

2. Update `copy_trading.py` to use target account credentials

3. Run copy trading:
   ```bash
   python copy_trading.py
   ```

## How Copy Trading Works

1. **Detection**: Monitors source account every 3 seconds (or via WebSocket)
2. **Validation**: Checks if order is new (not seen before)
3. **Notification**: Displays order details immediately
4. **Mirroring**: Places identical order in target account
5. **Confirmation**: Shows success/failure of mirror order

## Choosing the Right Monitoring Method

| Method | Latency | Reliability | Best For |
|--------|---------|-------------|----------|
| **Smart Polling (1s)** | ~1 second | ⭐⭐⭐⭐⭐ | **Your setup (3-4 trades/day)** |
| Polling (5s) | ~5 seconds | ⭐⭐⭐⭐⭐ | Regular day trading |
| WebSocket | ~instant | ⭐⭐⭐ | High-frequency (if stable) |

**For 3-4 trades/day with 1-second polling:**
- ✅ Feels instant (1-2 second detection)
- ✅ Only uses 10% of API capacity
- ✅ See trades happen in real-time
- ✅ Safe with 90% rate limit headroom
- ✅ Perfect balance of speed and reliability

## Security

**Important:** Never commit your `.env` file to version control. It contains sensitive credentials.
The `.gitignore` file is configured to exclude it automatically.
