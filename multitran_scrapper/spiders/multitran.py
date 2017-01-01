# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import csv

INPUT_CSV_NAME = 'input.csv'
CSV_DELIMITER = '	'
CSV_QUOTECHAR = '|'
OUTPUT_CSV_NAME = 'output.csv'
TRANSLATE_WORD_INDEX = 0


class MultitranSpider(scrapy.Spider):
    name = "multitran"
    allowed_domains = ["multitran.ru"]

    def __init__(self):
        input_file = open(INPUT_CSV_NAME, 'r')
        self.input_reader = csv.reader(input_file, delimiter=CSV_DELIMITER, quotechar=CSV_QUOTECHAR,
                                       quoting=csv.QUOTE_ALL)
        self.output = []

    def start_requests(self):
        requests = []
        for input_row in self.input_reader:
            if len(input_row) > 0:
                word = input_row[TRANSLATE_WORD_INDEX]
                request = Request("http://www.multitran.ru/c/m.exe?s={}".format(word), callback=self.translate,
                                  meta={"input_row": input_row})

                requests.append(request)
        return requests

    def translate(self, response):
        input_row = response.meta['input_row'][TRANSLATE_WORD_INDEX]
        common_row_xpath = '//*/tr/td/table/tr/td/table/tr/td/table/tr/td/table/tr'
        translate_xpath = 'td[2]/a/text()'
        dict_xpath = 'td[1]/a/i/text()'
        for common_row in response.xpath(common_row_xpath):
            dictionary = common_row.xpath(dict_xpath).extract()
            if len(dictionary) > 0:
                for translate in common_row.xpath(translate_xpath):
                    output_array = response.meta['input_row'].copy()
                    output_array.append(dictionary[0])
                    output_array.append(translate.extract())
                    self.output.append(output_array)

    def close(self, reason):
        output_file = open(OUTPUT_CSV_NAME, 'w')
        writer = csv.writer(output_file, delimiter=CSV_DELIMITER, quotechar=CSV_QUOTECHAR, quoting=csv.QUOTE_ALL)
        writer.writerows(self.output)
        output_file.close()
