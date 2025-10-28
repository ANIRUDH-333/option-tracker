"""
Web-based UI for monitoring orders in real-time.
Simple Flask server with live updates.
"""
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from datetime import datetime
import threading
import os
from smartapi_client import SmartAPIClient
from smart_polling import SmartPollingMonitor

app = Flask(__name__)
CORS(app)

# Global state
monitor = None
latest_orders = []
all_orders = []
monitoring_status = {
    'running': False,
    'start_time': None,
    'orders_detected': 0,
    'last_check': None,
    'polling_interval': '1s',
    'api_calls': '0/60',
    'market_hours': False
}


class UIOrderMonitor(SmartPollingMonitor):
    """Extended monitor that updates UI state."""
    
    def _play_notification_sound(self):
        """Play notification sound if available."""
        try:
            import platform
            import subprocess
            
            # Only try to play sound on local development (macOS/Windows/Linux with audio)
            if os.getenv('RENDER'):
                # Skip audio on Render deployment
                print("🔔 [AUDIO] New order notification (sound disabled in production)")
                return
                
            system = platform.system()
            if system == "Darwin":  # macOS
                os.system('afplay /System/Library/Sounds/Glass.aiff &')
            elif system == "Windows":
                # Windows beep
                import winsound
                winsound.Beep(1000, 500)
            elif system == "Linux":
                # Try to use system beep or paplay
                try:
                    os.system('paplay /usr/share/sounds/alsa/Front_Left.wav &')
                except:
                    print("🔔 [AUDIO] New order detected (no audio available)")
            
        except Exception as e:
            print(f"🔔 [AUDIO] New order detected (audio error: {e})")
    
    def check_for_new_orders(self):
        """Override to update monitoring status."""
        global monitoring_status
        monitoring_status['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        monitoring_status['polling_interval'] = f"{self.current_interval}s"
        monitoring_status['api_calls'] = f"{self.api_calls_count}/{self.max_calls_per_minute}"
        monitoring_status['market_hours'] = self._is_market_hours()
        return super().check_for_new_orders()
    
    def on_new_order(self, order):
        """Override to add orders to UI display."""
        global latest_orders, all_orders, monitoring_status
        
        # Play sound notification (only works locally on macOS)
        self._play_notification_sound()
        
        # Format order for display
        formatted_order = {
            'order_id': order.get('orderid'),
            'symbol': order.get('tradingsymbol'),
            'transaction_type': order.get('transactiontype'),
            'order_type': order.get('ordertype'),
            'quantity': order.get('quantity'),
            'price': order.get('price'),
            'status': order.get('status'),
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'exchange': order.get('exchange'),
            'product_type': order.get('producttype'),
            'filled_quantity': order.get('filledshares', 0),
            'average_price': order.get('averageprice', 0)
        }
        
        # Add to lists
        latest_orders.insert(0, formatted_order)  # Most recent first
        all_orders.insert(0, formatted_order)
        
        # Keep only last 10 in latest
        if len(latest_orders) > 10:
            latest_orders.pop()
        
        monitoring_status['orders_detected'] += 1
        
        # Print to console too
        print(f"\n🔔 NEW ORDER: {formatted_order['symbol']} - {formatted_order['transaction_type']}")


def start_monitoring():
    """Start the order monitor in background."""
    global monitor, monitoring_status
    
    try:
        client = SmartAPIClient()
        monitor = UIOrderMonitor(client)
        monitoring_status['running'] = True
        monitoring_status['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Run in separate thread
        monitor.start()
    except Exception as e:
        print(f"Error starting monitor: {e}")
        monitoring_status['running'] = False


@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get monitoring status."""
    return jsonify(monitoring_status)


@app.route('/api/orders/latest')
def get_latest_orders():
    """Get latest orders."""
    return jsonify(latest_orders)


@app.route('/api/orders/all')
def get_all_orders():
    """Get all orders."""
    return jsonify(all_orders)


@app.route('/api/start', methods=['POST'])
def start_monitor():
    """Start monitoring."""
    if not monitoring_status['running']:
        thread = threading.Thread(target=start_monitoring, daemon=True)
        thread.start()
        return jsonify({'success': True, 'message': 'Monitoring started'})
    return jsonify({'success': False, 'message': 'Already running'})


if __name__ == '__main__':
    print("="*80)
    print("COPY TRADING MONITOR - WEB UI")
    print("="*80)
    print("\n🌐 Starting web server...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("\n⚡ The monitor will start automatically")
    print("🔔 New orders will appear in real-time on the dashboard\n")
    print("="*80 + "\n")
    
    # Start monitoring immediately
    thread = threading.Thread(target=start_monitoring, daemon=True)
    thread.start()
    
    # Start Flask server with production-ready settings
    port = int(os.getenv('PORT', 5000))  # Use Render's PORT or default to 5000
    app.run(debug=False, host='0.0.0.0', port=port)
