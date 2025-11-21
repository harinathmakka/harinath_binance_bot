# **Binance Futures Testnet Trading Bot (Python CLI)**

### *Author: Harinath Makka*

A fully functional, production-grade **Binance Futures Testnet trading bot** built in Python.
This bot supports **Market, Limit, OCO, STOP-MARKET, STOP-LIMIT orders**, exchange-filter validation, secure HMAC-SHA256 signing, structured logging, and a clean CLI interface.

This repository demonstrates strong Python skills, API integration, error handling, validations, and modular architecture — suitable for internships and job-level submissions.

---

# 🔧 **Features**

### ✅ **Core Binance Futures Features**

* Market BUY / SELL
* Limit BUY / SELL
* Cancel a specific order
* Cancel all open orders
* Fetch open positions
* Check exchange info and filters

### 🔁 **Advanced Order Types**

* **OCO Orders** (TP + SL)

  * Detached mode
  * Wait mode (poll until entry fills)

* **STOP-MARKET Orders**

  * Supports `closePosition=true`
  * Automatic trigger-side validation

* **STOP-LIMIT Orders**

  * Validation to prevent `-2021 Order would immediately trigger`
  * Tick-size & precision auto-adjustment

### 🔒 **Exchange Safety & Validation**

* minQty, minNotional, tickSize, stepSize
* percent price rules
* Detects invalid prices
* Detects invalid triggers
* Rounds price/qty correctly

### 🧾 **Technical Highlights**

* HMAC-SHA256 signature generation
* Secure `.env` API key loading
* Clean modular architecture
* Detailed logging (`bot.log`) using Loguru
* Full CLI with argparse
* Works 100% on Binance Futures Testnet

---

# 📁 **Project Structure**

```
harinath_binance_bot/
│
├── src/
│   ├── cli.py                # Main CLI entrypoint
│   ├── config.py             # Loads .env and config
│   ├── client_wrapper.py     # API signing + request handling
│   ├── utils.py              # Filters, rounding, helpers
│   ├── market_orders.py      # Market order logic
│   ├── limit_orders.py       # Limit order logic
│   ├── logger.py             # Loguru logger setup
│   └── advanced/
│       ├── oco.py            # OCO order logic
│       ├── stop_orders.py    # STOP-MARKET & STOP-LIMIT
│
├── .env.example
├── requirements.txt
├── README.md
├── report.pdf                # Final project report
├── bot.log
└── .gitignore
```

---

# 🚀 **Installation & Setup**

## **1. Clone the repository**

```bash
git clone https://github.com/harinathmakka/harinath_binance_bot
cd harinath_binance_bot
```

---

## **2. Create and activate virtualenv**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## **3. Install dependencies**

```bash
pip install -r requirements.txt
```

---

## **4. Create `.env` file**

Copy:

```bash
cp .env.example .env
```

Edit your `.env` file:

```
BINANCE_API_KEY=YOUR_TESTNET_API_KEY
BINANCE_SECRET_KEY=YOUR_TESTNET_SECRET_KEY

TESTNET_BASE=https://testnet.binancefuture.com
```

---

# 🧪 **Quick Environment Check**

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

Run all commands using:

```bash
python3 -m src.cli <command> [options]
```

---

# 📌 **1. Auth Check**

Verify your API keys + signature:

```bash
python3 -m src.cli auth-check
```

---

# 📌 **2. Market Orders**

## BUY

```bash
python3 -m src.cli market --symbol BTCUSDT --side BUY --qty 0.002
```

## SELL

```bash
python3 -m src.cli market --symbol BTCUSDT --side SELL --qty 0.002
```

---

# 📌 **3. Limit Orders**

### BUY Limit at 82000

```bash
python3 -m src.cli limit --symbol BTCUSDT --side BUY --qty 0.002 --price 82000
```

### SELL Limit

```bash
python3 -m src.cli limit --symbol BTCUSDT --side SELL --qty 0.002 --price 83000
```

---

# 📌 **4. STOP-MARKET Orders**

### SELL Stop-Market with close position

```bash
python3 -m src.cli stop-market --symbol BTCUSDT --side SELL --qty 0.002 --stop-price 82000 --close-position
```

---

# 📌 **5. STOP-LIMIT Orders**

### BUY STOP-LIMIT

```bash
python3 -m src.cli stop-limit --symbol BTCUSDT --side BUY --qty 0.002 --stop-price 82500 --price 82550
```

### SELL STOP-LIMIT

```bash
python3 -m src.cli stop-limit --symbol BTCUSDT --side SELL --qty 0.002 --stop-price 82000 --price 81950
```

---

# 📌 **6. OCO Orders (Take Profit + Stop Loss)**

### Detached mode (instant return)

```bash
python3 -m src.cli oco --symbol BTCUSDT --side SELL --entry 83000 --tp 84000 --sl 82000 --qty 0.002 --detached
```

### Wait mode (auto waits until entry is filled)

```bash
python3 -m src.cli oco --symbol BTCUSDT --side SELL --entry 83000 --tp 84000 --sl 82000 --qty 0.002 --wait
```

---

# 📌 **7. Cancel Orders**

### Cancel a single order

```bash
python3 -m src.cli cancel --symbol BTCUSDT --order-id 123456
```

### Cancel all open orders

```bash
python3 -m src.cli cancel-all --symbol BTCUSDT
```

---

# 📌 **8. Positions**

```bash
python3 -m src.cli positions
```

---

# 📝 **Logging**

All API calls & validation logs go to:

```
bot.log
```

Includes:

* All REST requests
* All responses
* All order attempts
* Errors
* Exchange filter data

---

# 🛡️ **Validation & Safety Built In**

The bot prevents:

* Invalid prices
* Wrong stopPrice (avoids `-2021 Order would immediately trigger`)
* Wrong stepSize
* Wrong tickSize
* Wrong minNotional
* Improper trigger-side
* Missing parameters
* Wrong signature

All errors are shown clearly with guidance.

---

# 📄 **Report**

Full detailed report is included:

```
report.pdf
```

Explains architecture, challenges, solutions, testing, and screenshots.

---

# 🚀 **Future Enhancements (Planned)**

* Trailing Stop
* Live price via websockets
* Strategy engine (Scalping / Grid / Breakout)
* Hedge Mode (long + short simultaneously)
* Telegram notifications
* Portfolio analytics

---

# 🤝 **Contributing**

Pull requests are welcome.
For major changes, please open an issue first.

---

# 📧 **Contact**

**Author:** Harinath Makka
Email: **[harinathmakka@gmail.com](mailto:harinathmakka@gmail.com)**
GitHub: **[https://github.com/harinathmakka](https://github.com/harinathmakka)**

---

