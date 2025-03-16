# data_store.py
import os
import pickle
import datetime
import logging
from kiteconnect import KiteConnect
from kiteconnect.exceptions import KiteException

# ==================== CONFIGURATION ====================
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"
REQUEST_TOKEN = "your_request_token"
# Update the instrument token as needed (example token for NIFTY 50)
INSTRUMENT_TOKEN = 256265
INTERVAL = "day"  # can be "minute", "day", etc.

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_cache_filename(start_date, end_date, interval):
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    return f"historical_data_{start_str}_{end_str}_{interval}.pkl"

def pull_and_store_data(start_date, end_date, interval=INTERVAL, force_refresh=False):
    # Initialize KiteConnect
    kite = KiteConnect(api_key=API_KEY)
    try:
        session_data = kite.generate_session(REQUEST_TOKEN, api_secret=API_SECRET)
        kite.set_access_token(session_data["access_token"])
        logging.info("Session generated successfully!")
    except KiteException as e:
        logging.error(f"Error generating session: {e}")
        return

    filename = get_cache_filename(start_date, end_date, interval)
    if os.path.exists(filename) and not force_refresh:
        logging.info(f"Data file {filename} already exists. Use force_refresh=True to refresh data.")
        return

    try:
        data = kite.historical_data(INSTRUMENT_TOKEN, start_date, end_date, interval)
        with open(filename, "wb") as f:
            pickle.dump(data, f)
        logging.info(f"Historical data retrieved and stored in {filename}.")
    except KiteException as e:
        logging.error(f"Error fetching historical data: {e}")

if __name__ == "__main__":
    # Set the time range for data collection.
    start_date = datetime.datetime(2023, 1, 1)
    end_date = datetime.datetime(2023, 1, 31)
    pull_and_store_data(start_date, end_date, interval=INTERVAL)
