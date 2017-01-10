# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import csv
import re

# Settings
INPUT_CSV_NAME = 'input.csv'  # Path to input file with csv type
# Delimiter and quotechar are parameters of csv file. You should know it if you created the file
CSV_DELIMITER = '	'
CSV_QUOTECHAR = '|'
OUTPUT_CSV_NAME = 'output.csv'  # Path to output file with csv type
TRANSLATE_WORD_INDEX = 0  # Index of column which should be translated. Others columns will be copied to output file
EXCEPTED_DICTIONARIES = ['Сленг', 'Разговорное выражение', 'табу']  # Dictionaries which shouldn't be in output


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
                request = Request("http://www.multitran.com/m.exe?CL=1&s={}&l1=1&l2=2&SHL=2".format(word), callback=self.translate,
                                  meta={"input_row": input_row})

                requests.append(request)
        return requests

    def translate(self, response):
        input_row = response.meta['input_row'][TRANSLATE_WORD_INDEX]
        # common_row_xpath = '//*/tr/td/table/tr/td/table/tr/td/table/tr/td/table/tr'
        common_row_xpath = '//*/tr'
        translate_xpath = 'td[@class="trans"]/a/text()'
        dict_xpath = 'td[@class="subj"]/a/text()'
        for common_row in response.xpath(common_row_xpath):
            dictionary = common_row.xpath(dict_xpath).extract()
            if len(dictionary) > 0:
                if dictionary[0] in EXCEPTED_DICTIONARIES:
                    continue
                for translate in common_row.xpath(translate_xpath):
                    output_array = response.meta['input_row'].copy()
                    output_array.append(dictionary[0])
                    output_array.append(translate.extract())
                    self.output.append(output_array)
                    # self.logger.error('!!!!!!!!!!!!!!!!!')


    def close(self, reason):
        output_file = open(OUTPUT_CSV_NAME, 'w')
        writer = csv.writer(output_file, delimiter=CSV_DELIMITER, quotechar=CSV_QUOTECHAR, quoting=csv.QUOTE_ALL)
        writer.writerows(self.output)
        output_file.close()
