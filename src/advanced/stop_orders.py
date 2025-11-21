# src/advanced/stop_orders.py
"""
Stop orders module - safer validation to avoid immediate-trigger errors.
Provides:
 - place_stop_limit: Stop-Limit (STOP) order (trigger: stopPrice -> places LIMIT)
 - place_stop_market: Stop-Market (STOP_MARKET) order (trigger: stopPrice -> places MARKET)
"""

from decimal import Decimal
from typing import Optional, Dict, Any
from ..client_wrapper import BinanceFuturesClient
from ..utils import validate_side, validate_positive_number, parse_symbol_filters, round_price_to_tick, round_down_qty
from ..logger import log_action, logger

def _get_current_price(client: BinanceFuturesClient, symbol: str) -> Decimal:
    """Return current contract price as Decimal (uses /fapi/v1/ticker/price)."""
    tick = client.get_ticker_price(symbol)
    p = Decimal(str(tick.get("price") or "0"))
    return p

def _validate_stop_vs_market(symbol: str, client: BinanceFuturesClient, side: str, stop_price: Decimal, tick: Decimal):
    """
    Ensure stop_price is on the correct side of current market price.
    - BUY stop: stop_price must be > current_price + tick (to avoid immediate trigger)
    - SELL stop: stop_price must be < current_price - tick
    Raises ValueError with a helpful message if validation fails.
    """
    current = _get_current_price(client, symbol)
    # add a minimal buffer equal to one tick to avoid edge immediate trigger
    buffer = tick if tick and tick != 0 else Decimal("0.0001")
    if side == "BUY":
        if not (stop_price > (current + buffer)):
            raise ValueError(
                f"Invalid stopPrice for BUY. stopPrice ({stop_price}) must be greater than current price ({current}) by at least one tick ({buffer})."
            )
    else:  # SELL
        if not (stop_price < (current - buffer)):
            raise ValueError(
                f"Invalid stopPrice for SELL. stopPrice ({stop_price}) must be less than current price ({current}) by at least one tick ({buffer})."
            )

def place_stop_limit(symbol: str, side: str, qty, stop_price: float, limit_price: float, time_in_force: str = "GTC", reduce_only: bool = False) -> Dict[str, Any]:
    """
    Place a STOP-LIMIT (STOP) order:
      - stopPrice: the trigger price
      - price: the limit price placed after trigger
    This method validates the stopPrice relative to current market price to avoid immediate-trigger errors.
    """
    side = validate_side(side)
    qty_f = validate_positive_number("qty", qty)
    stop_f = validate_positive_number("stop_price", stop_price)
    limit_f = validate_positive_number("limit_price", limit_price)

    client = BinanceFuturesClient()
    info = client.get_exchange_info(symbol=symbol)
    if not info or "symbols" not in info or not info["symbols"]:
        raise RuntimeError("could not fetch symbol info")
    filters = parse_symbol_filters(info["symbols"][0])
    step = filters["stepSize"]
    tick = filters["tickSize"] or Decimal("0.0001")

    qty_dec = round_down_qty(float(Decimal(str(qty_f))), step)
    limit_price_dec = round_price_to_tick(limit_f, tick)
    stop_price_dec = round_price_to_tick(stop_f, tick)

    # validate stop price vs current price to avoid immediate trigger
    _validate_stop_vs_market(symbol, client, side, Decimal(str(stop_price_dec)), tick)

    log_action("place_stop_limit_attempt", symbol=symbol, side=side, qty=float(qty_dec), stopPrice=float(stop_price_dec), price=float(limit_price_dec))
    # place order using extended client.place_order (stop_price passed)
    resp = client.place_order(symbol=symbol, side=side, order_type="STOP", quantity=float(qty_dec),
                              price=float(limit_price_dec), time_in_force=time_in_force,
                              stop_price=float(stop_price_dec), reduce_only=reduce_only)
    log_action("place_stop_limit_sent", symbol=symbol, side=side, qty=float(qty_dec), stopPrice=float(stop_price_dec), price=float(limit_price_dec), orderId=resp.get("orderId"))
    return resp

def place_stop_market(symbol: str, side: str, qty, stop_price: float, close_position: bool = False) -> Dict[str, Any]:
    """
    Place a STOP_MARKET order:
      - stopPrice: trigger price
      - order type STOP_MARKET (market order placed when trigger hits)
      - closePosition: for closing an existing position (optional flag)
    Validates stopPrice relative to current market price to avoid immediate-trigger errors.
    """
    side = validate_side(side)
    qty_f = validate_positive_number("qty", qty)
    stop_f = validate_positive_number("stop_price", stop_price)

    client = BinanceFuturesClient()
    info = client.get_exchange_info(symbol=symbol)
    if not info or "symbols" not in info or not info["symbols"]:
        raise RuntimeError("could not fetch symbol info")
    filters = parse_symbol_filters(info["symbols"][0])
    step = filters["stepSize"]
    tick = filters["tickSize"] or Decimal("0.0001")

    qty_dec = round_down_qty(float(Decimal(str(qty_f))), step)
    stop_price_dec = round_price_to_tick(stop_f, tick)

    # validate stop price vs current price
    _validate_stop_vs_market(symbol, client, side, Decimal(str(stop_price_dec)), tick)

    log_action("place_stop_market_attempt", symbol=symbol, side=side, qty=float(qty_dec), stopPrice=float(stop_price_dec), closePosition=close_position)
    resp = client.place_order(symbol=symbol, side=side, order_type="STOP_MARKET", quantity=float(qty_dec), stop_price=float(stop_price_dec), close_position=bool(close_position))
    log_action("place_stop_market_sent", symbol=symbol, side=side, qty=float(qty_dec), stopPrice=float(stop_price_dec), closePosition=close_position, orderId=resp.get("orderId"))
    return resp
