import schedule
import time
from kiteconnect import KiteConnect
from datetime import datetime, time as dt_time

# Your Zerodha Kite API credentials
api_key = "your_api_key"
api_secret = "your_api_secret"
access_token = "your_access_token"  # Obtain through login flow

# Initialize KiteConnect
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)


def check_market_and_trade():
    """
    Checks market stats and decides whether to place or exit positions
    based on your strategy criteria.
    """
    print(f"Checking market stats at {datetime.now()}")
    # Implement your logic here
    # 1. Fetch market data
    # 2. Decide whether to buy/sell based on your criteria
    # 3. Place or exit positions as needed


def run_during_market_hours():
    """
    Function to run the check_market_and_trade function during market hours.
    """
    now = datetime.now().time()
    market_start = dt_time(9, 15)
    market_end = dt_time(15, 30)

    if market_start <= now <= market_end:
        check_market_and_trade()
    else:
        print(f"Market closed at {now}. Service sleeping...")


# Schedule the task to run every 10 minutes during market hours
schedule.every(10).minutes.do(run_during_market_hours)

while True:
    schedule.run_pending()
    time.sleep(1)
