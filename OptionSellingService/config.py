# config.py
"""Configuration variables for the Iron Condor trading strategy."""

# Trading schedule
ENTRY_DAYS = ["Tuesday", "Wednesday"]  # Days to enter trades
ENTRY_TIME = "10:45"  # Time to enter trades (24-hour format)

# Capital management
CAPITAL = 1000000  # Total capital in INR (₹10,00,000)
INITIAL_ALLOCATION = 0.7  # 70% of capital for initial position (₹7,00,000)
RESERVE_ALLOCATION = 0.3  # 30% reserved for adjustments (₹3,00,000)

# Entry conditions
IV_MIN = 20  # Minimum implied volatility (%)
IV_MAX = 95  # Maximum implied volatility (%)
MIN_CREDIT = 100  # Minimum net credit per lot (INR)

# Strike selection
STRIKE_DISTANCE = 150  # Minimum distance from current price for sold strikes
PROTECTION_DISTANCE = 200  # Distance from sold strikes for bought strikes
ADJUSTMENT_DISTANCE = 200  # Distance for adjustment strikes

# Risk management
STOP_LOSS_MULTIPLIER = 3  # Stop-loss at 3x initial credit
ADJUSTMENT_MIN_CREDIT = 30  # Minimum credit for adjustment spreads (INR)

# Backtesting parameters
BACKTEST_PERIOD_MONTHS = 12  # Duration for backtesting

# Zerodha Kite API credentials
API_KEY = "your_api_key"  # Replace with your API key
API_SECRET = "your_api_secret"  # Replace with your API secret
ACCESS_TOKEN = "your_access_token"  # Replace with generated token
# Replace with your actual API key
ALPHA_VANTAGE_API_KEY = "YOUR_API_KEY_HERE"