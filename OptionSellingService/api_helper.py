# api_helper.py
"""Helper functions for Zerodha Kite API interactions."""

from kiteconnect import KiteConnect
from config import API_KEY, API_SECRET, ACCESS_TOKEN

# Initialize KiteConnect
kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)


def generate_access_token():
    """Generate access token for Zerodha Kite API (run once manually)."""
    kite = KiteConnect(api_key=API_KEY)
    print("Visit this URL to get the request token:", kite.login_url())
    request_token = input("Enter the request token from the URL: ")
    data = kite.generate_session(request_token, api_secret=API_SECRET)
    access_token = data["access_token"]
    print("Access token:", access_token)
    return access_token


def get_current_nifty_price():
    """Fetch the current Nifty spot price."""
    quote = kite.quote("NSE:NIFTY 50")
    return quote["NSE:NIFTY 50"]["last_price"]


def get_options_chain(expiry_date=None):
    """Fetch Nifty options chain for the nearest expiry."""
    instruments = kite.instruments("NFO")
    options = [inst for inst in instruments if inst["name"] == "NIFTY" and inst["instrument_type"] in ["CE", "PE"]]
    if expiry_date:
        options = [opt for opt in options if opt["expiry"] == expiry_date]
    else:
        # Get options with the nearest expiry
        expiry_dates = sorted(set(opt["expiry"] for opt in options))
        nearest_expiry = expiry_dates[0]
        options = [opt for opt in options if opt["expiry"] == nearest_expiry]
    return options


def place_order(order_details):
    """Place an Iron Condor order (four legs)."""
    strikes = order_details["strikes"]
    lots = order_details["lots"]
    lot_size = 50  # Nifty lot size
    orders = [
        {"transaction_type": "SELL", "strike": strikes["sold_call"], "option_type": "CE"},
        {"transaction_type": "BUY", "strike": strikes["bought_call"], "option_type": "CE"},
        {"transaction_type": "SELL", "strike": strikes["sold_put"], "option_type": "PE"},
        {"transaction_type": "BUY", "strike": strikes["bought_put"], "option_type": "PE"}
    ]
    order_ids = []
    for order in orders:
        try:
            trading_symbol = f"NIFTY{order['strike']}{order['option_type']}"  # Simplified; fetch actual symbol
            order_id = kite.place_order(
                variety="regular",
                exchange="NFO",
                tradingsymbol=trading_symbol,
                transaction_type=order["transaction_type"],
                quantity=lots * lot_size,
                product="NRML",
                order_type="LIMIT",
                price=order.get("price")  # Need to fetch last price or set limit price
            )
            order_ids.append(order_id)
        except Exception as e:
            print(f"Order placement failed: {e}")
            return None
    return order_ids


def get_margin_required(strikes, lots):
    """Calculate margin required for the Iron Condor."""
    # Simplified; use kite.order_margins() for accurate margin
    return 100000 * lots  # Placeholder; replace with actual API call


def place_option_order(strike, option_type, transaction_type, lots):
    """Place a market order for a specific option.

    Args:
        strike (int): Strike price of the option.
        option_type (str): 'CE' for call, 'PE' for put.
        transaction_type (str): 'BUY' or 'SELL'.
        lots (int): Number of lots to trade.
    """
    trading_symbol = f"NIFTY{strike}{option_type}"  # Simplified; adjust based on actual symbol format
    lot_size = 50  # Example lot size for NIFTY options
    order_id = kite.place_order(
        variety="regular",
        exchange="NFO",
        tradingsymbol=trading_symbol,
        transaction_type=transaction_type,
        quantity=lots * lot_size,
        product="NRML",  # Normal product type for options
        order_type="MARKET"  # Using market orders for simplicity
    )
    return order_id


if __name__ == "__main__":
    # Run this once to generate access token
    token = generate_access_token()
    print("Update ACCESS_TOKEN in config.py with:", token)
