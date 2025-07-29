import pytest
from redis.asyncio import Redis

@pytest.mark.asyncio
async def test_local_redis():
    redis = Redis.from_url("redis://localhost:6379", decode_responses=True)

    key = "test:sensor35"
    data = {"temperatura": "10.5", "humedad": "70", "co2": "800", "presion": "1000"}

    await redis.hset(key, mapping=data)
    resultado = await redis.hgetall(key)

    assert resultado == data

    #await redis.delete(key)
    await redis.aclose()
