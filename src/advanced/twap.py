# src/advanced/twap.py

import time
from ..client_wrapper import BinanceFuturesClient
from ..logger import log_action

def execute_twap(
    symbol: str,
    side: str,
    total_qty: float,
    parts: int,
    interval: int
):
    """
    TWAP = Time Weighted Average Price.
    Splits a large MARKET order into multiple smaller MARKET orders,
    executed at fixed time intervals.

    Example:
        total_qty = 0.02
        parts = 10
        interval = 5 seconds
        → executes 10 slices of 0.002 BTC each, 5 seconds apart.
    """

    if parts < 1:
        raise ValueError("parts must be >= 1")
    if interval < 1:
        raise ValueError("interval must be >= 1")

    slice_qty = float(total_qty) / parts

    log_action({
        "action": "twap_start",
        "symbol": symbol,
        "side": side,
        "total_qty": total_qty,
        "parts": parts,
        "interval_sec": interval,
        "slice_qty": slice_qty
    })

    c = BinanceFuturesClient(sync_time=True)

    results = []
    print(f"\nStarting TWAP: {parts} slices × {slice_qty} qty every {interval} sec")
    print("-" * 50)

    for i in range(1, parts + 1):
        try:
            resp = c.place_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=slice_qty
            )

            log_action({
                "action": "twap_slice",
                "slice": i,
                "orderId": resp.get("orderId"),
                "status": resp.get("status"),
                "executedQty": resp.get("executedQty"),
                "origQty": resp.get("origQty")
            })

            print(f"[Slice {i}/{parts}] → orderId={resp.get('orderId')} status={resp.get('status')}")
            results.append(resp)

        except Exception as e:
            print(f"[Slice {i}] FAILED:", e)
            log_action({
                "action": "twap_slice_failed",
                "slice": i,
                "error": str(e)
            })
            # Do NOT stop the entire TWAP – continue
            continue

        # Sleep only between slices (not after last one)
        if i != parts:
            time.sleep(interval)

    log_action({
        "action": "twap_complete",
        "slices_executed": len(results),
        "expected_slices": parts
    })

    print("\nTWAP Completed.")
    print("Executed slices:", len(results), "/", parts)

    return {
        "executed_slices": len(results),
        "expected_slices": parts,
        "slice_qty": slice_qty,
        "results": results
    }
