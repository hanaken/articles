# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pickle


class ArticlesPipeline:
    def process_item(self, item, spider):
        if spider.name != "nikkan":
            return item
        file_name = item["url"].split("/")[-1].split(".")[0]
        print(file_name)
        with open('./data/{}.pickle'.format(file_name), 'wb') as f:
            pickle.dump(item, f)
        return item
