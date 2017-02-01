# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import signals
from scrapy import Spider


class NikkanSpider(CrawlSpider):
    name = 'nikkan'
    allowed_domains = ['www.nikkansports.com']
    #base_url = "http://www.nikkansports.com/search/top-search.html?q=%E6%88%A6%E8%A9%95&start={}&sort=desc&ch=%E9%87%8E%E7%90%83"
    base_url = "http://www.nikkansports.com/search/top-search.html?q=戦評&start={}&sort=desc&ch=野球"
    start_urls = []

    rules = (
        Rule(LinkExtractor(allow=r'baseball/news/[0-9]+\.html'), callback='parse_item', follow=True),
    )

    driver = None
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "articles.selenium_middleware.SeleniumMiddleware": 500,
        },
    }

    def __init__(self, *args, **kargs):
        super(NikkanSpider, self).__init__(*args, **kargs)
        for i in range(1,3):
            url = self.base_url.format(i*10)
            self.start_urls.append(url)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(NikkanSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse_item(self, response):
        item = {}
        item['url'] = response.url
        item['title'] = response.xpath('//*[@id="articleArea"]/header/h1/text()').extract()[0]
        item['body'] = ''
        for line in response.xpath('//*[@id="news"]/p/text()').extract():
            item['body'] += line + '\n'
        item['date'] = response.xpath('//*[@id="articleArea"]/header/time/text()').extract()[0]
        return item

    def spider_closed(self, spider):
        spider.logger.info('Spider closed: %s', spider.name)
        if spider.driver:
            spider.driver.close()

