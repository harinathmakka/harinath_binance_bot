# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
# Testnet base URL for Binance USDT-M futures (assignment requires this)
TESTNET_BASE = os.getenv("TESTNET_BASE", "https://testnet.binancefuture.com")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
RECV_WINDOW = int(os.getenv("RECV_WINDOW", "5000"))

# Logging path
LOG_PATH = os.getenv("LOG_PATH", "bot.log")
