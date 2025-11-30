from urllib.parse import urlparse, urljoin
from scrapy_redis.spiders import RedisSpider  # pyright: ignore[reportMissingImports]
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.url import canonicalize_url
import scrapy
from scrapy.settings import Settings

class UniversitySpider(RedisSpider):
    name = f"university_spider"
    redis_key = "university_spider:start_urls"

    custom_settings = {
        # BFS
        "SCHEDULER_QUEUE_CLASS": "scrapy_redis.queue.FifoQueue",
        # Obey robots.txt
        "ROBOTSTXT_OBEY": True,
    }

    # ---------- URL filetype blacklist ----------
    BAD_EXTENSIONS = (
        ".pdf", ".doc", ".docx", ".ppt", ".pptx",
        ".xls", ".xlsx", ".zip", ".rar", ".gz", ".7z", ".mp4", ".mp3",
        ".avi", ".mov", ".png", ".jpg", ".jpeg", ".gif", ".svg"
    )
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # Access the settings via the crawler object
        settings = crawler.settings
        
        # Instantiate the spider with all arguments
        obj = cls(settings, *args, **kwargs)
        # Required to set the crawler object on the spider instance
        obj.crawler = crawler
        # Call setup_redis explicitly to ensure mixin initialization
        obj.setup_redis(crawler)
        return obj
    
    def __init__(self, settings=None, *args, **kwargs):
        # Allow settings to be optional or passed via kwargs if needed
        crawler_id = kwargs.pop('crawler_id', None)
        university_name = kwargs.pop('name', None)
        
        # Pass remaining args to RedisSpider/Spider __init__
        super(UniversitySpider, self).__init__(*args, **kwargs)
        
        # If settings were passed explicitly, use them; otherwise fall back to self.settings (set by from_crawler later or manually)
        if settings:
            self.settings = settings
            allowed = settings.get('ALLOWED_DOMAINS')
            self.allowed_domains = [allowed]
            
        
        if crawler_id and university_name:
            self.name = f"{self.name}_{university_name}_{crawler_id}"
            self.redis_key = f"{self.name}:start_urls"
            
        # Logging only if settings are available
        if self.settings:
            self.logger.info(f"Initialized Spider: {self.name}")
            self.logger.info(f"Redis Key: {self.redis_key}")
            self.logger.info(f"DupeFilter Key: {self.settings.get('SCHEDULER_DUPEFILTER_KEY')}")
            self.logger.info(f"Allowed Domains: {self.allowed_domains}")

        # Initialize LinkExtractor with the specific allowed_domains for this instance
        self.link_extractor = LinkExtractor(
            allow_domains=self.allowed_domains,
            deny_extensions=self.BAD_EXTENSIONS
        )

    def make_requests_from_url(self, url):
        # Using default behavior (dont_filter=False) to ensure duplicates are checked
        return scrapy.Request(url, dont_filter=False)

    # ---------- Core Parser ----------
    def parse(self, response):
        url = response.url
        self.logger.info(f"[Parse] Parsing URL: {url}")

        # --------- SET DOMAIN RESTRICTION ON FIRST REQUEST ----------
        # (This acts as a fallback if allowed_domains wasn't passed correctly, 
        # but also handles the case where we want to restrict based on the start URL's redirect)
        if not self.allowed_domains:
            parsed = urlparse(url)
            base_domain = parsed.netloc
            if base_domain.startswith("www."):
                base_domain = base_domain[4:]
            self.allowed_domains = [base_domain]
            self.logger.info(f"[DOMAIN LOCK] Crawling restricted to: {base_domain}")
            
            # Re-initialize link extractor if we just learned the domain
            self.link_extractor = LinkExtractor(
                allow_domains=self.allowed_domains,
                deny_extensions=self.BAD_EXTENSIONS
            )
            
        
        try:
            page_data = {
                'url': response.url,
                'title': response.css('title::text').get(),
                'links': response.css('a::attr(href)').getall(),
                'html': response.text,
            }
        except Exception as e:
            self.logger.error(f"[Parse] Error parsing page: {e}")
            return
        
        yield page_data

        # ---------- Stop if depth exceeded ----------
        if response.meta.get('depth', 0) >= response.meta.get('max_depth', 10):
            self.logger.info(f"Depth exceeded: {response.url}")
            return
        
        # Extract and follow links
        links = self.link_extractor.extract_links(response)
        self.logger.info(f"[Parse] Found {len(links)} links on {url}")
        
        for link in links:
            # Normalize URLs for comparison to catch all self-referential variants
            # (e.g., with/without trailing slash, query params, etc.)
            canonical_current = canonicalize_url(url)
            canonical_link = canonicalize_url(link.url)
            
            if canonical_link == canonical_current:
                self.logger.debug(f"[Parse] Skipping self-referential link: {link.url}")
                continue
                 
            yield scrapy.Request(
                link.url,
                callback=self.parse,
                meta={"depth": response.meta.get("depth", 0) + 1, "max_depth": response.meta.get("max_depth", 10)}
            )
