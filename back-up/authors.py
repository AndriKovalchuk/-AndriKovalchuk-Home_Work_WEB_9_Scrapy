import json

import scrapy
from scrapy.crawler import CrawlerProcess


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    custom_settings = {"FEED_FORMAT": "json", "FEED_URI": "quotes.json"}
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['https://quotes.toscrape.com']

    def parse(self, response):
        for quote in response.xpath("/html//div[@class='quote']"):
            yield {
                "keywords": quote.xpath("div[@class='tags']/a/text()").extract(),
                "author": quote.xpath("span/small/text()").extract(),
                "quote": quote.xpath("span[@class='text']/text()").get()
            }
        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            # повний шлях ми отримаємо url=self.start_urls[0] + next_link
            yield scrapy.Request(url=self.start_urls[0] + next_link)

    def closed(self, reason):
        # Read the generated JSON file
        with open("quotes.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        # Rewrite the JSON file without Unicode escape sequences
        with open("quotes.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # run spider
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.start()
