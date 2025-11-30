from redis_utils import clear_redis

redis_url = "redis://localhost:6379/0"
count = 10
clear_redis(redis_url)