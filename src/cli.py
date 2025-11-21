# src/cli.py
import click
import sys
from tabulate import tabulate
from .logger import log_action
from .market_orders import place_market_order
from .limit_orders import place_limit_order
from .client_wrapper import BinanceFuturesClient
from .advanced.oco import place_oco

@click.group()
def cli():
    """Harinath Binance Bot CLI - testnet"""
    pass

@cli.command()
@click.option("--symbol", required=True)
@click.option("--side", required=True, type=click.Choice(["BUY","SELL"], case_sensitive=False))
@click.option("--qty", required=True)
def market(symbol, side, qty):
    """Place MARKET order"""
    try:
        place_market_order(symbol.upper(), side.upper(), qty)
    except Exception as e:
        print("Market order failed:", e)
        sys.exit(1)

@cli.command()
@click.option("--symbol", required=True)
@click.option("--side", required=True, type=click.Choice(["BUY","SELL"], case_sensitive=False))
@click.option("--qty", required=True)
@click.option("--price", required=True)
def limit(symbol, side, qty, price):
    """Place LIMIT order"""
    try:
        place_limit_order(symbol.upper(), side.upper(), qty, price)
    except Exception as e:
        print("Limit order failed:", e)
        sys.exit(1)

@cli.command("open-orders")
@click.option("--symbol", required=False)
def open_orders_cmd(symbol):
    try:
        c = BinanceFuturesClient(sync_time=True)
        orders = c.get_open_orders(symbol=symbol.upper() if symbol else None)
        if not orders:
            print("No open orders.")
            return
        table = [[o.get("orderId"), o.get("symbol"), o.get("side"), o.get("price"), o.get("origQty"), o.get("status")] for o in orders]
        print(tabulate(table, headers=["orderId","symbol","side","price","qty","status"], tablefmt="plain"))
    except Exception as e:
        print("open-orders failed:", e)
        sys.exit(1)

@cli.command("cancel-all")
@click.option("--symbol", required=False)
def cancel_all_cmd(symbol):
    try:
        c = BinanceFuturesClient(sync_time=True)
        orders = c.get_open_orders(symbol=symbol.upper() if symbol else None)
        if not orders:
            print("No open orders to cancel.")
            return
        cancelled = 0; failed = 0
        for o in orders:
            try:
                c.cancel_order(symbol=o.get("symbol"), orderId=o.get("orderId"))
                print("Cancelled", o.get("orderId"))
                cancelled += 1
            except Exception as e:
                msg = str(e)
                if "Unknown order sent" in msg or "-2011" in msg or "400" in msg:
                    print("Order unknown/already closed:", o.get("orderId"))
                    cancelled += 1
                else:
                    print("Failed to cancel", o.get("orderId"), ":", e)
                    failed += 1
        print(f"Summary cancelled={cancelled}, failed={failed}")
    except Exception as e:
        print("cancel-all failed:", e)
        sys.exit(1)

@cli.command("cancel-order")
@click.option("--symbol", required=True)
@click.option("--order-id", required=False, type=int)
@click.option("--client-order-id", required=False)
def cancel_order_cmd(symbol, order_id, client_order_id):
    if not order_id and not client_order_id:
        print("Provide --order-id or --client-order-id")
        sys.exit(2)
    try:
        c = BinanceFuturesClient(sync_time=True)
        try:
            if order_id:
                resp = c.cancel_order(symbol=symbol.upper(), orderId=order_id)
            else:
                resp = c.cancel_order(symbol=symbol.upper(), clientOrderId=client_order_id)
            print("Cancel response:", resp.get("status"), "orderId:", resp.get("orderId"))
        except Exception as e:
            msg = str(e)
            if "Unknown order sent" in msg or "-2011" in msg or "400" in msg:
                print("Order unknown/already closed; treated as cancelled.")
            else:
                raise
    except Exception as e:
        print("cancel-order failed:", e)
        sys.exit(1)

@cli.command("inspect-pos")
@click.option("--symbol", required=False)
def inspect_pos_cmd(symbol):
    try:
        c = BinanceFuturesClient(sync_time=True)
        acct = c.get_account()
        positions = acct.get("positions", []) or []
        table = []
        for p in positions:
            if symbol and p.get("symbol") != symbol.upper():
                continue
            table.append([p.get("symbol"), p.get("positionAmt"), p.get("entryPrice"), p.get("unRealizedProfit")])
        if not table:
            print("No positions found.")
            return
        print(tabulate(table, headers=["symbol", "positionAmt", "entryPrice", "unRealizedProfit"], tablefmt="plain"))
    except Exception as e:
        print("inspect-pos failed:", e)
        sys.exit(1)

