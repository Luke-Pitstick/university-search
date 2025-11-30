import redis

def clear_redis(redis_url, spider_name):
    r = redis.from_url(redis_url)
    r.delete(f"{spider_name}:start_urls")
    r.delete(f"{spider_name}:dupefilter")
    r.delete(f"{spider_name}:requests")
    r.delete(f"{spider_name}:items")

def add_to_redis(start_url, redis_url, spider_name):
    r = redis.from_url(redis_url)
    key = f"{spider_name}:start_urls"
    r.lpush(key, start_url)