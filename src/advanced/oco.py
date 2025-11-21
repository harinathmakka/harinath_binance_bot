# src/advanced/oco.py
import time
from decimal import Decimal
from typing import Optional, Tuple, Dict, Any
from ..client_wrapper import BinanceFuturesClient
from ..utils import validate_side, validate_positive_number, parse_symbol_filters, round_price_to_tick, round_down_qty
from ..logger import log_action, logger

def _poll_order_filled(client: BinanceFuturesClient, symbol: str, order_id: int, timeout: int = 30, poll_interval: float = 1.0):
    started = time.time()
    last_order = {}
    while True:
        o = client.get_order(symbol=symbol, orderId=order_id)
        last_order = o
        if (o.get("status") or "").upper() == "FILLED":
            return o
        if time.time() - started > timeout:
            return last_order
        time.sleep(poll_interval)

def _get_position_amount(client: BinanceFuturesClient, symbol: str) -> Decimal:
    acct = client.get_account()
    for p in acct.get("positions", []):
        if p.get("symbol") == symbol:
            return Decimal(str(p.get("positionAmt") or "0"))
    return Decimal("0")

def _place_limit_leg_with_reduce_fallback(client, symbol, side, quantity, price, time_in_force="GTC", prefer_reduce_only=True):
    qty_f = float(quantity)
    price_f = float(price)
    if prefer_reduce_only:
        try:
            resp = client.place_order(symbol=symbol, side=side, order_type="LIMIT", quantity=qty_f, price=price_f, time_in_force=time_in_force, reduce_only=True)
            return resp, True
        except Exception:
            logger.warning({"action":"reduce_only_failed","symbol":symbol,"price":price_f})
    resp = client.place_order(symbol=symbol, side=side, order_type="LIMIT", quantity=qty_f, price=price_f, time_in_force=time_in_force, reduce_only=False)
    return resp, False

def place_oco(symbol: str, side: str, qty, tp_price: float, sl_price: float, entry_type: str = "MARKET", entry_price: Optional[float] = None, wait_timeout: int = 30, poll_interval: float = 1.0, detach: bool = False):
    side = validate_side(side)
    qty_f = validate_positive_number("qty", qty)
    tp_price = validate_positive_number("tp_price", tp_price)
    sl_price = validate_positive_number("sl_price", sl_price)

    client = BinanceFuturesClient()
    info = client.get_exchange_info(symbol=symbol)
    if not info or "symbols" not in info or not info["symbols"]:
        raise RuntimeError("could not fetch symbol info")
    filters = parse_symbol_filters(info["symbols"][0])
    step = filters["stepSize"]
    tick = filters["tickSize"]

    qty_dec = Decimal(str(qty_f))
    qty_dec = round_down_qty(float(qty_dec), step)

    # 1) entry
    if entry_type.upper() == "MARKET":
        entry_resp = client.place_order(symbol=symbol, side=side, order_type="MARKET", quantity=float(qty_dec))
    else:
        if entry_price is None:
            raise ValueError("entry_price required for LIMIT entry_type")
        entry_resp = client.place_order(symbol=symbol, side=side, order_type="LIMIT", quantity=float(qty_dec), price=float(entry_price), time_in_force="GTC")
    log_action("oco_entry_sent", symbol=symbol, resp=entry_resp)

    entry_order_id = entry_resp.get("orderId")
    if not entry_order_id:
        raise RuntimeError("entry returned no orderId")

    if detach:
        # place TP & SL and return immediately
        leg_side = "SELL" if side == "BUY" else "BUY"
        tp_dec = round_price_to_tick(tp_price, tick)
        sl_dec = round_price_to_tick(sl_price, tick)
        pos = _get_position_amount(client, symbol)
        prefer_reduce = (side=="BUY" and pos>0) or (side=="SELL" and pos<0)
        tp_resp, _ = _place_limit_leg_with_reduce_fallback(client, symbol, leg_side, qty_dec, tp_dec, prefer_reduce_only=prefer_reduce)
        sl_resp, _ = _place_limit_leg_with_reduce_fallback(client, symbol, leg_side, qty_dec, sl_dec, prefer_reduce_only=prefer_reduce)
        return {"entry": entry_resp, "tp": tp_resp, "sl": sl_resp, "detached": True}

    # non-detach: wait for fill and monitor
    entry_final = _poll_order_filled(client, symbol, entry_order_id, timeout=wait_timeout, poll_interval=poll_interval)
    if (entry_final.get("status") or "").upper() != "FILLED":
        raise RuntimeError(f"entry not filled within {wait_timeout}s, status={entry_final.get('status')}")
    executed_qty = Decimal(str(entry_final.get("executedQty") or entry_final.get("origQty") or qty_dec))
    leg_qty = round_down_qty(float(executed_qty), step)
    leg_side = "SELL" if side == "BUY" else "BUY"
    tp_dec = round_price_to_tick(tp_price, tick)
    sl_dec = round_price_to_tick(sl_price, tick)
    pos = _get_position_amount(client, symbol)
    prefer_reduce = (side=="BUY" and pos>0) or (side=="SELL" and pos<0)
    tp_resp, _ = _place_limit_leg_with_reduce_fallback(client, symbol, leg_side, leg_qty, tp_dec, prefer_reduce_only=prefer_reduce)
    sl_resp, _ = _place_limit_leg_with_reduce_fallback(client, symbol, leg_side, leg_qty, sl_dec, prefer_reduce_only=prefer_reduce)
    # monitor TP/SL until one fills, then cancel the other
    tp_id = tp_resp.get("orderId")
    sl_id = sl_resp.get("orderId")
    start = time.time()
    winner = None
    while True:
        tp_o = client.get_order(symbol=symbol, orderId=tp_id)
        sl_o = client.get_order(symbol=symbol, orderId=sl_id)
        if (tp_o.get("status") or "").upper() == "FILLED":
            winner = ("TP", tp_o)
            try: client.cancel_order(symbol=symbol, orderId=sl_id)
            except Exception: pass
            break
        if (sl_o.get("status") or "").upper() == "FILLED":
            winner = ("SL", sl_o)
            try: client.cancel_order(symbol=symbol, orderId=tp_id)
            except Exception: pass
            break
        if time.time() - start > wait_timeout:
            break
        time.sleep(poll_interval)
    return {"entry": entry_final, "tp": tp_resp, "sl": sl_resp, "winner": winner}
