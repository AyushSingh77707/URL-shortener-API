import time
from app.core.redis import redis_client


def blacklist_token(payload:dict):
    ttl=payload["exp"]-int(time.time())
    if ttl>0:
        redis_client.set(f"blacklist:{payload['jti']}","1",ttl)

def is_blacklisted(jti:str):
    return redis_client.exists(f"blacklist:{jti}")
        




