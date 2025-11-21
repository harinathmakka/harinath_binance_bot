# **Binance Futures Testnet Trading Bot (Python CLI)**

### **Author: Harinath Makka**

A fully functional, production-grade **Binance Futures Testnet trading bot** built in Python.  
This bot supports **Market, Limit, OCO, STOP-MARKET, STOP-LIMIT** orders with complete exchange-filter validation, secure HMAC-SHA256 signing, structured logging, and a clean CLI interface.

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
  - Wait mode (polling until entry fills)  

- **STOP-MARKET Orders**  
  - Supports `closePosition=true`  
  - Auto trigger-side validation  

- **STOP-LIMIT Orders**  
  - Prevents `-2021 Order would immediately trigger`  
  - Tick-size/precision auto-rounding  

### 🔒 Exchange Validation
- Tick size, step size  
- Min quantity  
- Min notional  
- Percent-price rules  
- Correct rounding for price & quantity  
- Detects invalid stop prices  
- Detects invalid limit prices  

### 🧾 Technical Highlights
- HMAC-SHA256 signature generation  
- `.env` secure API loading  
- Modular file structure  
- Structured logging (`bot.log`)  
- Full CLI using argparse  
- 100% compatible with Binance Futures Testnet  

---

# 📁 **Project Structure**

