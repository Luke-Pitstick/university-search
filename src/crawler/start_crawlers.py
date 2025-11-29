import json
import sys
import redis
from scrapy.crawler import CrawlerProcess
from crawler.spiders.university_spider import UniversitySpider


def add_university_name(config, base_url):
    university_name = base_url.replace("https://", "")
    university_name = university_name.replace("www.", "")
    university_name = university_name.replace("/", "")
    university_name = university_name.replace(".edu", "")
    
    config["settings"]["UNIVERSITY_NAME"] = university_name
        

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

def load_config(path):
    with open(path, "r") as f:
        return json.load(f)

def main():
    if len(sys.argv) < 4:
        print("Usage: python create_crawlers.py <start_url> <count> <config.json> <test_mode>")
        return

    start_url = sys.argv[1]
    count = int(sys.argv[2])
    config_path = sys.argv[3]
    test_mode = sys.argv[4]

    config = load_config(config_path)
    add_university_name(config, start_url)
    
    if test_mode == "true":
        clear_redis(config["settings"]["REDIS_URL"], UniversitySpider.name)
        
    add_to_redis(start_url, config["settings"]["REDIS_URL"], UniversitySpider.name)

    print(redis.from_url(config["settings"]["REDIS_URL"]).lrange(f"{UniversitySpider.name}:start_urls", 0, -1))
    
    # Load Scrapy settings
    settings = config["settings"]


    # Run N concurrent crawlers
    process = CrawlerProcess(settings=settings)
    
    print(process.settings.get("LOG_LEVEL"))
    
    crawlers = []

    for i in range(count):
        print(f"Launching crawler #{i+1}")
        crawler = process.crawl(UniversitySpider)
        crawlers.append(crawler)

    process.start()


if __name__ == "__main__":
    main()
