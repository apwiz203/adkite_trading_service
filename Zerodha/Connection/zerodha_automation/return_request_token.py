import kiteconnect
import requests
import re
import onetimepass as otp
from urllib.parse import urlparse, parse_qs
from kiteconnect import KiteConnect


def get_request_token(credentials: dict, kite: KiteConnect) -> str:
    """Use provided credentials and return request token.

    Args:
        credentials: Login credentials for Kite
        kite: kite session

    Returns:
        Request token for the provided credentials
    """

    session = requests.Session()
    response = session.get(kite.login_url())

    # User login POST request
    login_payload = {
        "user_id": credentials["username"],
        "password": credentials["password"],
    }
    login_response = session.post("https://kite.zerodha.com/api/login", login_payload)

    # TOTP POST request
    totp_payload = {
        "user_id": credentials["username"],
        "request_id": login_response.json()["data"]["request_id"],
        "twofa_value": otp.get_totp(credentials["totp_key"]),
        "twofa_type": "totp",
        "skip_session": True,
    }
    totp_response = session.post("https://kite.zerodha.com/api/twofa", totp_payload)

    # Extract request token from redirect URL
    try:
        # Extracting query parameters from redirect URL
        response = session.get(kite.login_url())
        parse_result = urlparse(response.url)
        query_parms = parse_qs(parse_result.query)
    except Exception as e:
        # Extracting query parameters from error message in case of error
        pattern = r"request_token=[A-Za-z0-9]+"
        # Extracting request token
        query_parms = parse_qs(re.findall(pattern, e.__str__())[0])
    request_token = query_parms["request_token"][0]

    return request_token
