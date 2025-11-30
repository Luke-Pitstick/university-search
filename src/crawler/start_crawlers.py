import json
import sys
import redis
from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess
from spiders.university_spider import UniversitySpider
from utils.redis_utiils import clear_redis, add_to_redis
from utils.general_utils import add_university_name


        

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

    # Extract domain for all crawlers to share
    parsed = urlparse(start_url)
    base_domain = parsed.netloc
    if base_domain.startswith("www."):
        base_domain = base_domain[4:]

    # Run N concurrent crawlers
    process = CrawlerProcess(settings=settings)
    
    print(process.settings.get("LOG_LEVEL"))
    
    crawlers = []

    for i in range(count):
        print(f"Launching crawler #{i+1}")
        crawler = process.crawl(UniversitySpider, crawler_id=i+1, allowed_domains=[base_domain])
        crawlers.append(crawler)

    process.start()


if __name__ == "__main__":
    main()
