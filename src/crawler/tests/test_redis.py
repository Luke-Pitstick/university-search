import redis
from utils.redis_utils import clear_redis

def test_redis():
    clear_redis("redis://localhost:6379/0", 10)

if __name__ == "__main__":
    test_redis()