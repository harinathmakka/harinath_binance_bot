
# **Binance Futures Testnet Trading Bot (Python CLI)**

### **Author: Harinath Makka**

A fully functional, production-grade **Binance Futures Testnet trading bot** built in Python.  
This bot supports **Market, Limit, OCO, STOP-MARKET, STOP-LIMIT, and TWAP** orders with complete exchange-filter validation, secure HMAC-SHA256 signing, structured logging, and a clean CLI interface.

It demonstrates strong Python skills, API integration, error handling, validations, and modular architecture — suitable for internships and job submissions.

---

# 🚀 **Features**

### ✅ Core Binance Futures Features
- Market BUY / SELL  
- Limit BUY / SELL  
- Cancel an order  
- Cancel all orders  
- View open positions  
- Fetch exchange filters and rules  

### 🔁 Advanced Order Types
- **OCO Orders** (Take Profit + Stop Loss)  
  - Detached mode  
  - Wait mode  

- **STOP-MARKET Orders**  
  - Supports `closePosition=true`  
  - Auto trigger validation  

- **STOP-LIMIT Orders**  
  - Prevents `-2021 Order would immediately trigger`  
  - Tick-size/precision auto-rounding  

- **TWAP (Time Weighted Average Price)**  
  - Splits a large order into smaller slices  
  - Executes slices at fixed time intervals  
  - MARKET-based execution for guaranteed fills  

### 🔒 Exchange Validation
- Tick size, step size  
- Min quantity  
- Min notional  
- Percent-price rules  
- Correct rounding for price & quantity  
- Detects invalid stop/limit prices  

### 🧾 Technical Highlights
- HMAC-SHA256 signature generation  
- `.env` secure API loading  
- Modular file structure  
- Structured logging (`bot.log`)  
- Full CLI using Click  
- 100% compatible with Binance Futures Testnet  

---

# 📁 **Project Structure**

```

harinath_binance_bot/
│
├── src/
│   ├── cli.py                # CLI entrypoint
│   ├── config.py             # Load .env + config
│   ├── client_wrapper.py     # API signing + REST handling
│   ├── utils.py              # Helpers (filters, rounding)
│   ├── market_orders.py      # Market logic
│   ├── limit_orders.py       # Limit logic
│   ├── logger.py             # Loguru setup
│   └── advanced/
│       ├── oco.py            # OCO logic
│       ├── stop_orders.py    # STOP-LIMIT + STOP-MARKET
│       ├── twap.py           # TWAP Market-slice strategy
│
├── requirements.txt
├── .env.example
├── README.md
├── report.pdf
├── bot.log
└── .gitignore

````

---

# 🔧 **Installation & Setup**

## 1️⃣ Clone the repository

```bash
git clone https://github.com/harinathmakka/harinath_binance_bot
cd harinath_binance_bot
````

---

## 2️⃣ Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env`:

```
BINANCE_API_KEY=YOUR_TESTNET_API_KEY
BINANCE_SECRET_KEY=YOUR_TESTNET_SECRET_KEY

TESTNET_BASE=https://testnet.binancefuture.com
REQUEST_TIMEOUT=10
RECV_WINDOW=5000
```

---

# 🧪 **Verify Environment**

```bash
python3 - <<'PY'
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=".env")
print("TESTNET_BASE:", os.getenv("TESTNET_BASE"))
print("API KEY LOADED:", bool(os.getenv("BINANCE_API_KEY")))
PY
```

---

# 🎮 **CLI Usage Guide**

All commands follow this format:

```bash
python3 -m src.cli <command> [options]
```

---

# 📌 **Auth Check**

```bash
python3 -m src.cli auth-check
```

---

# 📌 **Market Orders**

### BUY

```bash
python3 -m src.cli market --symbol BTCUSDT --side BUY --qty 0.002
```

### SELL

```bash
python3 -m src.cli market --symbol BTCUSDT --side SELL --qty 0.002
```

---

# 📌 **Limit Orders**

### BUY LIMIT

```bash
python3 -m src.cli limit --symbol BTCUSDT --side BUY --qty 0.002 --price 82000
```

### SELL LIMIT

```bash
python3 -m src.cli limit --symbol BTCUSDT --side SELL --qty 0.002 --price 83000
```

---

# 📌 **STOP-MARKET Orders**

```bash
python3 -m src.cli stop-market --symbol BTCUSDT --side SELL --qty 0.002 --stop-price 82000 --close-position
```

---

# 📌 **STOP-LIMIT Orders**

### BUY STOP-LIMIT

```bash
python3 -m src.cli stop-limit --symbol BTCUSDT --side BUY --qty 0.002 --stop-price 82500 --price 82550
```

### SELL STOP-LIMIT

```bash
python3 -m src.cli stop-limit --symbol BTCUSDT --side SELL --qty 0.002 --stop-price 82000 --price 81950
```

---

# 📌 **OCO Orders (Take Profit + Stop Loss)**

### Detached Mode

```bash
python3 -m src.cli oco --symbol BTCUSDT --side SELL --entry 83000 --tp 84000 --sl 82000 --qty 0.002 --detached
```

### Wait Mode

```bash
python3 -m src.cli oco --symbol BTCUSDT --side SELL --entry 83000 --tp 84000 --sl 82000 --qty 0.002 --wait
```

---

# 📌 **TWAP Orders (Time Weighted Average Price)**

Split large orders into smaller MARKET slices executed over time.

### Example:

```bash
python3 -m src.cli twap \
    --symbol BTCUSDT \
    --side BUY \
    --qty 0.02 \
    --parts 10 \
    --interval 5
```

Meaning:

* Total quantity = 0.02
* Split into 10 slices → 0.002 each
* 5 seconds between each slice

---

# 📌 **Cancel Orders**

### Cancel single order

```bash
python3 -m src.cli cancel --symbol BTCUSDT --order-id 123456
```

### Cancel all open orders

```bash
python3 -m src.cli cancel-all --symbol BTCUSDT
```

---

# 📌 **Check Positions**

```bash
python3 -m src.cli inspect-pos
```

---

# 📝 **Logging**

All logs saved into:

```
bot.log
```

Includes:

* All API requests
* All responses
* Order details
* Validation errors
* OCO and STOP events
* TWAP slices
* Exchange filter details

---

# 📄 **Project Report**

Full project report: architecture, screenshots, test results:

👉 **[📄 Download Report (PDF)](./report.pdf)**

---

# 🚀 **Future Enhancements**

* Trailing Stop
* Grid trading strategy
* Websocket live price feed
* Strategy engine (scalping, breakout, grid)
* Hedge mode
* Telegram integration
* Portfolio analytics

---

# 🤝 **Contributing**

Pull requests are welcome.
For major changes, please open an issue first.

---

# 📧 **Contact**

**Author:** Harinath Makka
📩 Email: **[harinathmakka@gmail.com](mailto:harinathmakka@gmail.com)**
🌐 GitHub: **[https://github.com/harinathmakka](https://github.com/harinathmakka)**

---
