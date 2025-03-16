from kiteconnect import KiteConnect
from Zerodha.Connection.zerodha_automation.return_request_token import get_request_token

def connect(credentials: dict, kite: KiteConnect):
    request_token = get_request_token(credentials, kite)
    data = kite.generate_session(request_token, api_secret=credentials['api_secret'])
    kite.set_access_token(data["access_token"])
