import json
import sys
import redis
import warnings
from scrapy.exceptions import ScrapyDeprecationWarning
from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess
from spiders.university_spider import UniversitySpider
from utils.redis_utils import clear_redis, add_to_redis
from utils.general_utils import add_university_name
from utils.chroma_utils import clear_chroma_db

# Suppress Scrapy deprecation warnings from scrapy-redis
warnings.filterwarnings("ignore", category=ScrapyDeprecationWarning)



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
    #test_mode = sys.argv[4]

    config = load_config(config_path)
    config = config["settings"]
    config = add_university_name(config, start_url)
    
    # Check for test mode/clear cache (default to clearing Redis for fresh starts)
    # Pass "false" as 4th argument to resume a previous crawl
    should_clear = len(sys.argv) <= 4 or sys.argv[4].lower() != "false"
    
    if should_clear:
        print("Clearing Redis for fresh start...")
        clear_redis(config["REDIS_URL"])
        #clear_chroma_db("chroma_langchain_db/")
    
    add_to_redis(start_url, config["REDIS_URL"], count, config["UNIVERSITY_NAME"])

    


    config["ALLOWED_DOMAINS"] = start_url.split("/")[2]
    
    # FIX CONFIG FOR REDIS KEYS
    config["SCHEDULER_QUEUE_KEY"] = f"university_spider_{config['UNIVERSITY_NAME']}:requests"
    config["SCHEDULER_DUPEFILTER_KEY"] = f"university_spider_{config['UNIVERSITY_NAME']}:dupefilter"    
    
    

    # Run N concurrent crawlers
    process = CrawlerProcess(settings=config)
    
    print(process.settings.get("LOG_LEVEL"))
    
    crawlers = []

    for i in range(count):
        print(f"Launching crawler #{i+1}")
        crawler = process.crawl(UniversitySpider, crawler_id=i+1, name=config["UNIVERSITY_NAME"], allowed_domains=[config["ALLOWED_DOMAINS"]])
        crawlers.append(crawler)

    process.start()


if __name__ == "__main__":
    main()