@cli.command("filters")
@click.option("--symbol", required=True)
def filters_cmd(symbol):
    try:
        c = BinanceFuturesClient()
        info = c.get_exchange_info(symbol=symbol.upper())
        sym = info["symbols"][0]
        filters = sym.get("filters", [])
        table = [[f.get("filterType"), ", ".join(f"{k}={v}" for k,v in f.items() if k!="filterType")] for f in filters]
        print(tabulate(table, headers=["filterType","details"], tablefmt="plain"))
    except Exception as e:
        print("filters failed:", e)
        sys.exit(1)

@cli.command()
@click.option("--symbol", required=True)
@click.option("--side", required=True, type=click.Choice(["BUY","SELL"], case_sensitive=False))
@click.option("--qty", required=True)
@click.option("--tp-price", required=True)
@click.option("--sl-price", required=True)
@click.option("--entry-type", default="MARKET", type=click.Choice(["MARKET","LIMIT"], case_sensitive=False))
@click.option("--entry-price", required=False)
@click.option("--wait-time", default=30, type=int)
@click.option("--detach/--no-detach", default=False)
def oco(symbol, side, qty, tp_price, sl_price, entry_type, entry_price, wait_time, detach):
    try:
        result = place_oco(symbol.upper(), side.upper(), qty, float(tp_price), float(sl_price),
                           entry_type=entry_type.upper(), entry_price=entry_price, wait_timeout=wait_time, detach=detach)
        print("OCO result:")
        print("Entry:", result.get("entry", {}).get("status"))
        print("TP orderId:", result.get("tp", {}).get("orderId"))
        print("SL orderId:", result.get("sl", {}).get("orderId"))
        if result.get("detached"):
            print("Detached mode: placed entry + legs and returned.")
        if result.get("winner"):
            print("Winner:", result["winner"][0])
    except Exception as e:
        print("OCO failed:", e)
        sys.exit(1)

@cli.command("auth-check")
def auth_check():
    """Check if signed futures API access works"""
    try:
        c = BinanceFuturesClient(sync_time=True)
        acct = c.get_account()
        print("AUTH OK — futures account accessible.")
        print("Positions:", len(acct.get("positions", [])))
    except Exception as e:
        print("AUTH FAILED:", e)

@cli.command("stop-limit")
@click.option("--symbol", required=True)
@click.option("--side", required=True, type=click.Choice(["BUY","SELL"], case_sensitive=False))
@click.option("--qty", required=True)
@click.option("--stop-price", required=True)
@click.option("--price", required=True, help="Limit price placed after stop triggers")
@click.option("--time-in-force", default="GTC", show_default=True)
@click.option("--reduce-only/--no-reduce-only", default=False)
def stop_limit_cmd(symbol, side, qty, stop_price, price, time_in_force, reduce_only):
    """Place a STOP-LIMIT order (stopPrice -> limit order)"""
    try:
        from .advanced.stop_orders import place_stop_limit
        resp = place_stop_limit(symbol.upper(), side.upper(), qty, float(stop_price), float(price), time_in_force=time_in_force, reduce_only=reduce_only)
        print("Stop-Limit order placed. orderId:", resp.get("orderId"), "status:", resp.get("status"))
    except Exception as e:
        print("stop-limit failed:", e)
        sys.exit(1)


@cli.command("stop-market")
@click.option("--symbol", required=True)
@click.option("--side", required=True, type=click.Choice(["BUY","SELL"], case_sensitive=False))
@click.option("--qty", required=True)
@click.option("--stop-price", required=True)
@click.option("--close-position/--no-close-position", default=False, help="Use to close an existing position on trigger")
def stop_market_cmd(symbol, side, qty, stop_price, close_position):
    """Place a STOP_MARKET order (stopPrice -> market order)"""
    try:
        from .advanced.stop_orders import place_stop_market
        resp = place_stop_market(symbol.upper(), side.upper(), qty, float(stop_price), close_position=close_position)
        print("Stop-Market order placed. orderId:", resp.get("orderId"), "status:", resp.get("status"))
    except Exception as e:
        print("stop-market failed:", e)
        sys.exit(1)


if __name__ == "__main__":
    cli()