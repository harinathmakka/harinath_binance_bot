# src/limit_orders.py
from .client_wrapper import BinanceFuturesClient
from .utils import validate_side, validate_positive_number, parse_symbol_filters, round_price_to_tick, round_down_qty
from .logger import log_action, logger
from tabulate import tabulate
from decimal import Decimal

def place_limit_order(symbol: str, side: str, qty, price) -> dict:
    side = validate_side(side)
    qty_f = validate_positive_number("qty", qty)
    price_f = validate_positive_number("price", price)
    client = BinanceFuturesClient()
    info = client.get_exchange_info(symbol=symbol)
    if not info or "symbols" not in info or not info["symbols"]:
        raise RuntimeError("Could not fetch symbol info")
    filters = parse_symbol_filters(info["symbols"][0])
    step = filters["stepSize"]
    tick = filters["tickSize"]
    min_qty = filters.get("minQty", Decimal("0"))
    min_price = filters.get("minPrice", None)
    qty_dec = Decimal(str(qty_f))
    if qty_dec < min_qty:
        qty_dec = min_qty
    qty_dec = round_down_qty(float(qty_dec), step)
    price_dec = round_price_to_tick(price_f, tick)
    resp = client.place_order(symbol=symbol, side=side, order_type="LIMIT", quantity=float(qty_dec), price=float(price_dec), time_in_force="GTC")
    log_action("place_limit_order", symbol=symbol, side=side, qty=float(qty_dec), price=float(price_dec), result="sent")
    summary = [
        ["symbol", symbol],
        ["side", side],
        ["qty", float(qty_dec)],
        ["price", float(price_dec)],
        ["status", resp.get("status")],
        ["orderId", resp.get("orderId")],
    ]
    print(tabulate(summary, tablefmt="plain"))
    return resp
