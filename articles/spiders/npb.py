# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector


class NpbSpider(CrawlSpider):
    name = 'npb'
    allowed_domains = ['npb.jp']
    start_urls = ['http://npb.jp/scores/2016/0619/d-f-03/index.html']

    """
    rules = (
        Rule(LinkExtractor(allow=r'/scores/.+/playbyplay\.html'), callback='parse_item', follow=True),
    )
    """
    rules = (
        Rule(LinkExtractor(allow='/scores/2016/0619/d-f-03/playbyplay.html'), callback='parse_item', follow=True),
    )

    def parse_box(self, response):
        self.logger.info("Visited %s", response.url)
        item = response.meta['item']
        item['other_url'] = response.url
        return item

    def get_element_text(self, elements, xpath, index=0):
        body = elements[index].extract()
        return Selector(text=body).xpath(xpath).extract_first()

    def get_board_scores(self, response):
        scores = {}
        score_tables = response.xpath('//*[@id="game_stats"]/div[2]/div/table/thead/tr/*')
        score_tables_1 = response.xpath('//*[@id="game_stats"]/div[2]/div/table/tbody/tr[1]/*')
        score_tables_2 = response.xpath('//*[@id="game_stats"]/div[2]/div/table/tbody/tr[2]/*')
        team1 = self.get_element_text(score_tables_1, '//th/span/text()')
        team2 = self.get_element_text(score_tables_2, '//th/span/text()')
        for index, score in enumerate(score_tables):
            if index == 0:
                continue
            body = score.extract()
            title = Selector(text=body).xpath('//th/text()').extract_first()
            if title:
                point = self.get_element_text(score_tables_1, '//td/text()', index)
                scores["{}回表".format(title)] = {"point": point, "team": team1}
                point = self.get_element_text(score_tables_2, '//td/text()', index)
                scores["{}回裏".format(title)] = {"point": point, "team": team2}
            else:
                title = Selector(text=body).xpath('//td/text()').extract_first()
                if title == "計":
                    pass
                elif title == "H":
                    pass
                elif title == "E":
                    pass
        return scores

    def parse_item(self, response):
        item = {}
        request = scrapy.Request('http://npb.jp/scores/2016/0619/d-f-03/index.html', callback=self.parse_box)
        # TODO: 試合結果クローリング
        scores = self.get_board_scores(response)
        board_scores = []
        score_tables = response.xpath('//div[@id="progress"]/*')
        count = ""
        battings = []
        for score in score_tables:
            body = score.extract()
            line = Selector(text=body).xpath('//td/text()').extract()
            if not line:
                if count and battings:
                    board_scores.append({
                        "count": count, "point": scores[count]["point"],
                        "team": scores[count]["team"], "batting": battings
                    })
                    battings = []
                body = score.extract()
                count = Selector(text=body).xpath('//h5/text()').extract_first()
                continue
            if not count:
                continue
            if line[0][1:5] == "投手交代":
                # TODO: 投手交代考慮
                result_point = line[5].strip().split("（打点")
                if len(result_point) > 1:
                    result = result_point[0]
                    point = result_point[1][0]
                else:
                    result = result_point[0]
                    point = 0
                batting = {
                    "out": line[1].strip(),
                    "base": line[2].strip(),
                    "name": line[3].strip(), # 代打・エルドレッドみたいな表記どうしよう
                    "ball_strike": line[4].strip(),
                    "result": result,
                    "point": point
                }
            else:
                result_point = line[4].strip().split("（打点")
                if len(result_point) > 1:
                    result = result_point[0]
                    point = result_point[1]
                else:
                    result = result_point[0]
                    point = 0
                batting = {
                    "out": line[0].strip(),
                    "base": line[1].strip(),
                    "name": line[2].strip(),
                    "ball_strike": line[3].strip(),
                    "result": result,
                    "point": point
                }
            battings.append(batting)
        else:
            board_scores.append({
                "count": count, "point": scores[count]["point"],
                "team": scores[count]["team"], "batting": battings
            })

        item["play"] = board_scores
        request.meta['item'] = item
        return request
