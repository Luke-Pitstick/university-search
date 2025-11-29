# Entry point for starting the crawlers
import fire


def start_crawlers(config_path: str = 'config.json'):
    """Start the crawlers."""
    crawler_creator = CrawlerCreator(config_path)
    crawler_creator.start_crawlers()

if __name__ == '__main__':
    fire.Fire(start_crawlers)