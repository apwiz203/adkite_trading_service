from kiteconnect import KiteConnect

from Zerodha.Connection.ZerodhaConnection import connect


class RunAll:
    credentials = {
        "username": "login_id_here",
        "password": "password_here",
        "totp_key": "totp_key_here",
        "api_key": "api_key_here",
        "api_secret": "api_secret_here",
    }
    order_details = {
        "tradingsymbol": "",        # Tradingsymbol of the instrument ?
        "exchange": "",             # Name of the exchange (NSE, BSE, NFO, CDS, BCD, MCX)
        "transaction_type": "",     # BUY or SELL
        "order_type": "",           # Order type (MARKET, LIMIT etc.)
        "product": "",              # Margin product to use for the order (margins are blocked based on this) ?
        "quantity": "",             # Quantity to transact
        "price": "",                # The price to execute the order at (for LIMIT orders)
        "trigger_price": "",        # The price at which an order should be triggered (SL, SL-M)
        "disclosed_quantity": "",   # Quantity to disclose publicly (for equity trades)
        "validity": "",             # Order validity (DAY, IOC and TTL)
        "validity_ttl": "",         # Order life span in minutes for TTL validity orders
        "iceberg_legs": "",
                                    # Total number of legs for iceberg order type (number of legs per Iceberg should
                                    #  be between 2 and 10)
        "iceberg_quantity": "",     # Split quantity for each iceberg leg order (quantity/iceberg_legs)
        "auction_number": "",       # A unique identifier for a particular auction
        "tag": "",                  # An optional tag to apply to an order to identify it (alphanumeric, max 20 chars)
    }

    def run_all(self):
        kite = KiteConnect(api_key=self.credentials["api_key"])
        connect(credentials=self.credentials, kite=kite)

        ## buy order

        ## sell order
