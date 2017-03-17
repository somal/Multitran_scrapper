# -*- coding: utf-8 -*-
import csv

import scrapy
from scrapy import Request

# Settings
# Delimiter and quotechar are parameters of csv file. You should know it if you created the file
CSV_DELIMITER = '	'
CSV_QUOTECHAR = '"'  # '|'
OUTPUT_CSV_FOLDER = 'dictionaries'  # Path to output file with csv type


class MultitranSpider(scrapy.Spider):
    name = "multitran_all_dictionaries"
    host = 'http://www.multitran.com'

    def __init__(self):
        self.output_file = open('dictionaries.csv', 'w')
        self.output_writer = csv.writer(self.output_file, delimiter=CSV_DELIMITER, quotechar=CSV_QUOTECHAR,
                                        quoting=csv.QUOTE_ALL)

    def start_requests(self):
        return [Request("http://www.multitran.com/m.exe?CL=1&s&l1=1&l2=2&SHL=2", callback=self.parser)]

    def parser(self, response):
        self.f = open('tmp.txt', 'w')
        dictionary_xpath = '//*/tr/td[1]/a'
        for dictionary in response.xpath(dictionary_xpath)[1:-1]:
            name = dictionary.xpath('text()').extract()[0]
            link = dictionary.xpath('@href').extract()[0]
            # print("{} {}\n".format(name, link))
            yield Request(url=self.host + link, callback=self.dictionary_parser, meta={'name': name})

    def dictionary_parser(self, response):
        name = response.meta['name']
        ROW_XPATH = '//*/tr'
        for row in response.xpath(ROW_XPATH):
            row_value = [None] * 5
            row_value[0] = [name]
            row_value[1] = row.xpath('td[@class="termsforsubject"][1]/a/text()').extract()
            row_value[2] = row.xpath('td[@class="termsforsubject"][2]/a/text()').extract()
            row_value[3] = row.xpath('td[@class="termsforsubject"][3]/a/i/text()').extract()
            row_value[4] = row.xpath('td[@class="termsforsubject"][3]/a/@href').extract()
            if len(row_value[1]) > 0:
                self.output_writer.writerow([i[0] if len(i) > 0 else " " for i in row_value])
                # break
        next_link = response.xpath('//*/a[contains(text(),">>")]/@href').extract()
        if len(next_link) > 0:
            yield Request(url=self.host + next_link[0], callback=self.dictionary_parser, meta=response.meta)

    def close(self, reason):
        self.output_file.close()
