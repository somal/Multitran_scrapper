# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


# from scrapy.selector import Selector


class MultitranSpider(scrapy.Spider):
	name = "multitran"
	allowed_domains = ["multitran.ru"]
	start_urls = ['http://multitran.ru/']

	def __init__(self):
		self.input = open('input_data.txt', 'r')
		self.output = []

	def parse(self, response):
		for input_word in self.input.readlines():
			request = Request("http://www.multitran.ru/c/m.exe?s={}".format(input_word), callback=self.translate)
			request.meta['input_word'] = input_word.strip()
			yield request

	def translate(self, response):
		input_word = response.meta['input_word']
		xpath = '//*/tr/td/table/tr/td/table/tr/td/table/tr/td/table/tr/td[2]/a/text()'
		for word in response.xpath(xpath):
			self.output.append((input_word, word.extract()))
		# self.logger.error("Bla")

	def close(self, reason):
		output_file = open('output_data.txt', 'w')
		for w, t in self.output:
			# output_file.write()
			print("{} {}".format(w, t), file=output_file)
		output_file.close()
