import redis

def clear_redis(redis_url):
    r = redis.from_url(redis_url)
    print(f"Clearing Redis for {redis_url}")
    r.flushall()
    print(f"Cleared Redis for {redis_url}")

def add_to_redis(start_url, redis_url, count, university_name):
    r = redis.from_url(redis_url)
    # Crawler IDs are 1-based in start_crawlers.py
    for i in range(1, count + 1):
        # Must match the key format in UniversitySpider
        crawler_name = f"university_spider_{university_name}_{i}"
        key = f"{crawler_name}:start_urls"
        r.lpush(key, start_url)
        print(f"Added {start_url} to Redis key {key}")
