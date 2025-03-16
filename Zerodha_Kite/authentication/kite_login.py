from kiteconnect import KiteConnect
import logging

# Initialize KiteConnect
api_key = "your_api_key"
kite = KiteConnect(api_key=api_key)

# Request token (you need to generate this using your account)
request_token = "your_request_token"

# Generate session
data = kite.generate_session(request_token, api_secret="your_api_secret")
kite.set_access_token(data["access_token"])

# Save access token for future use
with open("access_token.txt", "w") as file:
    file.write(data["access_token"])

logging.info("Login successful!")
