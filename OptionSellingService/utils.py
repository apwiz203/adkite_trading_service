# utils.py
"""Utility functions for the Iron Condor trading strategy."""

import datetime

def is_market_open():
    """Check if the market is open (9:15 AM - 3:30 PM IST)."""
    now = datetime.datetime.now()
    market_open = datetime.time(9, 15)
    market_close = datetime.time(15, 30)
    return market_open <= now.time() <= market_close and now.weekday() < 5 and not is_market_holiday(now.date())

def is_market_holiday(date):
    """Check if the date is a market holiday (placeholder)."""
    return False  # Replace with holiday list or API

def log_trade(trade_details):
    """Log trade details to a file."""
    with open("trade_log.txt", "a") as f:
        f.write(f"{datetime.datetime.now()}: {trade_details}\n")