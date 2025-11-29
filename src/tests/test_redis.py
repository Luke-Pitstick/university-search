import redis
import pickle
import sys
import os
from urllib.parse import urlparse
from collections import Counter

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

def inspect_and_clear_queue(clear=False):
    try:
        r = redis.from_url("redis://localhost:6379/0")
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        return

    print("--- REDIS INSPECTION ---")
    
    # 1. Check keys
    keys = [k.decode() for k in r.keys("university_crawler*")]
    print(f"Found keys: {keys}")

    # 2. Check Requests Queue
    queue_key = "university_crawler:requests"
    
    count = 0
    if r.exists(queue_key):
        count = r.llen(queue_key)
        print(f"\nQueue '{queue_key}' has {count} items.")
    else:
        print(f"\nQueue '{queue_key}' is empty or does not exist.")

    # 3. Analyze content (only if not clearing immediately or if we want to see what we're deleting)
    if count > 0:
        print("\nAnalyzing first 50 items in the queue...")
        items = r.lrange(queue_key, 0, 50)
        domains = Counter()
        
        for item in items:
            try:
                # Scrapy-redis requests are pickled
                req = pickle.loads(item)
                
                url = None
                if hasattr(req, 'url'):
                    url = req.url
                elif isinstance(req, dict) and 'url' in req:
                    url = req['url']
                
                if url:
                    domain = urlparse(url).netloc
                    domains[domain] += 1
                else:
                    # print(f"  - [Could not extract URL from {type(req)}]")
                    pass
                    
            except Exception as e:
                # print(f"  - [Error unpickling: {e}]")
                pass

        print("\nDomain distribution in sample:")
        for domain, count in domains.most_common():
            print(f"  {domain}: {count}")

    # 4. Clear queue if requested
    if clear:
        print("\n--- CLEARING QUEUE ---")
        keys_to_delete = r.keys("university_crawler*")
        if keys_to_delete:
            r.delete(*keys_to_delete)
            print(f"Deleted keys: {[k.decode() for k in keys_to_delete]}")
        else:
            print("No keys to delete.")
        
        # Verify
        remaining_keys = r.keys("university_crawler*")
        if not remaining_keys:
            print("Redis queue cleared successfully.")
        else:
            print(f"Warning: Some keys remain: {remaining_keys}")

if __name__ == "__main__":
    # Check for --clear argument
    should_clear = "--clear" in sys.argv
    inspect_and_clear_queue(clear=should_clear)
