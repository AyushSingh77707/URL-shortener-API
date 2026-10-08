import redis 
import os

redis_client=redis.Redis(
    host=os.getenv("REDIS_HOST","127.0.0.1"),
    port=6379,
    decode_responses=True,
    protocol=2
)

