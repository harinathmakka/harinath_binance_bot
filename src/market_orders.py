# src/market_orders.py
from .client_wrapper import BinanceFuturesClient
from .utils import validate_side, validate_positive_number, parse_symbol_filters, round_down_qty
from .logger import log_action, logger
from decimal import Decimal
from tabulate import tabulate

def place_market_order(symbol: str, side: str, qty) -> dict:
    side = validate_side(side)
    qty_f = validate_positive_number("qty", qty)
    client = BinanceFuturesClient()
    info = client.get_exchange_info(symbol=symbol)
    if not info or "symbols" not in info or not info["symbols"]:
        raise RuntimeError("Could not fetch symbol info")
    filters = parse_symbol_filters(info["symbols"][0])
    step = filters["stepSize"]
    # Round down qty to step
    qty_dec = Decimal(str(qty_f))
    if qty_dec < filters.get("minQty", Decimal("0")):
        qty_dec = filters.get("minQty", qty_dec)
    qty_dec = round_down_qty(float(qty_dec), step)
    resp = client.place_order(symbol=symbol, side=side, order_type="MARKET", quantity=float(qty_dec))
    log_action("place_market_order", symbol=symbol, side=side, qty=float(qty_dec), result="sent")
    summary = [
        ["symbol", symbol],
        ["side", side],
        ["qty", float(qty_dec)],
        ["status", resp.get("status")],
        ["orderId", resp.get("orderId")],
        ["avgPrice", resp.get("avgPrice", "")]
    ]
    print(tabulate(summary, tablefmt="plain"))
    return resp
