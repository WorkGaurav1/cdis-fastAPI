from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize the rate limiter globally. 
# This uses the client's IP address (get_remote_address) to track requests.
limiter = Limiter(key_func=get_remote_address)
