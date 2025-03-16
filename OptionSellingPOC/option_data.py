# option_chain_store.py
import os
import pickle
import datetime
import logging
import yfinance as yf
import pandas as pd

# -------------------- Configuration --------------------
# Change the TICKER below as needed. For example:
# For a U.S. stock: TICKER = "AAPL"
# For the NIFTY 50 index: TICKER = "^NSEI" (note: option chain data for indices may be limited)
TICKER = "^NSEI"
# Set the desired expiration date (as a datetime object)
# Ensure that the expiration date is one of the dates returned by yf.Ticker(TICKER).options
EXPIRATION_DATE = datetime.datetime(2025, 2, 6)  # Example date; change as needed

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# -------------------- Utility Functions --------------------
def get_cache_filename(ticker, expiration_date):
    """
    Generate a cache filename (Pickle file) for the option chain data.
    """
    exp_str = expiration_date.strftime('%Y-%m-%d')
    # Remove characters that might be problematic in filenames
    ticker_clean = ticker.replace('^', '')
    return f"option_chain_{ticker_clean}_{exp_str}.pkl"


def get_csv_filenames(ticker, expiration_date):
    """
    Generate CSV filenames for the calls and puts data.
    """
    exp_str = expiration_date.strftime('%Y-%m-%d')
    ticker_clean = ticker.replace('^', '')
    calls_filename = f"calls_{ticker_clean}_{exp_str}.csv"
    puts_filename = f"puts_{ticker_clean}_{exp_str}.csv"
    return calls_filename, puts_filename


def pull_and_store_option_chain(ticker, expiration_date, force_refresh=False):
    """
    Download option chain data for the specified ticker and expiration date from Yahoo Finance,
    then store the data as both a Pickle file and as CSV files.

    Args:
        ticker (str): The ticker symbol (e.g., "AAPL" or "^NSEI").
        expiration_date (datetime.datetime): The expiration date for which to download data.
        force_refresh (bool): If True, re-download even if local files exist.

    Returns:
        dict: A dictionary with two keys, "calls" and "puts", each containing a Pandas DataFrame.
    """
    pkl_filename = get_cache_filename(ticker, expiration_date)
    calls_csv, puts_csv = get_csv_filenames(ticker, expiration_date)

    if (os.path.exists(pkl_filename) and os.path.exists(calls_csv) and os.path.exists(puts_csv)
            and not force_refresh):
        logging.info(f"Using cached data from {pkl_filename} and CSV files.")
        with open(pkl_filename, 'rb') as f:
            option_chain = pickle.load(f)
        return option_chain

    logging.info(f"Downloading option chain data for {ticker} for expiration {expiration_date.strftime('%Y-%m-%d')}.")
    yf_ticker = yf.Ticker(ticker)

    # Yahoo Finance returns a list of available expiration dates as strings (YYYY-MM-DD).
    available_expirations = yf_ticker.options
    exp_str = expiration_date.strftime('%Y-%m-%d')
    if exp_str not in available_expirations:
        logging.error(
            f"Expiration date {exp_str} is not available for ticker {ticker}. Available expirations: {available_expirations}")
        return None

    # Retrieve option chain data for the given expiration.
    chain = yf_ticker.option_chain(exp_str)
    # chain.calls and chain.puts are Pandas DataFrames.
    option_chain = {"calls": chain.calls, "puts": chain.puts}

    # Save as CSV files for verification.
    chain.calls.to_csv(calls_csv, index=False)
    chain.puts.to_csv(puts_csv, index=False)
    logging.info(f"Option chain CSV files saved: {calls_csv}, {puts_csv}")

    # Save the dictionary to a Pickle file.
    with open(pkl_filename, "wb") as f:
        pickle.dump(option_chain, f)
    logging.info(f"Option chain data cached in Pickle file: {pkl_filename}")

    return option_chain


if __name__ == "__main__":
    # Example usage:
    option_data = pull_and_store_option_chain(TICKER, EXPIRATION_DATE, force_refresh=False)
    if option_data:
        print("=== Calls Data ===")
        print(option_data["calls"].head())
        print("\n=== Puts Data ===")
        print(option_data["puts"].head())
