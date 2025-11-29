import json
from pathlib import Path
from typing import Dict, Any
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import scrapy
from .university_crawler import UniversitySpider

class CrawlerCreator:
    def __init__(self, config_path: str = 'config.json', *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.config = self._load_config(config_path)
        self.settings = self._build_scrapy_settings()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load and validate configuration from JSON file."""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        try:
            with config_file.open('r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in config file: {e.msg}", e.doc, e.pos
            )
        
        # Validate required keys
        required_keys = ['base_url', 'settings']
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise KeyError(f"Missing required config keys: {missing_keys}")
        
        return config
    
    def _build_scrapy_settings(self) -> scrapy.settings.Settings:
        """Build Scrapy settings from configuration."""
        settings = get_project_settings()
        
        # Extract settings with defaults
        config_settings = self.config.get('settings', {})
        
        # Determine which duplicate filter to use
        dupefilter_class = config_settings.get('DUPEFILTER_CLASS', 'redis')
        dupefilter_mapping = {
            'redis': 'src.filters.dupefilter.RedisBasedDupeFilter',
        }
        
        # Determine crawl order: BFS (breadth-first) or DFS (depth-first, default)
        use_bfs = True
        
        settings.setdict()
        
        # Set item count limit if pagecount is specified
        if self.kwargs.get('pagecount', None):
            settings.set('CLOSESPIDER_ITEMCOUNT', self.kwargs.get('pagecount'))
            print(f"\n🔧 Setting CLOSESPIDER_ITEMCOUNT to {self.kwargs.get('pagecount')}")
            print(f"🚫 HTTP cache disabled to ensure fresh crawling")
        
        return settings
    
    def start(self):
        """Start the crawler process."""
        process = CrawlerProcess(self.settings)
        process.crawl(
            UniversitySpider,
            base_url=self.config['base_url'],
            crawl_rules=self.config.get('crawl_rules')
        )
        process.start()
        