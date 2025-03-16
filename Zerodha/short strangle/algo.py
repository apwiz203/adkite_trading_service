from kiteconnect import KiteConnect
import datetime

# Initialize KiteConnect with your API key
api_key = "your_api_key"
api_secret = "your_api_secret"
kite = KiteConnect(api_key=api_key)

# Assume you've already obtained the access token through the login flow
access_token = "your_access_token"
kite.set_access_token(access_token)

# Define the underlying asset, expiry, and strike prices for the options
underlying_symbol = "NIFTY"
expiry_date = datetime.date(2024, 5, 25)  # Example expiry date
call_strike_price = 17000
put_strike_price = 16000

# Fetch option instrument tokens for the defined options
instrument_dict = kite.instruments("NSE")
call_token = None
put_token = None
for instrument in instrument_dict:
    if (instrument['tradingsymbol'] == f"{underlying_symbol}{expiry_date:%y%b}%CE{call_strike_price}" or
        instrument['tradingsymbol'] == f"{underlying_symbol}{expiry_date:%y%b}%PE{put_strike_price}"):
        if 'CE' in instrument['tradingsymbol']:
            call_token = instrument['instrument_token']
        else:
            put_token = instrument['instrument_token']

# Sell the options (ensure you have the necessary margins)
if call_token and put_token:
    kite.place_order(tradingsymbol=f"{underlying_symbol}{expiry_date:%y%b}%CE{call_strike_price}",
                     exchange=kite.EXCHANGE_NFO,
                     transaction_type=kite.TRANSACTION_TYPE_SELL,
                     quantity=1,
                     order_type=kite.ORDER_TYPE_MARKET,
                     product=kite.PRODUCT_MIS,
                     variety=kite.VARIETY_REGULAR)

    kite.place_order(tradingsymbol=f"{underlying_symbol}{expiry_date:%y%b}%PE{put_strike_price}",
                     exchange=kite.EXCHANGE_NFO,
                     transaction_type=kite.TRANSACTION_TYPE_SELL,
                     quantity=1,
                     order_type=kite.ORDER_TYPE_MARKET,
                     product=kite.PRODUCT_MIS,
                     variety=kite.VARIETY_REGULAR)
else:
    print("Could not find option tokens. Check your symbols and expiry date.")

# Risk Management
# Implement your risk management here. This could include setting stop-loss orders,
# monitoring positions for potential adjustments, etc.

