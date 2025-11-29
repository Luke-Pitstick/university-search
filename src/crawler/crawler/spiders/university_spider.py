from urllib.parse import urlparse
from scrapy_redis.spiders import RedisSpider  # pyright: ignore[reportMissingImports]
from scrapy.exceptions import IgnoreRequest
from scrapy.linkextractors import LinkExtractor
import scrapy

class UniversitySpider(RedisSpider):
    name = "university_crawler"
    redis_key = "university_crawler:start_urls"

    custom_settings = {
        # BFS
        "SCHEDULER_QUEUE_CLASS": "scrapy_redis.queue.FifoQueue",
        # Obey robots.txt
        "ROBOTSTXT_OBEY": True,
    }

    allowed_domains = []  # We'll fill dynamically on first response

    # ---------- URL filetype blacklist ----------
    BAD_EXTENSIONS = (
        ".pdf", ".doc", ".docx", ".ppt", ".pptx",
        ".xls", ".xlsx", ".zip", ".rar", ".gz", ".7z", ".mp4", ".mp3",
        ".avi", ".mov", ".png", ".jpg", ".jpeg", ".gif", ".svg"
    )
    
    link_extractor = LinkExtractor(
        allow_domains=allowed_domains,
        deny_extensions=BAD_EXTENSIONS
    )
    count = 0

    # ---------- Core Parser ----------
    def parse(self, response):
        url = response.url

        # --------- SET DOMAIN RESTRICTION ON FIRST REQUEST ----------
        if not self.allowed_domains:
            parsed = urlparse(url)
            base_domain = parsed.netloc
            if base_domain.startswith("www."):
                base_domain = base_domain[4:]
            self.allowed_domains = [base_domain]
            self.logger.info(f"[DOMAIN LOCK] Crawling restricted to: {base_domain}")

        page_data = {
            'url': response.url,
            'title': response.css('title::text').get(),
            'links': response.css('a::attr(href)').getall(),
            'html': response.text,
        }

        yield page_data

        # ---------- Stop if depth exceeded ----------
        if response.meta.get('depth', 0) >= response.meta.get('max_depth', 10):
            self.logger.info(f"Depth exceeded: {response.url}")
            return
        
        # Extract and follow links
        for link in self.link_extractor.extract_links(response):
            yield scrapy.Request(
                link.url,
                callback=self.parse,
                meta={"depth": response.meta.get("depth", 0) + 1, "max_depth": response.meta.get("max_depth", 10)}
            )
