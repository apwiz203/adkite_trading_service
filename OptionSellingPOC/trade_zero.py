import time
import logging
import datetime
import pytz
from kiteconnect import KiteConnect
from kiteconnect.exceptions import KiteException

# ==================== CONFIGURATION ====================
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"
REQUEST_TOKEN = "your_request_token"

UNDERLYING = "NIFTY"  # or "BANKNIFTY"
LOTS = 5
QUANTITY_PER_LOT = 50
TOTAL_QUANTITY = LOTS * QUANTITY_PER_LOT

# Risk management parameters
STOP_LOSS_PERCENT = 0.5   # 50% increase in premium triggers stop loss
TARGET_PROFIT = 1500      # Example profit target in INR
MAX_LOSS = -2000          # Example max loss in INR
TRAIL_PROFIT_TRIGGER = 800
TRAIL_AMOUNT = 200

# Market times (Assuming IST - Asia/Kolkata)
MARKET_START = datetime.time(9, 15)
MARKET_END = datetime.time(15, 20)
IST = pytz.timezone("Asia/Kolkata")

# Logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ==================== INITIAL SETUP ====================
kite = KiteConnect(api_key=API_KEY)

try:
    session_data = kite.generate_session(REQUEST_TOKEN, api_secret=API_SECRET)
    kite.set_access_token(session_data["access_token"])
    logging.info("Session generated successfully!")
except KiteException as e:
    logging.error(f"Error generating session: {e}")
    exit()

# ==================== UTILITY FUNCTIONS ====================
def is_market_open():
    now = datetime.datetime.now(IST).time()
    return MARKET_START <= now <= MARKET_END

def get_live_price(exchange_instrument):
    """
    Fetch the last traded price for a given instrument.
    exchange_instrument e.g. "NSE:NIFTY 50"
    """
    try:
        quote = kite.ltp([exchange_instrument])
        price = quote[exchange_instrument]["last_price"]
        logging.debug(f"Live price for {exchange_instrument}: {price}")
        return price
    except Exception as e:
        logging.error(f"Failed to get LTP for {exchange_instrument}: {e}")
        return None

def get_next_expiry():
    """
    Returns the next weekly expiry date as a string.
    Assumes weekly expiry on Thursdays. If today is Thursday,
    the next week's expiry is chosen.
    """
    today = datetime.date.today()
    days_until_thursday = (3 - today.weekday()) % 7
    if days_until_thursday == 0:
        days_until_thursday = 7  # If today is Thursday, pick next week's expiry
    next_thursday = today + datetime.timedelta(days=days_until_thursday)
    expiry_str = next_thursday.strftime("%d%b").upper()  # e.g., "24AUG"
    logging.debug(f"Next expiry determined as: {expiry_str}")
    return expiry_str

def construct_option_symbol(underlying, expiry, strike, option_type):
    """
    Construct an option symbol string.
    Example: "NFO:NIFTY24AUG17500CE"
    """
    symbol = f"NFO:{underlying}{expiry}{int(strike)}{option_type}"
    logging.debug(f"Constructed symbol: {symbol}")
    return symbol

def calculate_strikes(atm_price):
    """
    Dummy logic for calculating strikes based on the ATM price.
    Replace with delta or probability-based calculations as needed.
    """
    short_put_strike = atm_price - 300
    long_put_strike = short_put_strike - 100
    short_call_strike = atm_price + 300
    long_call_strike = short_call_strike + 100
    logging.debug(f"Calculated strikes: SP: {short_put_strike}, LP: {long_put_strike}, SC: {short_call_strike}, LC: {long_call_strike}")
    return {
        "short_put": short_put_strike,
        "long_put": long_put_strike,
        "short_call": short_call_strike,
        "long_call": long_call_strike,
    }

def place_order(tradingsymbol, transaction_type, quantity, price=None, retries=3):
    """
    Place an order with retry logic.
    price = None implies a MARKET order; otherwise, a LIMIT order is placed.
    """
    order_type = "MARKET" if price is None else "LIMIT"
    for attempt in range(1, retries + 1):
        try:
            order_id = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange="NFO",
                tradingsymbol=tradingsymbol,
                transaction_type=transaction_type,
                quantity=quantity,
                product="MIS",
                order_type=order_type,
                price=price
            )
            logging.info(f"Order placed: {tradingsymbol} {transaction_type} QTY:{quantity} Price:{price} ID:{order_id}")
            return order_id
        except KiteException as e:
            logging.error(f"Attempt {attempt}/{retries} - Failed to place order for {tradingsymbol} {transaction_type}: {e}")
            time.sleep(1)  # Brief pause before retrying
    logging.error(f"All attempts failed for order: {tradingsymbol} {transaction_type}")
    return None

def get_positions():
    """
    Fetch and return the current positions.
    """
    try:
        positions = kite.positions()
        return positions
    except Exception as e:
        logging.error(f"Failed to fetch positions: {e}")
        return {"day": [], "net": []}

