# System Architecture - Multi-Account Copy Trading

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERACTION                             │
│                                                                  │
│  1. Configure .env file with account credentials                │
│  2. Run: python run_multi_account_copy_trading.py              │
│                                                                  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│           run_multi_account_copy_trading.py                     │
│  • Load configuration                                           │
│  • Set copy trading settings (dry_run, filters, etc.)          │
│  • Initialize and start copy trader                             │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              MultiAccountConfig                                  │
│  • Loads master account from .env                               │
│  • Loads all FOLLOWER_N_* accounts from .env                   │
│  • Validates all credentials                                    │
│  • Provides account list to system                             │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              ClientManager                                       │
│  • Creates MultiAccountClient for each account                  │
│  • Initializes sessions with rate limit handling               │
│  • Manages all SmartAPI client instances                        │
│  • 5-second delay between initializations                       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│         MultiAccountCopyTrader (Main Engine)                    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Initialize with master + followers                   │  │
│  │  2. Load existing orders to avoid duplicates             │  │
│  │  3. Start monitoring loop (every 3 seconds)              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  MONITORING LOOP                                          │  │
│  │                                                           │  │
│  │  While True:                                              │  │
│  │    • Fetch order book from master                        │  │
│  │    • Find new orders (not seen before)                   │  │
│  │    • For each new completed order:                       │  │
│  │        → Apply filters (symbols, types)                  │  │
│  │        → Calculate follower quantities                    │  │
│  │        → Copy to each follower                           │  │
│  │        → Log results                                      │  │
│  │    • Sleep for 3 seconds                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Order Flow Diagram

```
MASTER ACCOUNT          COPY TRADING SYSTEM           FOLLOWER ACCOUNTS
─────────────          ────────────────────          ─────────────────

Place Order
    │
    ├─ NIFTY23FEB
    │  18000CE
    │  BUY, Qty: 50
    │  Market Order
    │
    ▼
Order Executed ───────► Polling Loop
                        (every 3 sec)
                            │
                            ├─ Fetch Order Book
                            │
                            ▼
                        New Order
                        Detected?
                            │
                            ├─ Yes ─────► Check Filters
                            │               │
                            │               ├─ Symbol OK?
                            │               ├─ Order Type OK?
                            │               └─ Status Complete?
                            │                   │
                            │                   ▼
                            │               Apply Settings
                            │                   │
                            │                   ├─ Quantity: 50
                            │                   │  (multiplier: 1.0)
                            │                   │
                            │                   ▼
                            │               Dry Run?
                            │                   │
                            │                   ├─ Yes → Display Only
                            │                   │
                            │                   └─ No → Place Orders
                            │                             │
                            │                             ▼
                            │                     ┌───────────────┐
                            │                     │ Follower 1    │
                            │                     ├───────────────┤
                            │                     │ Place Order   │◄───┐
                            │                     │ NIFTY         │    │
                            │                     │ BUY, Qty: 50  │    │
                            │                     └───────────────┘    │
                            │                             │            │
                            │                             ├─ Success   │
                            │                             │  Order ID  │
                            │                             │  9876543   │
                            │                             │            │
                            │                     ┌───────────────┐    │
                            │                     │ Follower 2    │    │
                            │                     ├───────────────┤    │
                            │                     │ Place Order   │────┘
                            │                     │ NIFTY         │
                            │                     │ BUY, Qty: 50  │
                            │                     └───────────────┘
                            │                             │
                            │                             ├─ Success
                            │                             │  Order ID
                            │                             │  9876544
                            │                             │
                            ▼                             ▼
                        Log Results                   Orders
                        Save to JSON ◄────────────── Executed
                            │
                            ├─ Total: 2
                            ├─ Success: 2
                            └─ Failed: 0
```

## 📦 Component Interaction

