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
                "tags": quote.xpath("div[@class='tags']/a/text()").extract(),
                "author": quote.xpath("span/small/text()").extract(),
                "quote": quote.xpath("span[@class='text']/text()").get()
            }
        next_page = response.xpath("//li[@class='next']/a/@href").get()
        if next_page:
            # повний шлях ми отримаємо url=self.start_urls[0] + next_page
            yield scrapy.Request(url=self.start_urls[0] + next_page)

    def closed(self, reason):
        # Read the generated JSON file
        with open("quotes.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        # Rewrite the JSON file without Unicode escape sequences
        with open("quotes.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


class AuthorsSpider(scrapy.Spider):
    name = 'authors'
    custom_settings = {"FEED_FORMAT": "json", "FEED_URI": "authors.json"}
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['https://quotes.toscrape.com']

    def parse(self, response):
        
        for author in response.xpath("//div[@class='quote']"):
            
            about_link = author.xpath(".//a/@href").get()
            yield response.follow(about_link, self.parse_author)

        next_page = response.xpath("//li[@class='next']/a/@href").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_author(self, response):

        yield {
            "fullname": response.xpath("//h3[@class='author-title']/text()").get(),
            "born_date": response.xpath("//span[@class='author-born-date']/text()").get(),
            "born_location": response.xpath("//span[@class='author-born-location']/text()").get(),
            "description": response.xpath("//div[@class='author-description']/text()").get()
        }

    def load_dump(self):
        with open("authors.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        with open("authors.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.crawl(AuthorsSpider)
    process.start()
