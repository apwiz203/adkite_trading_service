# backtest.py
"""Module to backtest the Iron Condor strategy."""

import pandas as pd
from config import CAPITAL, BACKTEST_PERIOD_MONTHS
from strategy import check_entry_conditions, select_strikes, calculate_lots
from utils import log_trade


def load_historical_data(file_path="data/nifty_options_data.csv"):
    """Load historical options data (assumes CSV format)."""
    return pd.read_csv(file_path)


def run_backtest():
    """Run backtest on historical data."""
    print(f"Running backtest for {BACKTEST_PERIOD_MONTHS} months...")
    data = load_historical_data()
    end_date = pd.to_datetime("today")
    start_date = end_date - pd.DateOffset(months=BACKTEST_PERIOD_MONTHS)
    data = data[(data["date"] >= start_date) & (data["date"] <= end_date)]

    total_profit = 0
    for date, day_data in data.groupby("date"):
        if check_entry_conditions(day_data):  # Adjust to use historical data
            current_price = day_data["spot_price"].iloc[0]
            strikes = select_strikes(current_price)
            lots = calculate_lots()
            profit = lots * 100  # Simplified; replace with P&L calculation
            total_profit += profit
            log_trade({"date": date, "strikes": strikes, "profit": profit})
    print(f"Backtest completed. Total profit: {total_profit} INR")
    return total_profit


if __name__ == "__main__":
    run_backtest()