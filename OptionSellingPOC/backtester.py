# backtester.py
import os
import pickle
import datetime
import logging
import trade_zero as algo  # Import your production algo module

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Backtester:
    def __init__(self, data_file, start_date, end_date):
        """
        Initialize the backtester.
        - data_file: The path to the locally stored historical data file.
        - start_date, end_date: The time range to filter the stored data for backtesting.
        """
        self.data_file = data_file
        self.start_date = start_date
        self.end_date = end_date
        self.historical_data = []
        self.trade_log = []         # Records simulated order details
        self.simulated_positions = {}  # Tracks simulated positions
        self.strategy_context = None
        self.current_candle = None  # The "live" candle during simulation

    def load_historical_data(self):
        if not os.path.exists(self.data_file):
            logging.error(f"Data file {self.data_file} does not exist!")
            return
        with open(self.data_file, "rb") as f:
            all_data = pickle.load(f)
        # Filter candles by date. Each candle is expected to have a "date" key (a datetime object).
        self.historical_data = [candle for candle in all_data
                                if self.start_date <= candle["date"] <= self.end_date]
        logging.info(f"Loaded {len(self.historical_data)} candles from {self.data_file} "
                     f"for the period {self.start_date} to {self.end_date}.")

    # -------------- Simulation Functions -------------- #
    def sim_get_live_price(self, exchange_instrument):
        """Simulated live price: returns the 'close' price of the current candle."""
        if self.current_candle:
            return self.current_candle["close"]
        return None

    def sim_place_order(self, tradingsymbol, transaction_type, quantity, price=None, retries=3):
        """
        Simulate an order:
          - Assumes market orders are filled at the current candle's open price.
          - Records order details in the trade log.
          - Updates simulated positions.
        """
        if self.current_candle is None:
            logging.error("No current candle available to simulate order fill.")
            return None

        # Assume fill price equals the candle's open price.
        fill_price = self.current_candle["open"]
        order_details = {
            "tradingsymbol": tradingsymbol,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "fill_price": fill_price,
            "timestamp": self.current_candle["date"],
            "status": "filled"
        }
        self.trade_log.append(order_details)
        logging.info(f"Simulated order executed: {order_details}")

        # Update simulated positions (additive model)
        pos = self.simulated_positions.get(tradingsymbol, 0)
        if transaction_type.upper() == "BUY":
            self.simulated_positions[tradingsymbol] = pos + quantity
        else:
            self.simulated_positions[tradingsymbol] = pos - quantity

        # Return a simulated order ID.
        return f"SIM-{len(self.trade_log)}"

    def sim_get_positions(self):
        """Return simulated positions in a structure similar to the live version."""
        day_positions = []
        for symbol, qty in self.simulated_positions.items():
            pnl = 0  # You can extend this to calculate mark-to-market PNL.
            day_positions.append({"tradingsymbol": symbol, "quantity": qty, "pnl": pnl})
        return {"day": day_positions, "net": day_positions}

    def sim_close_all_positions(self):
        """Simulate closing all positions at the current candle's price."""
        for symbol, qty in list(self.simulated_positions.items()):
            if qty != 0:
                txn_type = "BUY" if qty < 0 else "SELL"
                self.sim_place_order(symbol, txn_type, abs(qty))
        self.simulated_positions = {}
        logging.info("Simulated closing of all positions.")

    def sim_calculate_pnl(self):
        """A simplified P&L calculation. Extend as needed."""
        return 0

    # -------------- Running the Backtest -------------- #
    def run_backtest(self):
        self.load_historical_data()
        if not self.historical_data:
            logging.error("No historical data available for backtesting.")
            return

        # Monkey-patch production functions with simulation functions.
        algo.get_live_price = self.sim_get_live_price
        algo.place_order = self.sim_place_order
        algo.get_positions = self.sim_get_positions
        algo.close_all_positions = self.sim_close_all_positions
        algo.calculate_pnl = self.sim_calculate_pnl
        # Override market open check to always return True in simulation.
        algo.is_market_open = lambda: True

        # Initiate the strategy (it now uses simulated functions).
        self.strategy_context = algo.execute_iron_condor()
        if self.strategy_context is None:
            logging.error("Strategy failed to execute in backtest mode.")
            return

        # Step through each historical candle and simulate the monitoring.
        for candle in self.historical_data:
            self.current_candle = candle
            logging.info(f"Simulated time: {candle['date']}, Price: {candle['close']}")
            cont = algo.monitor_and_adjust(self.strategy_context)
            if not cont:
                logging.info("Strategy signaled an exit condition at simulated time.")
                break

        self.print_summary()

    def print_summary(self):
        print("=== Backtesting Summary ===")
        print("\nTrade Log:")
        for trade in self.trade_log:
            print(trade)
        final_pnl = algo.calculate_pnl()
        print(f"\nFinal simulated PNL: {final_pnl}")

if __name__ == "__main__":
    # Specify the data file created by data_store.py (adjust the filename as needed).
    data_file = "historical_data_20230101_20230131_day.pkl"
    # Set the time range for the backtest.
    start_date = datetime.datetime(2023, 1, 10)
    end_date = datetime.datetime(2023, 1, 20)
    backtester = Backtester(data_file, start_date, end_date)
    backtester.run_backtest()
