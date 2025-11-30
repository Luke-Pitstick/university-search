import redis

def clear_redis(redis_url, count):
    r = redis.from_url(redis_url)
    print(f"Clearing Redis for {redis_url}")
    r.flushall()
    print(f"Cleared Redis for {redis_url}")

def add_to_redis(start_url, redis_url, count):
    r = redis.from_url(redis_url)
    for i in range(count + 1):
        key = f"university_spider_{i}:start_urls"
        r.lpush(key, start_url)
        print(f"Added {start_url} to Redis for {redis_url} {i}")