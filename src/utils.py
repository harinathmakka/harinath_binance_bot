# src/utils.py
import hmac
import hashlib
from decimal import Decimal, ROUND_DOWN
from typing import Dict

from urllib.parse import urlencode

def sign_payload(secret: str, params: dict) -> str:
    # Binance requires original order, no re-sorting
    qs = urlencode(params, doseq=True)
    return hmac.new(secret.encode('utf-8'), qs.encode('utf-8'), hashlib.sha256).hexdigest()

def validate_side(side: str) -> str:
    s = side.upper()
    if s not in ("BUY", "SELL"):
        raise ValueError("side must be BUY or SELL")
    return s

def validate_positive_number(name: str, v) -> float:
    try:
        fv = float(v)
    except Exception:
        raise ValueError(f"{name} must be a number")
    if fv <= 0:
        raise ValueError(f"{name} must be positive")
    return fv

def parse_symbol_filters(symbol_info: dict) -> Dict[str, Decimal]:
    # returns commonly used filter values as Decimal
    f = {"tickSize": Decimal("0"), "stepSize": Decimal("0"), "minQty": Decimal("0"), "minNotional": Decimal("0"), "minPrice": None, "maxPrice": None}
    for fil in symbol_info.get("filters", []):
        t = fil.get("filterType")
        if t == "PRICE_FILTER":
            f["tickSize"] = Decimal(str(fil.get("tickSize", "0")))
            f["minPrice"] = Decimal(str(fil.get("minPrice", "0")))
            f["maxPrice"] = Decimal(str(fil.get("maxPrice", "0")))
        elif t == "LOT_SIZE":
            f["stepSize"] = Decimal(str(fil.get("stepSize", "0")))
            f["minQty"] = Decimal(str(fil.get("minQty", "0")))
        elif t in ("MIN_NOTIONAL", "MIN_NOTIONAL_FILTER"):
            f["minNotional"] = Decimal(str(fil.get("notional", fil.get("minNotional", "0"))))
    return f

def round_price_to_tick(price: float, tick: Decimal) -> Decimal:
    p = Decimal(str(price))
    if tick == 0:
        return p
    return (p // tick) * tick

def round_down_qty(qty: float, step: Decimal) -> Decimal:
    q = Decimal(str(qty))
    if step == 0:
        return q
    precision = -step.as_tuple().exponent
    # floor to step using quantize trick
    return (q.quantize(step, rounding=ROUND_DOWN))
    
def qty_for_min_notional(price: Decimal, min_notional: Decimal, step: Decimal):
    if price == 0:
        return Decimal("0")
    required = (min_notional / price).quantize(step)
    return required
