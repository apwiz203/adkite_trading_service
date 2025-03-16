from kiteconnect import KiteConnect
import pandas as pd
import numpy as np

# Load access token
with open("access_token.txt", "r") as file:
    access_token = file.read().strip()

# Initialize KiteConnect
api_key = "your_api_key"
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# Fetch NIFTY and Bank NIFTY options
instruments = kite.instruments(exchange="NSE")
nifty_options = [instr for instr in instruments if instr['tradingsymbol'].startswith('NIFTY') and instr['segment'] == 'NFO-OPT']
bank_nifty_options = [instr for instr in instruments if instr['tradingsymbol'].startswith('BANKNIFTY') and instr['segment'] == 'NFO-OPT']

# Define your option selling strategy here
# Example: Selling NIFTY OTM options
def sell_otm_options():
    # Fetch current price of NIFTY
    nifty_ltp = kite.ltp("NSE:NIFTY 50")['NSE:NIFTY 50']['last_price']

    # Sell NIFTY OTM options (e.g., 200 points away)
    for option in nifty_options:
        strike_price = int(option['strike'])
        if strike_price > nifty_ltp + 200:
            # Place sell order
            order = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NFO,
                tradingsymbol=option['tradingsymbol'],
                transaction_type=kite.TRANSACTION_TYPE_SELL,
                quantity=75,  # Lot size of NIFTY options
                order_type=kite.ORDER_TYPE_MARKET,
                product=kite.PRODUCT_MIS  # Intraday
            )
            print(f"Order placed: {order}")

if __name__ == "__main__":
    sell_otm_options()