def close_all_positions():
    """
    Close all open day positions by placing reverse orders.
    """
    positions = get_positions()
    if "day" in positions:
        for pos in positions["day"]:
            if pos["quantity"] != 0:
                # Determine reverse transaction type based on current quantity.
                txn_type = "BUY" if pos["quantity"] < 0 else "SELL"
                qty = abs(pos["quantity"])
                place_order(pos["tradingsymbol"], txn_type, qty)
                logging.info(f"Closed position: {pos['tradingsymbol']} Quantity: {pos['quantity']}")
    else:
        logging.info("No day positions found to close.")

def calculate_pnl():
    """
    Calculate and return the total PNL for day positions.
    """
    positions = get_positions()
    pnl = 0
    for pos in positions.get("day", []):
        pnl += pos.get("pnl", 0)
    logging.info(f"Calculated PNL: {pnl}")
    return pnl

# ==================== STRATEGY EXECUTION ====================
def execute_iron_condor():
    """
    Initiate the Iron Condor strategy by:
      - Checking market hours.
      - Fetching the ATM price and calculating strikes.
      - Constructing option symbols.
      - Placing the required orders.
    """
    if not is_market_open():
        logging.error("Market not open. Cannot execute strategy.")
        return None

    underlying_symbol = "NSE:NIFTY 50" if UNDERLYING == "NIFTY" else "NSE:BANKNIFTY"
    atm_price = get_live_price(underlying_symbol)
    if atm_price is None:
        logging.error("Could not fetch ATM price. Aborting strategy.")
        return None

    atm_strike = round(atm_price / 50) * 50
    strikes = calculate_strikes(atm_strike)
    expiry = get_next_expiry()

    short_put_symbol = construct_option_symbol(UNDERLYING, expiry, strikes["short_put"], "PE")
    long_put_symbol = construct_option_symbol(UNDERLYING, expiry, strikes["long_put"], "PE")
    short_call_symbol = construct_option_symbol(UNDERLYING, expiry, strikes["short_call"], "CE")
    long_call_symbol = construct_option_symbol(UNDERLYING, expiry, strikes["long_call"], "CE")

    # Place orders (here, MARKET orders are used for simplicity).
    place_order(short_put_symbol, "SELL", TOTAL_QUANTITY)
    place_order(long_put_symbol, "BUY", TOTAL_QUANTITY)
    place_order(short_call_symbol, "SELL", TOTAL_QUANTITY)
    place_order(long_call_symbol, "BUY", TOTAL_QUANTITY)

    logging.info("Iron Condor strategy initiated.")
    return {
        "short_put_symbol": short_put_symbol,
        "long_put_symbol": long_put_symbol,
        "short_call_symbol": short_call_symbol,
        "long_call_symbol": long_call_symbol,
        "entry_time": datetime.datetime.now(IST),
        "trail_base": 0
    }

def monitor_and_adjust(context):
    """
    Monitor the open positions and adjust the strategy based on PNL and time.
      - Exits all positions if target profit or max loss is hit.
      - Implements a trailing stop logic.
      - Exits positions if the market is about to close.
    """
    if context is None:
        return False

    pnl = calculate_pnl()
    logging.info(f"Current PNL: {pnl}")

    # Exit conditions based on profit or loss limits.
    if pnl >= TARGET_PROFIT:
        logging.info("Target profit reached. Exiting all positions.")
        close_all_positions()
        return False
    if pnl <= MAX_LOSS:
        logging.info("Max loss limit reached. Exiting all positions.")
        close_all_positions()
        return False

    # Trailing stop logic.
    if pnl > TRAIL_PROFIT_TRIGGER and context["trail_base"] == 0:
        context["trail_base"] = TRAIL_PROFIT_TRIGGER
        logging.info("Trailing profit trigger reached. Locking in profits.")

    if context["trail_base"] > 0 and pnl < context["trail_base"]:
        logging.info("Trailing stop triggered. Exiting positions.")
        close_all_positions()
        return False

    if context["trail_base"] > 0 and pnl > (context["trail_base"] + TRAIL_AMOUNT):
        context["trail_base"] = pnl - TRAIL_AMOUNT
        logging.info(f"Trailing base updated to: {context['trail_base']}")

    # Exit if the market is about to close.
    if datetime.datetime.now(IST).time() > MARKET_END:
        logging.info("Market closing soon. Exiting all positions.")
        close_all_positions()
        return False

    return True

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    logging.info("Starting Iron Condor Strategy")
    strategy_context = execute_iron_condor()

    try:
        while True:
            if strategy_context is None:
                logging.error("Strategy initiation failed. Exiting.")
                break

            if not is_market_open():
                logging.info("Market closed. Closing positions if any.")
                close_all_positions()
                break

            if not monitor_and_adjust(strategy_context):
                # Either stop conditions met or positions closed.
                break

            time.sleep(60)  # Wait 1 minute before next check
    except KeyboardInterrupt:
        logging.info("Keyboard Interrupt detected. Closing positions and exiting.")
        close_all_positions()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        close_all_positions()
