# strategy.py
"""Core logic for the Iron Condor trading strategy."""
import requests

from config import IV_MIN, IV_MAX, MIN_CREDIT, CAPITAL, INITIAL_ALLOCATION, STRIKE_DISTANCE, PROTECTION_DISTANCE, \
    ALPHA_VANTAGE_API_KEY
from api_helper import get_current_nifty_price, get_margin_required


def check_entry_conditions(options_chain, current_price, expiry_date):
    """Verify if entry conditions are met."""
    strikes = select_strikes(current_price)
    avg_iv = calculate_average_iv(options_chain, strikes)
    net_credit = calculate_net_credit(options_chain, strikes)
    has_major_events = check_economic_calendar(expiry_date)
    return (IV_MIN <= avg_iv <= IV_MAX and net_credit >= MIN_CREDIT and not has_major_events)


def calculate_lots():
    """Calculate number of lots based on capital and margin."""
    margin_per_lot = get_margin_required({"type": "Iron Condor"}, 1)
    available_capital = CAPITAL * INITIAL_ALLOCATION
    lots = int(available_capital // margin_per_lot)
    return max(lots, 1)  # Ensure at least 1 lot


def round_to_nearest_strike(price):
    """Round price to the nearest valid strike (e.g., multiple of 50)."""
    return round(price / 50) * 50  # Adjust based on your instrument's strike intervals


def select_strikes(current_price):
    """Select OTM strikes for the Iron Condor."""
    sold_call = round_to_nearest_strike(current_price + STRIKE_DISTANCE)
    bought_call = round_to_nearest_strike(sold_call + PROTECTION_DISTANCE)
    sold_put = round_to_nearest_strike(current_price - STRIKE_DISTANCE)
    bought_put = round_to_nearest_strike(sold_put - PROTECTION_DISTANCE)
    return {
        "sold_call": sold_call,
        "bought_call": bought_call,
        "sold_put": sold_put,
        "bought_put": bought_put
    }


def calculate_average_iv(options_chain, current_price, strike_range=200):
    """Calculate average IV for options within a strike range of the current price."""
    relevant_options = [
        opt for opt in options_chain
        if abs(opt["strike"] - current_price) <= strike_range
    ]
    if not relevant_options:
        return 0
    total_iv = sum(opt["iv"] for opt in relevant_options)
    return total_iv / len(relevant_options)


def get_premium(options_chain, strike, option_type):
    """Get the premium for a specific strike and option type."""
    for opt in options_chain:
        if opt["strike"] == strike and opt["option_type"] == option_type:
            return opt["premium"]
    return None  # Return None if no matching option is found


def calculate_fees(gross_credit):
    """Estimate taxes and brokerage fees (placeholder)."""
    return 10  # Replace with actual fee logic


def calculate_net_credit(options_chain):
    """Calculate the net credit for the Iron Condor."""
    current_price = get_current_nifty_price()  # Assume this function exists
    strikes = select_strikes(current_price)

    sold_call_premium = get_premium(options_chain, strikes["sold_call"], "CE")
    bought_call_premium = get_premium(options_chain, strikes["bought_call"], "CE")
    sold_put_premium = get_premium(options_chain, strikes["sold_put"], "PE")
    bought_put_premium = get_premium(options_chain, strikes["bought_put"], "PE")

    # Check for missing premiums
    if None in [sold_call_premium, bought_call_premium, sold_put_premium, bought_put_premium]:
        return 0  # Return 0 if any premium is unavailable

    call_spread_credit = sold_call_premium - bought_call_premium
    put_spread_credit = sold_put_premium - bought_put_premium
    total_credit = call_spread_credit + put_spread_credit

    # Adjust for lot size (assume lot_size is a defined constant, e.g., 50 for Nifty)
    return total_credit * 75


def check_economic_calendar(expiry_date):
    """Check for major economic events before expiry."""
    url = f"https://www.alphavantage.co/query?function=ECONOMIC_CALENDAR&symbol=INDIA&apikey={ALPHA_VANTAGE_API_KEY}"
    try:
        response = requests.get(url)
        events = response.json().get("economic_calendar", [])
        major_events = [event for event in events if event["impact"] == "High" and event["date"] <= expiry_date]
        return len(major_events) > 0
    except Exception as e:
        print(f"Error fetching economic calendar: {e}")
        return False


def check_entry_conditions(options_chain, current_price, expiry_date):
    """Verify if entry conditions are met."""
    strikes = select_strikes(current_price)
    avg_iv = calculate_average_iv(options_chain, strikes)
    net_credit = calculate_net_credit(options_chain, strikes)
    has_major_events = check_economic_calendar(expiry_date)
    return (IV_MIN <= avg_iv <= IV_MAX and net_credit >= MIN_CREDIT and not has_major_events)