```
┌──────────────────────────────────────────────────────────────────┐
│                        CONFIGURATION LAYER                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  .env File → MultiAccountConfig                                  │
│              │                                                    │
│              ├─ Master Account (AccountConfig)                   │
│              │   • API_KEY, CLIENT_ID, etc.                      │
│              │                                                    │
│              └─ Follower Accounts (List[AccountConfig])          │
│                  • FOLLOWER_1_*, FOLLOWER_2_*, ...               │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ClientManager                                                    │
│  │                                                                │
│  ├─ master_client (MultiAccountClient)                          │
│  │   • SmartConnect instance                                     │
│  │   • Session management                                        │
│  │   • Order book fetching                                       │
│  │                                                                │
│  └─ follower_clients (List[MultiAccountClient])                 │
│      • Each has own SmartConnect                                 │
│      • Independent sessions                                      │
│      • Order placement                                           │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                         LOGIC LAYER                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  MultiAccountCopyTrader                                          │
│  │                                                                │
│  ├─ CopyTradingSettings                                          │
│  │   • dry_run mode                                              │
│  │   • Symbol filters                                            │
│  │   • Quantity rules                                            │
│  │   • Order type filters                                        │
│  │                                                                │
│  └─ OrderTracker                                                 │
│      • Known order IDs                                           │
│      • Copy records                                              │
│      • Statistics                                                │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                         OUTPUT LAYER                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Console Output          JSON Logs                               │
│  • Real-time display     • logs/copy_trading_*.json              │
│  • Order details         • Complete copy history                 │
│  • Success/failure       • Statistics                            │
│  • Statistics            • Error details                         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## 🔐 Security & Safety Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                      SAFETY MECHANISMS                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  LAYER 1: Configuration Validation                         │ │
│  │  • Check all required fields present                       │ │
│  │  • Validate credential format                              │ │
│  │  • Test account connections                                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  LAYER 2: Rate Limit Protection                            │ │
│  │  • 5-second delay between account inits                    │ │
│  │  • Exponential backoff on errors                           │ │
│  │  • Automatic retry with delays                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  LAYER 3: Order Validation                                 │ │
│  │  • Only copy completed orders                              │ │
│  │  • Avoid duplicate order IDs                               │ │
│  │  • Validate order parameters                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  LAYER 4: Filtering & Rules                                │ │
│  │  • Symbol whitelist/blacklist                              │ │
│  │  • Order type filtering                                    │ │
│  │  • Quantity validation                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  LAYER 5: Dry Run Mode                                     │ │
│  │  • Simulate without placing orders                         │ │
│  │  • Display what would happen                               │ │
│  │  • Test configuration safely                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  LAYER 6: Manual Confirmation (Optional)                   │ │
│  │  • Prompt before each copy                                 │ │
│  │  • Review order details                                    │ │
│  │  • User approval required                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  LAYER 7: Error Handling                                   │ │
│  │  • Try-catch on all operations                             │ │
│  │  • Log failures for review                                 │ │
│  │  • Continue on single failure                              │ │
│  │  • Never crash the system                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  LAYER 8: Comprehensive Logging                            │ │
│  │  • Every decision logged                                   │ │
│  │  • Success/failure tracking                                │ │
│  │  • JSON records for audit                                  │ │
│  │  • Session statistics                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Data Flow

```
1. CONFIGURATION LOADING
   .env file → MultiAccountConfig → Validated Config
   
2. CLIENT INITIALIZATION
   Config → ClientManager → SmartAPI Clients
   • Master client initialized
   • Wait 5 seconds
   • Follower 1 initialized
   • Wait 5 seconds
   • Follower 2 initialized
   • ...
   
3. INITIAL STATE LOAD
   Master Client → Order Book API → Existing Orders
   • Store all order IDs
   • Avoid copying old orders
   
4. MONITORING LOOP
   Every 3 seconds:
   Master Client → Order Book API → Current Orders
   → Find new orders (not in known_orders)
   → Filter by status='complete'
   → Process each new order
   
5. ORDER PROCESSING
   New Order → Apply Filters
            → Check Settings
            → Calculate Quantities
            → For each follower:
                → Build order params
                → Place order (or simulate)
                → Track result
            → Log all actions
   
6. LOGGING
   Each Copy Attempt → JSON Record
   {
     master_order_id,
     symbol,
     quantity,
     follower_name,
     success,
     follower_order_id,
     error
   }
   → Append to copy_records
   → Save to file on exit
```

## 🔄 State Management

```
┌─────────────────────────────────────────────────────────────────┐
│                    OrderTracker State                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  known_master_orders: Set[str]                                  │
│  • All order IDs seen from master                               │
│  • Used to detect new orders                                    │
│  • Initialized with existing orders                             │
│                                                                  │
│  copy_records: List[Dict]                                       │
│  • Every copy attempt                                           │
│  • Success and failure                                          │
│  • Complete order details                                       │
│                                                                  │
│  failed_copies: List[Dict]                                      │
│  • Failed copy attempts                                         │
│  • For retry or review                                          │
│  • Error messages included                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

State Transitions:
──────────────────

Order Not Seen → New Order Detected → Process Order → Copy Success
                                                    → Copy Failed
                                                    
Copy Failed → Log to failed_copies → Continue (don't crash)
```

## 🎯 Decision Points

```
                    NEW ORDER DETECTED
                           │
                           ▼
                    Order Complete?
                      /          \
                    No            Yes
                    │              │
                Skip              ▼
                              Symbol Filter
                              /          \
                         Blocked       Allowed
                           │              │
                          Skip           ▼
                                   Order Type Filter
                                   /             \
                              Disabled        Enabled
                                 │               │
                                Skip            ▼
                                           Dry Run?
                                           /        \
                                         Yes         No
                                         │           │
                                    Display     Confirmation?
                                         │      /         \
                                         │    Yes         No
                                         │     │           │
                                         │   Ask User     │
                                         │   /      \     │
                                         │ Yes      No    │
                                         │  │       │     │
                                         │  │      Skip   │
                                         └──┴─────────────┘
                                                  │
                                                  ▼
                                          Place Orders in
                                          All Followers
                                                  │
                                                  ▼
                                            Log Results
```

This architecture ensures:
- ✅ Clean separation of concerns
- ✅ Easy to test each component
- ✅ Multiple safety layers
- ✅ Comprehensive logging
- ✅ Graceful error handling
- ✅ Scalable to many followers
