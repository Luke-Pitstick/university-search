from trafilatura import extract

class DataCleaningPipeline:
    def process_item(self, item, spider):
        # Extracts text from HTML using trafilatura
        extracted_text = extract(item['html'])
        item['text'] = extracted_text
        spider.logger.info(f"DataCleaningPipeline: Text extracted for {item['url']}")
        return item