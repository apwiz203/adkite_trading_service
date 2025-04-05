def calculate_iron_condor_margin_approx(short_put_strike, long_put_strike, short_call_strike,
                                        long_call_strike, short_put_premium, long_put_premium,
                                        short_call_premium, long_call_premium, lot_size,
                                        underlying_price=None, multiplier=5.5):
    """
    Approximates the margin for an Iron Condor on Nifty.
    Returns maximum loss and a rough margin estimate.

    Parameters:
    - short_put_strike, long_put_strike, short_call_strike, long_call_strike: Strike prices
    - short_put_premium, long_put_premium, short_call_premium, long_call_premium: Premiums
    - lot_size: Number of units per contract (e.g., 75 for Nifty)
    - underlying_price: Current Nifty price (optional, for alternative method)
    - multiplier: Factor to adjust max loss to approximate SPAN margin (default 5.5)

    Returns:
    - max_loss: Theoretical maximum loss
    - estimated_margin: Rough margin estimate
    """
    # Calculate spread widths
    put_spread_width = short_put_strike - long_put_strike
    call_spread_width = long_call_strike - short_call_strike
    max_spread_width = max(put_spread_width, call_spread_width)

    # Calculate net premium received
    net_premium = (short_put_premium + short_call_premium) - (long_put_premium + long_call_premium)

    # Maximum loss per lot
    max_loss_per_lot = max_spread_width - net_premium
    max_loss = max_loss_per_lot * lot_size

    # Estimate margin using multiplier (based on example)
    estimated_margin = max_loss * multiplier

    # Alternative method: 5% of contract value (if underlying price provided)
    if underlying_price:
        contract_value_margin = 0.05 * underlying_price * lot_size
        return max_loss, max(estimated_margin, contract_value_margin)

    return max_loss, estimated_margin


# Example usage
short_put_strike = 22000
long_put_strike = 21800
short_call_strike = 23000
long_call_strike = 23200
short_put_premium = 11.55
long_put_premium = 5.05
short_call_premium = 7.6
long_call_premium = 2.4
lot_size = 75
underlying_price = 22400  # Optional

max_loss, estimated_margin = calculate_iron_condor_margin_approx(
    short_put_strike, long_put_strike, short_call_strike, long_call_strike,
    short_put_premium, long_put_premium, short_call_premium, long_call_premium,
    lot_size, underlying_price
)

print(f"Theoretical Maximum Loss: ₹{max_loss:.2f}")
print(f"Estimated Margin (Approximation): ₹{estimated_margin:.2f}")