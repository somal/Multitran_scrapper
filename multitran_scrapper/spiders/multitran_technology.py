# -*- coding: utf-8 -*-
"""
This file is a scratch of technology parser.
"""
import csv

import scrapy
from scrapy import Request

# Settings
# Delimiter and quotechar are parameters of csv file. You should know it if you created the file
CSV_DELIMITER = '	'
CSV_QUOTECHAR = '"'  # '|'
INPUT_NAME = 'input.txt'
OUTPUT_CSV_NAME = 'technology.csv'  # Path to output file with csv type

ONLY_RECOMMENDATED_TRANSLATIONS = True
COLUMNS = ['Input word', 'Translations', 'Dictionary', 'Block number', 'Block name', 'Author', 'Link on author',
           'Comment']


class MultitranSpider(scrapy.Spider):
    name = "multitran_technology"
    allowed_domains = ["multitran.com"]

    def __init__(self):
        self.input_file = open(INPUT_NAME, 'r')
        self.output_file = open(OUTPUT_CSV_NAME, 'w')
        self.output_writer = csv.writer(self.output_file, delimiter=CSV_DELIMITER, quotechar=CSV_QUOTECHAR,
                                        quoting=csv.QUOTE_ALL)

    def start_requests(self):
        requests = []
        for request in self.input_file:
            requests.append(Request(url='http://www.multitran.com/m.exe?CL=1&s={}&l1=1&l2=2&SHL=2'.format(request),
                                    meta={'theme': request}))
        return requests

    def parse(self, response):
        # self.logger.info(response.url)
        theme = response.meta['theme']
        common_row_xpath = '//*/tr/td[@class="phras"]/a'
        for common_row in response.xpath(common_row_xpath):
            link = "http://www.multitran.com{}".format(common_row.xpath('@href').extract_first())
            name = common_row.xpath('text()').extract_first()
            yield scrapy.Request(url=link, callback=self.parse_dictionary, meta={'name': name, 'theme': theme})

    def parse_dictionary(self, response):
        name = response.meta['name']
        theme = response.meta['theme']
        ROW_XPATH = '//*/tr'
        WORD_XPATH = 'td[@class="phraselist1"]/a/text()'
        TRANSLATE_XPATH = 'td[@class="phraselist2"]/a/text()'
        for row in response.xpath(ROW_XPATH):
            row_value = [None] * 4
            row_value[0] = row.xpath(WORD_XPATH).extract_first()
            row_value[1] = row.xpath(TRANSLATE_XPATH).extract_first()
            row_value[2] = name
            row_value[3] = theme
            if row_value[0] is not None:
                self.output_writer.writerow(row_value)

    def close(self, reason):
        self.output_file.close()
