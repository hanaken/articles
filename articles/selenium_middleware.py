# -*- coding: utf-8 -*-
from scrapy.http import HtmlResponse
from selenium.webdriver import PhantomJS


class SeleniumMiddleware:

    driver = PhantomJS()
    
    def process_request(self, request, spider):
        spider.driver = self.driver
        self.driver.get(request.url)
        return HtmlResponse(
                self.driver.current_url,
                body = self.driver.page_source,
                encoding = 'utf-8',
                request = request)

