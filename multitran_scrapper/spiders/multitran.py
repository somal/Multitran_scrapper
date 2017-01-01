# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import csv

INPUT_CSV_NAME = 'input.csv'
CSV_DELIMITER = '	'
CSV_QUOTECHAR = '|'
OUTPUT_CSV_NAME = 'output.csv'


class MultitranSpider(scrapy.Spider):
    name = "multitran"
    allowed_domains = ["multitran.ru"]

    def __init__(self):
        input = open(INPUT_CSV_NAME, 'r')
        self.input_reader = csv.reader(input, delimiter=CSV_DELIMITER, quotechar=CSV_QUOTECHAR,
                                       quoting=csv.QUOTE_ALL)
        self.output = []

    def start_requests(self):
        requests = []
        for input_word in self.input_reader:
            if len(input_word) > 0:
                request = Request("http://www.multitran.ru/c/m.exe?s={}".format(input_word[0]), callback=self.translate,
                                  meta={"input_word": input_word[0]})

                requests.append(request)
        return requests

    def translate(self, response):
        input_word = response.meta['input_word']
        row_path = '//*/tr/td/table/tr/td/table/tr/td/table/tr/td/table/tr'
        translate_xpath = 'td[2]/a/text()'
        dict_xpath = 'td[1]/a/i/text()'
        for row in response.xpath(row_path):
            dictionary = row.xpath(dict_xpath).extract()
            if len(dictionary) > 0:
                for translate in row.xpath(translate_xpath):
                    self.output.append([input_word, dictionary[0], translate.extract()])

    def close(self, reason):
        output_file = open(OUTPUT_CSV_NAME, 'w')
        writer = csv.writer(output_file, delimiter=CSV_DELIMITER, quotechar=CSV_QUOTECHAR, quoting=csv.QUOTE_ALL)
        writer.writerows(self.output)
        output_file.close()
