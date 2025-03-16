# data_store.py
import os
import pickle
import datetime
import logging
import yfinance as yf
import pandas as pd

# ==================== CONFIGURATION ====================
# For NIFTY 50, Yahoo Finance uses '^NSEI'. Change this if needed.
TICKER = '^NSEI'
INTERVAL = '30m'  # Options include '1d' (daily), '1h', '15m', etc.

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_cache_filename(start_date, end_date, interval):
    """
    Generate a cache filename based on the ticker, date range, and interval.
    """
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    return f"historical_data_{TICKER}_{start_str}_{end_str}_{interval}.pkl"


def get_csv_filename(start_date, end_date, interval):
    """
    Generate a CSV filename based on the ticker, date range, and interval.
    """
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    # Remove characters that might not be allowed in filenames (e.g., '^')
    ticker_clean = TICKER.replace('^', '')
    return f"historical_data_{ticker_clean}_{start_str}_{end_str}_{interval}.csv"


def pull_and_store_data(start_date, end_date, interval=INTERVAL, force_refresh=False):
    """
    Download historical data for the specified ticker and store it locally in both
    Pickle and CSV formats.

    Args:
        start_date (datetime.datetime): Start date for the data.
        end_date (datetime.datetime): End date for the data.
        interval (str): Data interval (e.g., '1d' for daily data).
        force_refresh (bool): If True, force re-download even if a cache file exists.
    """
    pkl_filename = get_cache_filename(start_date, end_date, interval)
    csv_filename = get_csv_filename(start_date, end_date, interval)

    if os.path.exists(pkl_filename) and os.path.exists(csv_filename) and not force_refresh:
        logging.info(
            f"Data files {pkl_filename} and {csv_filename} already exist. Use force_refresh=True to refresh data.")
        return

    logging.info(f"Downloading historical data for {TICKER} from {start_date} to {end_date} at interval '{interval}'.")

    # Download data using yfinance
    data = yf.download(TICKER, start=start_date, end=end_date, interval=interval)

    if data.empty:
        logging.error("No data was downloaded. Check the ticker and date range.")
        return

    # Save the data to CSV format
    data.to_csv(csv_filename)
    logging.info(f"Historical data saved in CSV format to {csv_filename}.")

    # Convert the DataFrame to a list of dictionaries (each representing a candle)
    candles = []
    for dt, row in data.iterrows():
        candle = {
            "date": dt.to_pydatetime(),  # Convert Timestamp to datetime
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"],
            "volume": row["Volume"]
        }
        candles.append(candle)

    # Save the candles list to a Pickle file
    with open(pkl_filename, "wb") as f:
        pickle.dump(candles, f)

    logging.info(f"Historical data downloaded and stored in {pkl_filename}.")


if __name__ == "__main__":
    # Set the time range for data collection.
    start_date = datetime.datetime(2025, 1, 1)
    end_date = datetime.datetime(2025, 1, 31)
    pull_and_store_data(start_date, end_date, interval=INTERVAL)
