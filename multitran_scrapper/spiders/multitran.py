# -*- coding: utf-8 -*-
"""
It's the main parser of Multitran translation system.
It has input csv file which contains words for translation as one column.

*** Please, see Description.docx. It contains detailed description,
    but it includes information of one-to-many translations (one word has several translations).
    The last version of parser select only recommended translation and save only it to DB
***

For every word from input file, the parser creates several columns of information and saves to output csv file:
  input_word | translation | dictionary of translation (из какого словаря взят перевод) | block_number | author_name | link on author | author's comment
Some comments of data:
 - any word has several translations from different blocks
 - if you want to have only recommended translations, you should set ONLY_RECOMMENDATED_TRANSLATIONS = True, otherwise False


 - output
 - block
 - link_of_author
 - recomendation system


"""
import csv
import re

import scrapy
from scrapy import Request

# Settings
INPUT_CSV_NAME = 'tables/input.csv'  # Path to input file with csv type
# Delimiter and quotechar are parameters of csv file. You should know it if you created the file
CSV_DELIMITER = '	'
CSV_QUOTECHAR = '"'  # '|'
OUTPUT_CSV_NAME = 'tables/output1.csv'  # Path to output file with csv type
TRANSLATE_WORD_INDEX = 0  # Index of column which should be translated. Others columns will be copied to output file
EXCEPTED_DICTIONARIES = ['разг.']  # Dictionaries which shouldn't be in output

ONLY_RECOMMENDATED_TRANSLATIONS = True
COLUMNS = ['Input word', 'Translations', 'Dictionary', 'Block number', 'Block name', 'Author', 'Link on author',
           'Comment']


class MultitranSpider(scrapy.Spider):
    name = "multitran"
    allowed_domains = ["multitran.ru"]

    def __init__(self):
        self.input_file = open(INPUT_CSV_NAME, 'r')
        self.input_reader = csv.reader(self.input_file, delimiter=CSV_DELIMITER, quotechar=CSV_QUOTECHAR,
                                       quoting=csv.QUOTE_ALL)

        self.output_file = open(OUTPUT_CSV_NAME, 'w')
        self.output_writer = csv.writer(self.output_file, delimiter=CSV_DELIMITER, quotechar=CSV_QUOTECHAR,
                                        quoting=csv.QUOTE_ALL)

    def start_requests(self):
        requests = []
        i = 0
        for input_row in self.input_reader:
            if len(input_row) > 0:
                word = input_row[TRANSLATE_WORD_INDEX]
                request = Request("http://www.multitran.com/m.exe?CL=1&s={}&l1=1&l2=2&SHL=2".format(word),
                                  callback=self.parse,
                                  meta={"input_row": input_row, 'index': i})

                requests.append(request)
                i += 1
        return requests

    def write_translations(self, translations, output):
        def recommend_translation(translations):
            def calc_value(translate, unigrams):
                words = translate.split()
                return sum([unigrams[w] for w in words]) / len(words)

            unigrams = {}
            for translate in translations:
                for words in translate.split():
                    if unigrams.get(words, None) is None:
                        unigrams[words] = 1
                    else:
                        unigrams[words] += 1

            maxvalue = 0
            result = []
            for i, translate in enumerate(translations):
                value = calc_value(translate, unigrams)
                if value > maxvalue:
                    maxvalue = value
                    result = [i]

            return result

        # Add recommended flag to every translates
        recommended_translation_indexes = recommend_translation(translations)
        if ONLY_RECOMMENDATED_TRANSLATIONS:
            output = [output[i] for i in recommended_translation_indexes]
        else:
            for i, o in enumerate(output):
                o.append('X' if i in recommended_translation_indexes else 'O')

        # Write ready-to-use data to csv file
        self.output_writer.writerows(output)

    def parse(self, response):

        def get_selector_tag(selector):
            return selector.xpath('name()').extract_first()

        def get_all_leaf_nodes(selector):
            all_leaf_xpath = 'descendant-or-self::node()'
            return selector.xpath(all_leaf_xpath)

        common_row_xpath = '//*/tr[child::td[@class="gray" or @class="trans"]]'
        translate_xpath = 'td[@class="trans"]'
        dict_xpath = 'td[@class="subj"]/a/text()'
        nx_gramms_сommon_xpath = "//*/div[@class='middle_col'][3]"
        nx_gramms_status_xpath = "p[child::a]/text()"
        nx_gramms_words_xpath = "a[string-length(@title)>0]/text()"
        block_number = 0
        translates = []
        output = []
        for common_row in response.xpath(common_row_xpath):
            dictionary = common_row.xpath(dict_xpath).extract()
            if len(dictionary) > 0:
                if not dictionary[0] in EXCEPTED_DICTIONARIES:
                    # NX grams detection
                    nx_gramms_common = response.xpath(nx_gramms_сommon_xpath)
                    nx_gramms_status = nx_gramms_common.xpath(nx_gramms_status_xpath).extract()
                    nx_gramms = 'цельное слово' if len(nx_gramms_status) == 0 else nx_gramms_status[
                                                                                       0] + " : " + "|".join(
                        nx_gramms_common.xpath(nx_gramms_words_xpath).extract())

                    translation_parts = []
                    all_leaf_nodes = get_all_leaf_nodes(common_row.xpath(translate_xpath))
                    comment = ''
                    for node in all_leaf_nodes:
                        flag_full_translation = False
                        node_tag = get_selector_tag(node)
                        if node_tag is None:
                            node_value = node.extract()
                            if node_value.strip() == ";":
                                flag_full_translation = True
                            if node == all_leaf_nodes[-1]:
                                translation_parts.append(node_value)
                                flag_full_translation = True
                            if flag_full_translation:
                                translation_value = "".join(translation_parts)

                                try_find_comment = re.findall('(?P<translate_value>.*)\((?P<comment>.*)\)',
                                                              translation_value)
                                if len(try_find_comment) > 0:
                                    translation_value, comment = try_find_comment[0]
                                else:
                                    comment = ''

                                output_array = response.meta['input_row'].copy()
                                output_array.append(translation_value)
                                output_array.append(dictionary[0])
                                output_array.append(str(block_number))
                                output_array.append(block_name)
                                # output_array.append(nx_gramms)

                                output_array.append(author)
                                output_array.append(author_href)
                                output_array.append(comment)
                                output_array = [x.strip() for x in output_array]
                                output.append(output_array)

                                translates.append(translation_value)
                                translation_parts = []
                            else:
                                translation_parts.append(node_value)
                        elif node_tag == "a":
                            author_href = node.xpath('@href').extract_first()
                            author = re.findall('/m\.exe\?a=[0-9]*&[amp;]?UserName=(?P<author_name>.*)', author_href)
                            if len(author) > 0:
                                author = author[0]
                            else:
                                author_href = ''
                                author = ''
            else:
                self.write_translations(translates, output)
                translates = []
                output = []
                block_name = "".join(common_row.xpath('td[@class="gray"]/descendant-or-self::text()').extract())
                block_name = block_name[:block_name.find("|")]
                block_number += 1

        self.write_translations(translates, output)

    def close(self, reason):
        self.input_file.close()
        self.output_file.close()
