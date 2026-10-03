from slowapi import Limiter
from slowapi.util import get_remote_address  #users ip address

#creating a limiter
limiter=Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    strategy="fixed-window",
    headers_enabled=True
    )

