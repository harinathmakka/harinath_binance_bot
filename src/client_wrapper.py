# src/client_wrapper.py
import time
from typing import Dict, Any, Optional, List
import requests
from .config import BINANCE_API_KEY, BINANCE_API_SECRET, TESTNET_BASE, REQUEST_TIMEOUT, RECV_WINDOW
from .utils import sign_payload
from .logger import log_action, logger

def _local_timestamp_ms() -> int:
    return int(time.time() * 1000)

class BinanceFuturesClient:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, base: Optional[str] = None, sync_time: bool = True):
        self.api_key = api_key or BINANCE_API_KEY
        self.api_secret = api_secret or BINANCE_API_SECRET
        self.base = (base or TESTNET_BASE).rstrip("/")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"X-MBX-APIKEY": self.api_key})
        self.time_offset_ms = 0
        if sync_time:
            try:
                resp = self._public_request("/fapi/v1/time")
                server = int(resp.get("serverTime", 0))
                local = _local_timestamp_ms()
                self.time_offset_ms = server - local
                log_action("time_sync", serverTime=server, localTime=local, offset_ms=self.time_offset_ms)
            except Exception as e:
                logger.warning({"action": "time_sync_failed", "msg": str(e)})

    def _current_timestamp(self) -> int:
        return _local_timestamp_ms() + int(self.time_offset_ms)

    def _signed_request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = dict(params or {})
        params.update({
            "timestamp": self._current_timestamp(),
            "recvWindow": RECV_WINDOW
        })
        try:
            signature = sign_payload(self.api_secret or "", params)
        except Exception as e:
            logger.exception({"action": "sign_failed", "err": str(e)})
            raise
        params["signature"] = signature
        url = f"{self.base}{path}"
        try:
            if method.upper() == "GET":
                r = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            elif method.upper() == "DELETE":
                r = self.session.delete(url, params=params, timeout=REQUEST_TIMEOUT)
            else:
                r = self.session.post(url, params=params, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            log_action("api_request", path=path, method=method, status=r.status_code)
            return data
        except requests.HTTPError as e:
            resp_text = getattr(e.response, "text", None)
            status_code = getattr(e.response, "status_code", None)
            logger.error({"error": "http_error", "path": path, "status": status_code, "text": resp_text})
            raise
        except Exception as e:
            logger.exception({"error": "request_failed", "path": path, "msg": str(e)})
            raise

    def _public_request(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base}{path}"
        try:
            r = self.session.get(url, params=params or {}, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            log_action("public_api_request", path=path, status=r.status_code)
            return data
        except Exception as e:
            logger.exception({"error": "public_request_failed", "path": path, "msg": str(e)})
            raise

    # Public endpoints
    def get_server_time(self) -> Dict[str, Any]:
        return self._public_request("/fapi/v1/time")
    def get_exchange_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        params = {"symbol": symbol} if symbol else {}
        return self._public_request("/fapi/v1/exchangeInfo", params)
    def get_ticker_price(self, symbol: str) -> Dict[str, Any]:
        return self._public_request("/fapi/v1/ticker/price", {"symbol": symbol})

    # Signed endpoints
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: Optional[float] = None, time_in_force: str = "GTC", reduce_only: bool = False) -> Dict[str, Any]:
        params = {"symbol": symbol, "side": side, "type": order_type, "quantity": quantity}
        if order_type.upper() == "LIMIT":
            if price is None:
                raise ValueError("price is required for LIMIT orders")
            params["price"] = float(price)
            params["timeInForce"] = time_in_force
        if reduce_only:
            params["reduceOnly"] = "true"
        return self._signed_request("POST", "/fapi/v1/order", params)

    def get_order(self, symbol: str, orderId: int) -> Dict[str, Any]:
        params = {"symbol": symbol, "orderId": int(orderId)}
        return self._signed_request("GET", "/fapi/v1/order", params)

    def cancel_order(self, symbol: str, orderId: Optional[int] = None, clientOrderId: Optional[str] = None) -> Dict[str, Any]:
        params = {"symbol": symbol}
        if orderId:
            params["orderId"] = int(orderId)
        elif clientOrderId:
            params["origClientOrderId"] = clientOrderId
        else:
            raise ValueError("orderId or clientOrderId required")
        return self._signed_request("DELETE", "/fapi/v1/order", params)

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"symbol": symbol} if symbol else {}
        return self._signed_request("GET", "/fapi/v1/openOrders", params)

    def get_account(self) -> Dict[str, Any]:
        return self._signed_request("GET", "/fapi/v2/account", {})

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: Optional[float] = None,
                    time_in_force: str = "GTC", reduce_only: bool = False, stop_price: Optional[float] = None,
                    close_position: bool = False, working_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Place an order. Extended to accept stop_price (for STOP/STOP_MARKET),
        close_position (for STOP_MARKET), and working_type (MARK_PRICE or CONTRACT_PRICE).
        Existing callers (MARKET, LIMIT) still work as before.
        """
        params = {"symbol": symbol, "side": side, "type": order_type, "quantity": quantity}

        if order_type.upper() == "LIMIT" or order_type.upper() == "STOP":
            if price is None:
                raise ValueError("price is required for LIMIT/STOP (stop-limit) orders")
            params["price"] = float(price)
            params["timeInForce"] = time_in_force

        # Add optional stopPrice for STOP / STOP_MARKET
        if stop_price is not None:
            params["stopPrice"] = float(stop_price)

        # reduceOnly boolean param accepted by futures API
        if reduce_only:
            params["reduceOnly"] = "true"

        # closePosition is specific to STOP_MARKET if you want to close a position
        if close_position:
            params["closePosition"] = "true"

        # workingType - optional (MARK_PRICE or CONTRACT_PRICE)
        if working_type:
            params["workingType"] = working_type

        return self._signed_request("POST", "/fapi/v1/order", params)
