# main.py
"""Main script to run the Iron Condor trading strategy live."""

import time
from datetime import datetime
from config import ENTRY_DAYS, ENTRY_TIME, PROTECTION_DISTANCE
from api_helper import get_options_chain, place_option_order
from strategy import check_entry_conditions, select_strikes, calculate_lots, calculate_net_credit, \
    round_to_nearest_strike
from utils import is_market_open, log_trade
from config import STOP_LOSS_MULTIPLIER, ADJUSTMENT_DISTANCE, ADJUSTMENT_MIN_CREDIT
from api_helper import place_order, get_current_nifty_price

def run_trading_service():
    """Execute the Iron Condor strategy in live trading."""
    print("Starting Iron Condor trading service...")
    while True:
        now = datetime.now()
        if (now.strftime("%A") in ENTRY_DAYS and is_market_open() and
            now.strftime("%H:%M") == ENTRY_TIME):
            print(f"Checking entry at {now}...")
            options_chain = get_options_chain()
            if check_entry_conditions(options_chain):
                current_price = get_current_nifty_price()
                strikes = select_strikes(current_price)
                lots = calculate_lots()
                order_details = {"strikes": strikes, "lots": lots}
                order_ids = place_order(order_details)
                if order_ids:
                    log_trade({"entry_time": str(now), "strikes": strikes, "lots": lots, "order_ids": order_ids})
                    print("Position entered. Monitoring...")
                    monitor_position(order_details)  # Implement this
            time.sleep(24 * 60 * 60)  # Wait until next day
        time.sleep(60)  # Check every minute

def monitor_position(order_details):
    """Monitor the position for stop-loss and adjustments."""
    initial_credit = calculate_net_credit(get_options_chain())  # Fetch at entry
    while True:
        current_price = get_current_nifty_price()
        # Placeholder: Fetch current premiums and calculate loss
        loss = 0  # Implement premium difference calculation
        if loss >= initial_credit * STOP_LOSS_MULTIPLIER:
            exit_spread(order_details)  # Implement exit logic
            new_strikes = select_adjustment_strikes(current_price)
            new_order = {"strikes": new_strikes, "lots": order_details["lots"]}
            if calculate_net_credit(get_options_chain()) >= ADJUSTMENT_MIN_CREDIT:
                place_order(new_order)
                log_trade({"adjustment_time": str(datetime.now()), "strikes": new_strikes})
            break
        time.sleep(60)

def select_adjustment_strikes(current_price):
    """Select new strikes for adjustment."""
    sold_call = round_to_nearest_strike(current_price + ADJUSTMENT_DISTANCE)
    bought_call = round_to_nearest_strike(sold_call + PROTECTION_DISTANCE)
    sold_put = round_to_nearest_strike(current_price - ADJUSTMENT_DISTANCE)
    bought_put = round_to_nearest_strike(sold_put - PROTECTION_DISTANCE)
    return {"sold_call": sold_call, "bought_call": bought_call, "sold_put": sold_put, "bought_put": bought_put}


def exit_spread(order_details, side):
    """Exit the specified spread (call or put) in an Iron Condor strategy.

    Args:
        order_details (dict): Contains 'strikes' (dict of strike prices) and 'lots' (int).
        side (str): 'call' to exit the call spread, 'put' to exit the put spread.
    """
    lots = order_details["lots"]
    if side == "call":
        # Close the call spread
        # Buy back the sold call to close the short position
        place_option_order(order_details["strikes"]["sold_call"], "CE", "BUY", lots)
        # Sell the bought call to close the long position
        place_option_order(order_details["strikes"]["bought_call"], "CE", "SELL", lots)
    elif side == "put":
        # Close the put spread
        # Buy back the sold put to close the short position
        place_option_order(order_details["strikes"]["sold_put"], "PE", "BUY", lots)
        # Sell the bought put to close the long position
        place_option_order(order_details["strikes"]["bought_put"], "PE", "SELL", lots)
    else:
        raise ValueError("Invalid side: must be 'call' or 'put'")

if __name__ == "__main__":
    run_trading_service()