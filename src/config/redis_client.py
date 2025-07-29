import redis.asyncio as aioredis
import os
from dotenv import load_dotenv

load_dotenv()

_redis_client = None

async def get_redis_client():
    global _redis_client
    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            raise EnvironmentError("REDIS_URL no está definido. Asegúrate de configurarlo en el entorno.")

        _redis_client = aioredis.from_url(
            redis_url,
            decode_responses=True
        )
    return _redis_client